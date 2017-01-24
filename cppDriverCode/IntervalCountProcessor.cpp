#include "stdafx.h"
#include "IntervalCountProcessor.h"
#include "kmkTime.h"
#include <assert.h>
#include "IDevice.h"
#include <cstring>
#include <algorithm>

#define MAX_QUEUE_ENTRIES 30000

// Id of the interval counts report
#define DATA_IN_REPORT 4
#define REPORT_SIZE 63

// Timeout in ms for configuration querys
#define CONFIGURATION_QUERY_TIMEOUT 2000

#define ComponentDetector 0
#define ComponentConfiguration 1

namespace kmk
{

IntervalCountProcessor::IntervalCountProcessor(IDataInterface *pDataInterface)
: _pDataInterface(pDataInterface)
, _countEventCallback(NULL)
, _countEventCallbackArg(NULL)
, _finishedCallback(NULL)
, _finishedCallbackArg(NULL)
, _errorCallback(NULL)
, _errorCallbackArg(NULL)
, _waitEvent(true, false, L"")
, _detectorStatus(TS_STOP)
, _requiredThreadStatus(TS_STOP)
, _inputPacketBufferDataSize(0)
, _dataQueue(REPORT_SIZE, MAX_QUEUE_ENTRIES)
, _startAcquisitionTime(0)
, _endAcquisitionTime(0)

, _configurationQueryState(CQS_IDLE)
, _configurationQueryEvent(false, false, L"")
{
	_pDataInterface->SetDataReadyCallback(ReadDataCallbackProc, this);
	_pDataInterface->SetErrorCallback(DataInterfaceErrorCallbackProc, this);
	_inputPacketBuffer.resize(REPORT_SIZE); // Max packet size is the data report 
}

IntervalCountProcessor::~IntervalCountProcessor()
{
	_pDataInterface->SetDataReadyCallback(NULL, NULL);
	_pDataInterface->SetErrorCallback(NULL, NULL);
}

int IntervalCountProcessor::DeterminePacketSize(BYTE reportId)
{
	switch(reportId)
	{
	case DATA_IN_REPORT:
		return REPORT_SIZE;

	case CONFIGURATION_GETLLD_CHANNEL:
	case CONFIGURATION_GETPULSEWIDTH:
	//case CONFIGURATION_GETBIAS2:
	case CONFIGURATION_GETVERSION:
		return 3;
		
	case CONFIGURATION_GETGAIN:
	case CONFIGURATION_GETDIFFGAIN:
	//case CONFIGURATION_GETPOLARITY:
	case CONFIGURATION_GETBIAS:
	//case CONFIGURATION_GETHIGHVOLTAGE: 
		return 2;

	case CONFIGURATION_GETSETTINGS:
		return 5;
	
	case CONFIGURATION_GETSERIAL:
		return DEVICE_SERIAL_LENGTH + 1; // + 1 for header
	default:
		return 0;
	}
}

// NOTE: This call is coming from the read thread of the DataInterface, make sure its fast!
void IntervalCountProcessor::QueueData(int64_t timeStamp, BYTE *pData, size_t dataLength)
{
	kmk::Lock lock(_criticalSection);

    size_t totalDataLength = _inputPacketBufferDataSize + dataLength;
	bool newPacketReceived = false;
	int readIndex = 0;
	BYTE tempPacket[REPORT_SIZE];

	while (1)
	{
        int packetSize = 0;

		// We need at least 2 bytes for the packet length
		if (totalDataLength - readIndex >= 2)
		{
			// Reports dont contain the size, determine the size from the reportId (first byte)
			BYTE reportId = ((size_t)readIndex < _inputPacketBufferDataSize) ? _inputPacketBuffer[readIndex] : pData[readIndex - _inputPacketBufferDataSize];
			packetSize = DeterminePacketSize(reportId);
		}

		// Is there enough data between the two buffers to construct this packet?
        if (packetSize != 0 && packetSize <= (int)totalDataLength - readIndex)
		{
            int sizeFromBuffer = std::max(0, std::min(packetSize, (int)_inputPacketBufferDataSize - readIndex));
			int sizeFromNewData = packetSize - sizeFromBuffer;
			BYTE *pQueueData = NULL;
			if (sizeFromBuffer == packetSize)
			{
				pQueueData = &_inputPacketBuffer[readIndex];
			}
			else if (sizeFromNewData == packetSize)
			{
				pQueueData = &pData[readIndex + sizeFromBuffer - _inputPacketBufferDataSize];
			}
			else
			{
				// Copy the data split between the two buffers into the temp buffer and queue the whole packet
				if (sizeFromBuffer != 0)
                    memcpy(tempPacket, &_inputPacketBuffer[readIndex], sizeFromBuffer);
				if (sizeFromNewData != 0)
                    memcpy(&tempPacket[sizeFromBuffer], &pData[readIndex + sizeFromBuffer - _inputPacketBufferDataSize], sizeFromNewData);

				pQueueData = tempPacket;
			}

			_dataQueue.Enqueue(timeStamp, pQueueData, packetSize);
			newPacketReceived = true;
			readIndex += packetSize;
		}
		else
		{
			// Not enough data. Move/Copy the remaining data to the start of the _inputPacketBuffer
            size_t sizeFromBuffer = std::max(0, (int)_inputPacketBufferDataSize - readIndex);
            size_t sizeFromNewData = dataLength - (readIndex + sizeFromBuffer - _inputPacketBufferDataSize);

			if (readIndex != 0 && sizeFromBuffer != 0)
				memcpy(&_inputPacketBuffer[0], &_inputPacketBuffer[readIndex], sizeFromBuffer);
			if (sizeFromNewData != 0)
				memcpy(&_inputPacketBuffer[sizeFromBuffer], &pData[readIndex + sizeFromBuffer - _inputPacketBufferDataSize], sizeFromNewData);

			_inputPacketBufferDataSize = sizeFromBuffer + sizeFromNewData;
			break;
		}
		
	}
	
	if (newPacketReceived)
		_waitEvent.Signal();
}

void IntervalCountProcessor::Reset()
{
	kmk::Lock lock(_criticalSection);

	// Clear all acquired data
	_dataQueue.Clear();
	_inputPacketBufferDataSize = 0;
}

bool IntervalCountProcessor::StartProcessing(unsigned char componentId)
{
	kmk::Lock lock(_criticalSection);
	

	switch (componentId)
	{
	case ComponentConfiguration:
		break;

	case ComponentDetector:
		_detectorStatus = TS_RUNNING;
		_startAcquisitionTime = kmk::Time::GetTimeMs();
		break;

	default:
		return false;
	}

	bool isAlreadyRunning = _requiredThreadStatus != TS_STOP;
	_requiredThreadStatus = TS_RUNNING;

	// If the processing thread is not already running then start it
	if (!isAlreadyRunning)
	{
		Reset();

		if (_pDataInterface != NULL)
		{
			if (!_pDataInterface->BeginReading())
				return false;
		}

		if (!_thread.Start(ProcessThreadProc, this))
		{
			_requiredThreadStatus = TS_STOP;
			return false;
		}
	}

	return true;
}

bool IntervalCountProcessor::StopProcessing(unsigned char componentId, bool force)
{
	bool stopProcessing = false;

	{
		kmk::Lock lock(_criticalSection);

		switch (componentId)
		{
		case ComponentConfiguration:
			break;

		case ComponentDetector:
			_detectorStatus = force ? TS_STOP : TS_FINISH;
			_endAcquisitionTime = kmk::Time::GetTimeMs();
			break;

		default:
			return false;
		}

		stopProcessing = _requiredThreadStatus != TS_STOP && 
						 _detectorStatus != TS_RUNNING && 
						 _configurationQueryState != CQS_WAITING;
	}
	
	if (stopProcessing)
	{
		if (_pDataInterface != NULL)
		{
			_pDataInterface->StopReading();
		}

		{
			kmk::Lock lock(_criticalSection);
			_requiredThreadStatus = force ? TS_STOP : TS_FINISH;
		}

		_waitEvent.Signal(); // Interrupt any wait on the thread

		// If we are not allowing the queue to be completed then wait for the thread to exit before continuing
		if (force)
            _thread.WaitForTermination();
	}

	if (force && componentId == ComponentDetector)
	{
		// Raise the finished callback
		kmk::Lock lock(_criticalSection);
		if (_finishedCallback != NULL)
		{
			(*_finishedCallback)(_finishedCallbackArg, true);
		}
	}

	return true;
}

void IntervalCountProcessor::AddComponent(uint8_t /*componentId*/, IDevice * /*pDevice*/, CountEventCallbackFunc pCountEventFunc,
			void *pCountEventArg, FinishedProcessingCallbackFunc pFinishedFunc, void *pFinishedArg,
			ErrorCallbackFunc pErrorFunc, void *pErrorArg)
{
	kmk::Lock lock(_criticalSection);
	_countEventCallback = pCountEventFunc;
	_countEventCallbackArg = pCountEventArg;

	_finishedCallback = pFinishedFunc;
	_finishedCallbackArg = pFinishedArg;

	_errorCallback = pErrorFunc;
	_errorCallbackArg = pErrorArg;
}

void IntervalCountProcessor::RemoveComponent(uint8_t /*componentId*/, IDevice * /*pDevice*/)
{
	kmk::Lock lock(_criticalSection);
	_countEventCallback = NULL;
	_countEventCallbackArg = NULL;

	_finishedCallback = NULL;
	_finishedCallbackArg = NULL;
}

int64_t IntervalCountProcessor::GetRealTime(uint8_t /*componentId*/)
{	
	kmk::Lock lock(_criticalSection);

	// Determine if we are currently acquiring data. If so calculate the real time based on currentTime - startTime 
	// else return the time of the previously completed acquisition
	if (_detectorStatus == TS_RUNNING)
	{
		return kmk::Time::GetTimeMs() - _startAcquisitionTime;
	}
	else
	{
		return _endAcquisitionTime - _startAcquisitionTime;
	}
}

void IntervalCountProcessor::ResetRealTime(uint8_t /*componentId*/)
{
    kmk::Lock lock(_criticalSection);
    _startAcquisitionTime = kmk::Time::GetTimeMs();
    _endAcquisitionTime = _startAcquisitionTime;
}

void IntervalCountProcessor::ProcessReport(int64_t timestamp, BYTE *pData, size_t dataSize)
{
	// First byte is the report id
	uint8_t reportId = pData[0];

	switch(reportId)
	{
	case DATA_IN_REPORT:
		ProcessDataReport(timestamp, pData, dataSize);
		break;

		// Get configuration report
	case CONFIGURATION_GETLLD_CHANNEL:
	case CONFIGURATION_GETPULSEWIDTH:
	//case CONFIGURATION_GETBIAS2:		
	case CONFIGURATION_GETGAIN:
	case CONFIGURATION_GETDIFFGAIN:
	//case CONFIGURATION_GETPOLARITY:
	case CONFIGURATION_GETBIAS:
	//case CONFIGURATION_GETHIGHVOLTAGE: 
	case CONFIGURATION_GETSETTINGS:
	case CONFIGURATION_GETSERIAL:
	case CONFIGURATION_GETVERSION:
		ProcessConfigurationReport(pData, dataSize);
		break;
	}
}

// Process a report (called on the process thread)
void IntervalCountProcessor::ProcessDataReport(int64_t timestamp, BYTE *pData, size_t dataSize)
{
	{
		kmk::Lock lock(_criticalSection);
		if (_detectorStatus == TS_STOP || _countEventCallback == NULL)
			return; // No callback means no point processing data!
	}

	// Reports should always be the same size
	if (dataSize != REPORT_SIZE)
		return;

	// Read following bytes in pairs and determine if any channel data is included
	// First byte is report id
	for (int offset = 1; offset < REPORT_SIZE; offset += 2)
	{
		// Check the least sig bit of the 2 byte data. If its a 1 it has a valid value
		if ((pData[offset + 1] & 0x1) == 1)
		{
			// Valid channel. Actual channel number is 12 bit (remove first 4 bits from the least sig byte)
			unsigned int val = ((pData[offset] << 4) & 0xFF0) + ((pData[offset+1] >> 4) & 0xF);

			// Raise callback for each event
			(*_countEventCallback)(_countEventCallbackArg, timestamp, val, 1);
		}
		else 
		{
			break; // No more data in this report
		}
	}
}

void IntervalCountProcessor::ProcessConfigurationReport(BYTE *pData, size_t dataSize)
{
	// A configuration report response has been received. If we are still waiting
	// for the response then store the data and notify the original calling thread
	kmk::Lock lock(_criticalSection);
	if (_configurationQueryState != CQS_WAITING)
	{
		// We are not waiting for a response (probably timed out). Just ignore this report
		return;
	}

	// Copy the full packet into the result buffer
	if (_configurationQueryResultData.size() < dataSize)
		_configurationQueryResultData.resize(dataSize);

    memcpy(&_configurationQueryResultData[0], pData, dataSize);
	_configurationQueryState = CQS_SUCCESS;
	
	// Signal the waiting thread that data is ready
	_configurationQueryEvent.Signal();
}

bool IntervalCountProcessor::GetConfigurationData(uint8_t /*componentId*/, uint8_t configurationId, BYTE *pDataOut, size_t &dataLength)
{
    size_t requestLength = dataLength + 1;
	// Time for a little fix - Report 0x87 is shared between PULSEWIDTH (LCS - 1 byte) and BIAS 2 (SIGMA / TN15 - 2 bytes).
	// Because the report id is used to determine the data packet size we need to pass this on with the same size. Pad the PULSEWIDTH with 1
	// extra byte
	if (configurationId == CONFIGURATION_GETPULSEWIDTH && dataLength == 1)
	{
		++requestLength;
	}

	// Create a request report
	std::vector<BYTE> requestReport;
	requestReport.resize(requestLength);
	requestReport[0] = configurationId;

	{
		kmk::Lock lock(_criticalSection);

		// Getting a configuration requires writing a report to the device and waiting for a response
		if (_configurationQueryState != CQS_IDLE)
			return false;

		_configurationQueryEvent.Reset();
		_configurationQueryState = CQS_WAITING;
	}
	
	StartProcessing(ComponentConfiguration);

	// Send the request
	if (!_pDataInterface->GetConfigurationSetting((unsigned char*)&requestReport[0], requestReport.size()))
	{
		{
			kmk::Lock lock(_criticalSection);
			_configurationQueryState = CQS_IDLE;
		}

		// No longer waiting for configuration response, close the connection if its not being used
		StopProcessing(ComponentConfiguration, true);
		return false;
	}

	// Wait for a response
	bool result = _configurationQueryEvent.Wait(CONFIGURATION_QUERY_TIMEOUT);
	{
		{
			kmk::Lock lock(_criticalSection);
			result &= _configurationQueryState == CQS_SUCCESS;
			_configurationQueryState = CQS_IDLE;
		}

		// No longer waiting for configuration response, close the connection if its not being used
		StopProcessing(ComponentConfiguration, true);
		
		if (result)
		{
			kmk::Lock lock(_criticalSection);

			// Grab the data out of the packet and copy into the output buffer
            memcpy(pDataOut, &_configurationQueryResultData[1], dataLength);
		}
		else
			dataLength = 0;
	}
	return result;
}

bool IntervalCountProcessor::SetConfigurationData(uint8_t /*componentId*/, uint8_t configurationId, BYTE *pDataIn, size_t dataLength)
{
	// Create a report
	std::vector<BYTE> requestReport;
	requestReport.resize(dataLength + 1);
	requestReport[0] = configurationId;
    memcpy(&requestReport[1], pDataIn, dataLength);

	return _pDataInterface->SetConfigurationSetting(&requestReport[0], requestReport.size());
}

int IntervalCountProcessor::ProcessThreadProc(void *pArg)
{
	IntervalCountProcessor *pThis = (IntervalCountProcessor*)pArg;
	unsigned char *pBuffer = new unsigned char [REPORT_SIZE];
	int64_t timestamp;

	ThreadStatus keepRunning = TS_RUNNING;
	do
	{
		// If something is in the queue then process it, otherwise wait for data		
		if (!pThis->_dataQueue.IsEmpty())
		{
			// Process
			pThis->_dataQueue.Dequeue(pBuffer, REPORT_SIZE, timestamp);
			pThis->ProcessReport(timestamp, pBuffer, REPORT_SIZE);
		}
		else
		{
			// No more data, check if we have been asked to finish once all data is processed
			{
				kmk::Lock lock(pThis->_criticalSection);
				if (pThis->_requiredThreadStatus == TS_FINISH ||
					pThis->_requiredThreadStatus == TS_STOP)
				{
					// Mark as finished and break from the loop
					pThis->_requiredThreadStatus = TS_STOP;
					break;
				}
				
                pThis->_waitEvent.Reset();
			}
			
			// Wait for event signalling new data (or cancel)
			pThis->_waitEvent.Wait(INFINITE);
		}

		// Check thread continue status
		{
			kmk::Lock lock(pThis->_criticalSection);
			keepRunning = pThis->_requiredThreadStatus;
		}
	} while (keepRunning == TS_RUNNING || keepRunning == TS_FINISH);

	// Raise the finished callback for the detector?
	if (pThis->_detectorStatus == TS_FINISH)
	{
		kmk::Lock lock(pThis->_criticalSection);
		if (pThis->_finishedCallback != NULL)
		{
			(*pThis->_finishedCallback)(pThis->_finishedCallbackArg, false);
			pThis->_detectorStatus = TS_STOP;
		}
	}

	delete[] pBuffer;
	return 0;
}

// Callback raised everytime data is received from the data interface.
void IntervalCountProcessor::ReadDataCallbackProc(void *pArg, unsigned char *pData, size_t dataSize)
{
	IntervalCountProcessor *pThis = (IntervalCountProcessor*)pArg;

	// Pass data onto the data processor
	pThis->QueueData(kmk::Time::GetTime(), pData, dataSize);
}

void IntervalCountProcessor::DataInterfaceErrorCallbackProc(void *pArg, int errorCode, String message)
{
	IntervalCountProcessor *pThis = (IntervalCountProcessor*)pArg;
	pThis->RaiseError(errorCode, message);
}

void IntervalCountProcessor::RaiseError(int errorCode, String message)
{
	if (_errorCallback != NULL)
	{
		(*_errorCallback)(_errorCallbackArg, errorCode, message);
	}
}

}
