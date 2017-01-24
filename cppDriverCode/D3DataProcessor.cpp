#include "stdafx.h"
#include "D3DataProcessor.h"
#include "D3Structs.h"
#include "kmkTime.h"
#include <cstring>
#include <stdlib.h>
#include <algorithm>

#include "SIGMA_25.h"
#include "TN15.h"
#include <assert.h>


// The main reports max size is 8205 bytes and we only request it one at a time. 
// Add some more space for configuration setting reports that might also be returned
#define MAX_REPORT_SIZE 8205

// Allocate enough space for (approx) a seconds worth of data
#define MAX_BUFFER_SIZE (MAX_REPORT_SIZE * 20)

// Number of milliseconds to wait between querying for a new spectrum
#define QUERY_SPECTRUM_RATE 100

// Timeout in ms for configuration querys
#define CONFIGURATION_QUERY_TIMEOUT 2000

namespace kmk
{
D3DataProcessor::D3DataProcessor(IDataInterface *pDataInterface)
: _pDataInterface(pDataInterface)
, _waitEvent(false, false, L"")
, _requiredThreadStatus(TS_STOP)
, _ignoreFirstSpectrumDataPacket(true)
, _accumilatedRealTimeMs(0)
, _configurationQueryState(CQS_IDLE)
, _configurationQueryEvent(false, false, L"")

{
	_messageQueueBuffer.resize(MAX_BUFFER_SIZE);
	_messageQueueBufferReadIndex = 0;
	_messageQueueBufferWriteIndex = 0;
	_messageQueueBufferDataSize = 0;

	_inputPacketBuffer.resize(MAX_REPORT_SIZE);
	_inputPacketBufferDataSize = 0;

	_pDataInterface->SetDataReadyCallback(ReadDataCallbackProc, this);
	_pDataInterface->SetErrorCallback(DataInterfaceErrorCallbackProc, this);
}

D3DataProcessor::~D3DataProcessor()
{
	_pDataInterface->SetDataReadyCallback(NULL, NULL);
	_pDataInterface->SetErrorCallback(NULL, NULL);
}

void D3DataProcessor::AddComponent(uint8_t componentId, IDevice *pDevice, CountEventCallbackFunc pCountEventFunc, 
		void *pCountEventArg, FinishedProcessingCallbackFunc pFinishedFunc, void *pFinishedArg,
		ErrorCallbackFunc pErrorFunc, void *pErrorArg)
{
	kmk::Lock lock(_criticalSection);
	kmk::Lock eventLock(_eventSection);

	ComponentDesc *pDesc;
	if (componentId == SigmaComponentId)
		pDesc = &_sigmaComponent;
	else if (componentId == TN15ComponentId)
		pDesc = &_tn15Component;
	else
		return;
	
	pDesc->pDevice = pDevice;
	pDesc->countEventCallback = pCountEventFunc;
	pDesc->countEventCallbackArg = pCountEventArg;
	
	pDesc->finishedCallback = pFinishedFunc;
	pDesc->finishedCallbackArg = pFinishedArg;

	pDesc->errorCallback = pErrorFunc;
	pDesc->errorCallbackArg = pErrorArg;
}

void D3DataProcessor::RemoveComponent(uint8_t componentId, IDevice *)
{
	kmk::Lock lock(_criticalSection);
	kmk::Lock eventLock(_eventSection);

	// Remove the reference to the component
	switch(componentId)
	{
	case SigmaComponentId:
		_sigmaComponent.Clear();
		break;

	case TN15ComponentId:
		_tn15Component.Clear();
		break;
	}
}

int64_t D3DataProcessor::GetRealTime(uint8_t componentId)
{
	kmk::Lock lock(_criticalSection);
	switch(componentId)
	{
	case SigmaComponentId:
		return _sigmaComponent.accumilatedRealTimeMs;

	case TN15ComponentId:
		return _tn15Component.accumilatedRealTimeMs;
	}

	return 0;
}

void D3DataProcessor::ResetRealTime(uint8_t componentId)
{
    kmk::Lock lock(_criticalSection);
    switch(componentId)
    {
    case SigmaComponentId:
        _sigmaComponent.accumilatedRealTimeMs = 0;
        break;

    case TN15ComponentId:
        _tn15Component.accumilatedRealTimeMs = 0;
        break;
    }
}

void D3DataProcessor::AddToMessageQueue(BYTE *pData, size_t dataLength)
{
	// Append to the end of the buffer as long as there is space
	size_t remainingBufferSpace = MAX_BUFFER_SIZE - _messageQueueBufferDataSize;
	if (dataLength > remainingBufferSpace)
	{
		RaiseError(ERROR_INTERNAL_DEVICE, L"Message Buffer Full. Packet Ignored");
		return; // Proper error
	}
	
	for (size_t i = 0; i < dataLength; ++i)
	{
		_messageQueueBuffer[_messageQueueBufferWriteIndex++] = pData[i];

		// Wrap around if necessary
		if (_messageQueueBufferWriteIndex >= MAX_BUFFER_SIZE)
			_messageQueueBufferWriteIndex = 0;
	}

	_messageQueueBufferDataSize += dataLength;
}

// NOTE: This call is coming from the read thread of the DataInterface, make sure its fast!
void D3DataProcessor::QueueData(int64_t /*timeStamp*/, BYTE *pData, size_t dataLength)
{
	kmk::Lock lock(_criticalSection);

    size_t totalDataLength = _inputPacketBufferDataSize + dataLength;
	bool newPacketReceived = false;
	int readIndex = 0;
	BYTE sizeBytes[2];

	while (1)
	{
		unsigned short *pPacketSize = NULL;

		// We need at least 2 bytes for the packet length
		if (totalDataLength - readIndex >= 2)
		{
			// Get two bytes to use as packet size. Remember they could be spread between the two buffers
			sizeBytes[0] = ((size_t)readIndex < _inputPacketBufferDataSize) ? _inputPacketBuffer[readIndex] : pData[readIndex - _inputPacketBufferDataSize];
			sizeBytes[1] = ((size_t)readIndex + 1 < _inputPacketBufferDataSize) ? _inputPacketBuffer[readIndex + 1] : pData[readIndex + 1 - _inputPacketBufferDataSize];
			pPacketSize = (unsigned short*)sizeBytes;

			// TODO/TEMP: Ignore the next 26 bytes if packetsize == 0
			if (*pPacketSize == 0 || *pPacketSize > _inputPacketBuffer.size())
			{
                RaiseError(ERROR_READ_FAILED, L"Corrupt input data detected.");
				return;
			}
		}

		// Is there enough data between the two buffers to construct this packet?
		if (pPacketSize && *pPacketSize <= totalDataLength - readIndex)
		{
			// We have a full packet, copy enough data from the two buffers into the message queue
			size_t remainingBufferSpace = MAX_BUFFER_SIZE - _messageQueueBufferDataSize;
			if (*pPacketSize <= remainingBufferSpace)
			{
                int sizeFromBuffer = std::max<int>(0, std::min((int)*pPacketSize, (int)_inputPacketBufferDataSize - readIndex));
				int sizeFromNewData = *pPacketSize - sizeFromBuffer;

				if (sizeFromBuffer != 0)
					AddToMessageQueue(&_inputPacketBuffer[readIndex], sizeFromBuffer);
				if (sizeFromNewData != 0)
					AddToMessageQueue(&pData[readIndex + sizeFromBuffer - _inputPacketBufferDataSize], sizeFromNewData);

				newPacketReceived = true;
			}
			else
			{
				RaiseError(ERROR_INTERNAL_DEVICE, L"Message Buffer Full. Packet Ignored");
			}

			readIndex += *pPacketSize;
		}
		else
		{
			// No. Move/Copy the remaining data to the start of the _inputPacketBuffer
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

// Get the given number of bytes from the input buffer. if peekOnly == true DO NOT remove the data from the input buffer
// NOTE: _criticalSection should be locked BEFORE calling this function
bool D3DataProcessor::GetDataFromInputBuffer(BYTE *pDataOut, size_t numBytes, bool peekOnly)
{
	// Not enough bytes ready
	if (_messageQueueBufferDataSize < numBytes)
		return false;

    size_t readIndex = _messageQueueBufferReadIndex;
	for (size_t i = 0; i < numBytes; ++i)
	{
		pDataOut[i] = _messageQueueBuffer[readIndex++];
		
		if (readIndex >= MAX_BUFFER_SIZE)
			readIndex = 0;
	}

	// Remove the data from the input buffer?
	if (!peekOnly)
	{
		_messageQueueBufferReadIndex = readIndex;
		_messageQueueBufferDataSize -= numBytes;
	}

	return true;
}

// Check the input buffer to see if a full report is ready to process. Return the data and remove it from the input buffer if its ready.
// Returns false if no report is ready
bool D3DataProcessor::GetNextReport(std::vector<BYTE> &dataBufferOut, size_t &reportSizeOut)
{
	kmk::Lock lock(_criticalSection);

	// The first two bytes of a report give the size of the report
	unsigned short reportSize;
	if (!GetDataFromInputBuffer((BYTE*)&reportSize, 2, true))
		return false;

	assert(reportSize != 0);
	// Do we have all the bytes for this report?
	if (_messageQueueBufferDataSize < reportSize)
		return false;

	// Read all the data and remove from the input buffer
	if (dataBufferOut.size() < reportSize)
		dataBufferOut.resize(reportSize);

	GetDataFromInputBuffer(&dataBufferOut[0], reportSize, false);
	reportSizeOut = reportSize;
	return true;
}

void D3DataProcessor::Reset()
{
	kmk::Lock lock(_criticalSection);

	// Clear all acquired data
	_messageQueueBufferDataSize = 0;
	_messageQueueBufferReadIndex = 0;
	_messageQueueBufferWriteIndex = 0;
	_accumilatedRealTimeMs = 0;

	_inputPacketBufferDataSize = 0;
}

bool D3DataProcessor::StartProcessing(unsigned char componentId)
{
	kmk::Lock lock(_criticalSection);

	switch (componentId)
	{
	case SigmaComponentId:
		if (_sigmaComponent.status == TS_RUNNING)
			return true;
		
		_sigmaComponent.status = TS_RUNNING;
		_sigmaComponent.startStopTimestamp = Time::GetTime();
		_sigmaComponent.accumilatedRealTimeMs = 0;
		break;

	case TN15ComponentId:
		if (_tn15Component.status == TS_RUNNING)
			return true;
		
		_tn15Component.status = TS_RUNNING;
		_tn15Component.startStopTimestamp = Time::GetTime();
		_tn15Component.accumilatedRealTimeMs = 0;
		break;

	case ConfigurationComponentId:
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
			_pDataInterface->BeginReading();
		}

		// The first data packet in any acquisition represents the total time since the very last request which is of no use to the 
		// new acquisition so ignore it
		_ignoreFirstSpectrumDataPacket = true;
		_accumilatedRealTimeMs = 0;

		if (!_thread.Start(ProcessThreadProc, this))
		{
			_requiredThreadStatus = TS_STOP;
			return false;
		}
	}

	return true;
}

bool D3DataProcessor::StopProcessing(unsigned char componentId, bool force)
{
	bool stopReading = false;

	{
		kmk::Lock lock(_criticalSection);

		switch (componentId)
		{
		case SigmaComponentId:
			if (_sigmaComponent.status == TS_STOP)
				return true;
			
			_sigmaComponent.status = force ? TS_STOP : TS_FINISH;
			_sigmaComponent.startStopTimestamp = Time::GetTime();
			break;

		case TN15ComponentId:
			if (_tn15Component.status == TS_STOP)
				return true;
			
			_tn15Component.status = force ? TS_STOP : TS_FINISH;
			_tn15Component.startStopTimestamp = Time::GetTime();
			break;

		case ConfigurationComponentId:
			break;
		default:
			return false;
		}

		stopReading =	_requiredThreadStatus != TS_STOP && 
						_sigmaComponent.status != TS_RUNNING && 
						_tn15Component.status != TS_RUNNING &&
						_configurationQueryState != CQS_WAITING;
	}
	
	if (stopReading)
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
	
	if (force)
	{
		// If it is forced but we are not stopping the read (another component is still active) then raise the finished event 
		// for this component immediatly
		kmk::Lock lock(_eventSection);
		switch (componentId)
		{
		case SigmaComponentId:
			(*_sigmaComponent.finishedCallback)(_sigmaComponent.finishedCallbackArg, true);
			break;

		case TN15ComponentId:
			(*_tn15Component.finishedCallback)(_tn15Component.finishedCallbackArg, true);
			break;
		}
	}

	return true;
}

// Process a report (called on the process thread)
void D3DataProcessor::ProcessReport(BYTE *pData)
{
	// Determine the report type
	MessageHeader *pMessageHeader = (MessageHeader*)pData;

	switch(pMessageHeader->contentHeader.reportID)
	{
	case D3StartResponseHeader::REPORT_ID:
		break;

	case D3Spectrum16ResponseHeader::REPORT_ID:
		// Parse the spectrum data
		ProcessSpectrum16Report((D3Spectrum16ResponseHeader*)pData);
		break;

	case D3InternalErrorMessage::REPORT_ID:
		// TODO: Report an error
		{
			D3InternalErrorMessage *pErrorHeader = (D3InternalErrorMessage*)pData;
			
#ifdef _UNICODE
			wchar_t buffer[D3InternalErrorMessage::BUFFER_SIZE];
#ifdef _WINDOWS
			size_t charsToConvert = D3InternalErrorMessage::BUFFER_SIZE;
			mbstowcs_s(&charsToConvert, buffer, pErrorHeader->m_errorText, D3InternalErrorMessage::BUFFER_SIZE);
#else
            mbstowcs(buffer, pErrorHeader->m_errorText, D3InternalErrorMessage::BUFFER_SIZE);
#endif
			String str (buffer);
#else
			String str (pErrorHeader->m_errorText);
#endif
			RaiseError(ERROR_INTERNAL_DEVICE, str);
		}
		break;

	case D3Configuration16::REPORT_ID_GET_BIAS:
	case D3Configuration16::REPORT_ID_GET_LLD:
	case D3Configuration16::REPORT_ID_GET_VERSION:
	case D3Configuration8::REPORT_ID_GET_GAIN:
	case D3Configuration8::REPORT_ID_GET_OTG:
		ProcessConfigurationReport(pMessageHeader);
		break;

	case D3ConfigurationSerial::REPORT_ID_GET_SERIAL:
		ProcessConfigurationReport(pMessageHeader);
		break;
	}

}

void D3DataProcessor::ProcessSpectrum16Report(D3Spectrum16ResponseHeader *pMessage)
{
	CountEventCallbackFunc sigmaEventFunc = NULL;
	CountEventCallbackFunc tn15EventFunc = NULL;
	void *pSigmaEventArg = NULL;
	void *ptn15EventArg = NULL;

	FinishedProcessingCallbackFunc sigmaFinishedFunc = NULL;
	FinishedProcessingCallbackFunc tn15FinishedFunc = NULL;
	void *pSigmaFinishedArg = NULL;
	void *ptn15FinishedArg = NULL;
	int64_t timestamp = 0;

	// Grab a local copy of the event functions (We dont want the critical section locked during the call to the actual event functions)
	{
		kmk::Lock lock(_criticalSection);

		// The first data packet in any acquisition represents the total time since the very last request which is of no use to the 
		// new acquisition so ignore it
		if (_ignoreFirstSpectrumDataPacket)
		{
			_ignoreFirstSpectrumDataPacket = false;

			// Store the timestamp of the current time as a reference point
			_startAcquisitionTimestamp = Time::GetTime();
			return;
		}

		// Calculate the timestamp for this data
		_accumilatedRealTimeMs += pMessage->realTimeMS;

		timestamp = _startAcquisitionTimestamp + MS_TO_TICKS(_accumilatedRealTimeMs);

		int64_t currentTime = Time::GetTime();
		
		// The timestamp should never exceed the current time on the system clock, if it does then we are seeing a drift in time
		// between the device and host machine. Correct it at this point
		if (timestamp > currentTime)
		{
			_accumilatedRealTimeMs = kmk::Time::TicksToMs(currentTime - _startAcquisitionTimestamp);
			timestamp = currentTime;
		}

		// If the components are enabled then set the callbacks
		if (_sigmaComponent.status != TS_STOP)
		{
			if ((_sigmaComponent.status == TS_RUNNING && _sigmaComponent.startStopTimestamp <= timestamp) || _sigmaComponent.startStopTimestamp >= timestamp)
			{
				sigmaEventFunc = _sigmaComponent.countEventCallback;
				pSigmaEventArg = _sigmaComponent.countEventCallbackArg;
				_sigmaComponent.accumilatedRealTimeMs += pMessage->realTimeMS;
			}
			else if (_sigmaComponent.status == TS_FINISH)
			{	// The component is waiting to finish and the latest message is beyond the stop time so raise the event
				_sigmaComponent.status = TS_STOP;
				sigmaFinishedFunc = _sigmaComponent.finishedCallback;
				pSigmaFinishedArg = _sigmaComponent.finishedCallbackArg;
			}
		}

		if (_tn15Component.status != TS_STOP)
		{
			if ((_tn15Component.status == TS_RUNNING && _tn15Component.startStopTimestamp <= timestamp) || _tn15Component.startStopTimestamp >= timestamp)
			{
				tn15EventFunc = _tn15Component.countEventCallback;
				ptn15EventArg = _tn15Component.countEventCallbackArg;
				_tn15Component.accumilatedRealTimeMs += pMessage->realTimeMS;
			}
			else if (_tn15Component.status == TS_FINISH)
			{	// The component is waiting to finish and the latest message is beyond the stop time so raise the event
				_tn15Component.status = TS_STOP;
				tn15FinishedFunc = _tn15Component.finishedCallback;
				ptn15FinishedArg = _tn15Component.finishedCallbackArg;
			}
		}
	}

	// Gamma spectrum / SIGMA
	// Raise an event for each channel containing counts
	if (sigmaEventFunc != NULL)
	{
		for (int i = 0; i < D3Spectrum16ResponseHeader::SPECTRUM_SIZE; ++i)
		{
			assert(pMessage->gammaSpectrum[i] < 1000);
			if (pMessage->gammaSpectrum[i] > 0)
				(*sigmaEventFunc)(pSigmaEventArg, timestamp, i, pMessage->gammaSpectrum[i]);
		}
	}
	else if (sigmaFinishedFunc != NULL)
	{
		(*sigmaFinishedFunc)(pSigmaFinishedArg, false);
	}

	// Neutron / TN15
	if (tn15EventFunc != NULL)
	{
		if (pMessage->neutronCounts > 0)
			(*tn15EventFunc)(ptn15EventArg, timestamp, 0, pMessage->neutronCounts);		
	}
	else if (tn15FinishedFunc != NULL)
	{
		(*tn15FinishedFunc)(ptn15FinishedArg, false);
	}
}

void D3DataProcessor::ProcessConfigurationReport(MessageHeader *pMessageHeader)
{
	// A configuration report response has been received. If we are still waiting
	// for the response then store the data and notify the original calling thread
	Lock lock(_criticalSection);
	if (_configurationQueryState != CQS_WAITING)
	{
		// We are not waiting for a response (probably timed out). Just ignore this report
		return;
	}

	// Copy the full packet into the result buffer
	if (_configurationQueryResultData.size() < pMessageHeader->messageSize)
		_configurationQueryResultData.resize(pMessageHeader->messageSize);

    std::memcpy(&_configurationQueryResultData[0], pMessageHeader, pMessageHeader->messageSize);
	_configurationQueryState = CQS_SUCCESS;
	
	// Signal the waiting thread that data is ready
	_configurationQueryEvent.Signal();
}

bool D3DataProcessor::GetConfigurationData(uint8_t componentId, uint8_t configurationId, BYTE *pDataOut, size_t &dataLength)
{
    D3GetConfiguration request;
    memset(&request, 0, sizeof(request));
	request.m_message.messageSize = sizeof(D3GetConfiguration);
	request.m_message.contentHeader.componentID = componentId;
	request.m_message.contentHeader.reportID = configurationId;

	{
		kmk::Lock lock(_criticalSection);

		// Getting a configuration requires writing a report to the device and waiting for a response
		if (_configurationQueryState != CQS_IDLE)
			return false;

		_configurationQueryEvent.Reset();
		_configurationQueryState = CQS_WAITING;
	}
	
	// Make sure the data processor is running to process the configuration response
	StartProcessing(ConfigurationComponentId);

	// Send the request
	if (!_pDataInterface->GetConfigurationSetting((unsigned char*)&request, sizeof(D3GetConfiguration)))
	{
		{
			kmk::Lock lock(_criticalSection);
			_configurationQueryState = CQS_IDLE;
		}

		StopProcessing(ConfigurationComponentId, true);
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
		StopProcessing(ConfigurationComponentId, true);
		
		if (result)
		{
			kmk::Lock lock(_criticalSection);

			// Grab the data out of the packet and copy into the output buffer
			MessageHeader *pHeader = (MessageHeader*)&_configurationQueryResultData[0];
			assert(pHeader->contentHeader.componentID == componentId);

			// Calculate the size of the data by removing the size of the header and crc
			size_t sizeOfData = pHeader->messageSize - sizeof(MessageHeader) - sizeof(uint16_t);

			// Success, copy the result back into the buffer
			if (sizeOfData > dataLength)
			{
				result = false; // Not enough space in the buffer!
				dataLength = 0;
			}
			else
			{
                std::memcpy(pDataOut, &_configurationQueryResultData[sizeof(MessageHeader)], sizeOfData);
				dataLength = sizeOfData;
			}
		}
		else
		{
			dataLength = 0;
		}
	}
	return result;
}

bool D3DataProcessor::SetConfigurationData(uint8_t componentId, uint8_t configurationId, BYTE *pDataIn, size_t dataLength)
{
	const int fullHeaderSize = sizeof(MessageHeader) + sizeof(uint16_t); // Size of header + crc

	// For D3 force dfu command to if board
	if (configurationId == REPORT_ID_SET_DFU)
		componentId = InterfaceBoardComponentId;

	// Create the header and insert the data
	std::vector<BYTE> buffer;
	buffer.resize(fullHeaderSize + dataLength);

	MessageHeader *pHeader = (MessageHeader*)&buffer[0];
	pHeader->contentHeader.componentID = componentId;
	pHeader->contentHeader.reportID = configurationId;
    pHeader->messageSize = (uint16_t)buffer.size();
    std::memcpy(&buffer[sizeof(MessageHeader)], pDataIn, dataLength);

	// Send the configuration to the device
	return _pDataInterface->SetConfigurationSetting(&buffer[0], buffer.size());
}

int D3DataProcessor::ProcessThreadProc(void *pArg)
{
	D3DataProcessor *pThis = (D3DataProcessor*)pArg;
	std::vector<BYTE> tempBuffer;
	tempBuffer.resize(MAX_REPORT_SIZE);
	size_t tempReportSize = 0;
	int64_t nextQueryTime = kmk::Time::GetTimeMs();

	bool forcedStop = true;
	
	ThreadStatus keepRunning = TS_RUNNING;
	do
	{
		// If something is in the queue then process it, otherwise wait for data		
		if (pThis->GetNextReport(tempBuffer, tempReportSize))
		{
			// Process
            pThis->ProcessReport(&tempBuffer[0]);
		}
		else
		{
			// No more data, check if we have been asked to finish once all data is processed
			{
				kmk::Lock lock(pThis->_criticalSection);
				if (pThis->_requiredThreadStatus == TS_FINISH)
				{
					// Mark as finished and break from the loop
					pThis->_requiredThreadStatus = TS_STOP;
					forcedStop = false;
					break;
				}

				pThis->_waitEvent.Reset();
			}
			
			// Wait for event signalling new data or the time to query the next spectrum data
            uint32_t waitTime = (uint32_t)std::max<int64_t>(nextQueryTime - kmk::Time::GetTimeMs(), 1);
			pThis->_waitEvent.Wait(waitTime);
		}

		// Are we ready to query for a new spectrum?
		if (kmk::Time::GetTimeMs() >= nextQueryTime)
		{
			// Only send requests if we need them, connections serving only configuration requests need not apply
            bool configOnly = (pThis->_tn15Component.status == TS_STOP && pThis->_sigmaComponent.status == TS_STOP);
			if (!configOnly)
			{
				D3BasicRequestHeader request;
				memset(&request, 0, sizeof(D3BasicRequestHeader));
				request.componentID = InterfaceBoardComponentId;
				request.reportID = REPORT_ID_GET_16BIT_SPECTRUM;
				request.messageSize = sizeof(D3BasicRequestHeader);
				pThis->_pDataInterface->SetConfigurationSetting((unsigned char*)&request, sizeof(D3BasicRequestHeader));
			}

			nextQueryTime = kmk::Time::GetTimeMs() + QUERY_SPECTRUM_RATE; 
		}

		// Check thread continue status
		{
			kmk::Lock lock(pThis->_criticalSection);
			keepRunning = pThis->_requiredThreadStatus;
		}
	} while (keepRunning == TS_RUNNING || keepRunning == TS_FINISH);

	{
		// Raise finished callback (if not already raised)
		kmk::Lock lock(pThis->_eventSection);
		if (pThis->_sigmaComponent.finishedCallback != NULL && pThis->_sigmaComponent.status != TS_STOP)
		{
			 pThis->_sigmaComponent.status= TS_STOP;
			(*(pThis->_sigmaComponent.finishedCallback))(pThis->_sigmaComponent.finishedCallbackArg, forcedStop);
		}

		if (pThis->_tn15Component.finishedCallback != NULL && pThis->_tn15Component.status != TS_STOP)
		{
			pThis->_tn15Component.status = TS_STOP;
			(*(pThis->_tn15Component.finishedCallback))(pThis->_tn15Component.finishedCallbackArg, forcedStop);
		}
	}

	return 0;
}

// Callback raised everytime data is received from the data interface.
void D3DataProcessor::ReadDataCallbackProc(void *pArg, unsigned char *pData, size_t dataSize)
{
	D3DataProcessor *pThis = (D3DataProcessor*)pArg;

	// Pass data onto the data processor
	pThis->QueueData(kmk::Time::GetTime(), pData, dataSize);
}

void D3DataProcessor::DataInterfaceErrorCallbackProc(void *pArg, int errorCode, String message)
{
	D3DataProcessor *pThis = (D3DataProcessor*)pArg;
	pThis->RaiseError(errorCode, message);
}

void D3DataProcessor::RaiseError(int errorCode, String message)
{
	kmk::Lock lock(_eventSection);

	// Raise an error accross each component if its active
	if (_sigmaComponent.status != TS_STOP)
	{
		if (_sigmaComponent.errorCallback != NULL)
		{
			(*_sigmaComponent.errorCallback)(_sigmaComponent.errorCallbackArg, errorCode, message);
		}
	}

	if (_tn15Component.status != TS_STOP)
	{
		if (_tn15Component.errorCallback != NULL)
		{
			(*_tn15Component.errorCallback)(_tn15Component.errorCallbackArg, errorCode, message);
		}
	}
}

}
