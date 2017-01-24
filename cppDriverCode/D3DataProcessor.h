#pragma once

#include "IDataProcessor.h"
#include "IDevice.h"
#include <vector>
#include "Thread.h"
#include "Lock.h"
#include "Event.h"
#include "RollingQueue.h"
#include "D3Structs.h"

namespace kmk
{
// A class representing a data processor for the D3 detector. The D3 contains 2 components (Sigma + TN15)
class D3DataProcessor : public IDataProcessor
{
public:

	// Id values of each of the components including a cnfiguration component used when we are waiting for GetConfigurationData to be returned
	static const int SigmaComponentId = 0x01;
	static const int TN15ComponentId = 0x02;
	static const int InterfaceBoardComponentId = 0x07;
	static const int ConfigurationComponentId = 0x0a;

private:

	enum ThreadStatus
	{
		TS_STOP,	// Thread is stopped / should be stopped immediatly
		TS_RUNNING, // Thread is running / should continue running
		TS_FINISH	// Thread is running / should finish current queue then stop
	};

	// Each component needs its own set of callback routines and settings
	struct ComponentDesc
	{
		IDevice *pDevice;
		CountEventCallbackFunc countEventCallback;
		void *countEventCallbackArg;
		FinishedProcessingCallbackFunc finishedCallback;
		void *finishedCallbackArg;
		ErrorCallbackFunc errorCallback;
		void *errorCallbackArg;
		ThreadStatus status;	// Whether this device is acquiring
		int64_t startStopTimestamp; // Timestamp - If enabled then this is the start time of acquisition otherwise the end time of acquisition
		int64_t accumilatedRealTimeMs; // Real time of the currently action / previous acquisition

		ComponentDesc()
			: pDevice(NULL)
			, countEventCallback(NULL)
			, countEventCallbackArg(NULL)
			, finishedCallback(NULL)
			, finishedCallbackArg(NULL)
			, errorCallback(NULL)
			, errorCallbackArg(NULL)
			, status(TS_STOP)
			, startStopTimestamp(0)
			, accumilatedRealTimeMs(0)
		{

		}

		void Clear()
		{
			pDevice = NULL;
			countEventCallback = NULL;
			countEventCallbackArg = NULL;
			finishedCallback = NULL;
			finishedCallbackArg = NULL;
			errorCallback = NULL;
			errorCallbackArg = NULL;
			status = TS_STOP;
			startStopTimestamp = 0;
			accumilatedRealTimeMs = 0;
		}
	};

	// The data interface used for sending configuration requests
	IDataInterface *_pDataInterface;
	ComponentDesc _sigmaComponent;
	ComponentDesc _tn15Component;
	
	// Thread status properties
	kmk::Thread _thread;
	kmk::CriticalSection _criticalSection;
	kmk::CriticalSection _eventSection;
	kmk::Event _waitEvent;
	ThreadStatus _requiredThreadStatus;
	
	// Ignore the first spectrum data message in every acquisition
	bool _ignoreFirstSpectrumDataPacket;
	
	// Timestamp set when the first spectrum data packet is recieved and used to calculate the timestamp of all subsequent counts
	int64_t _startAcquisitionTimestamp;
	int64_t _accumilatedRealTimeMs;
	
	// We need to construct two input buffers. The first will be used as soon as data comes in to construct a full packet.
	// Only when we have a full packet will it be added to the full circular message buffer. By only trying to add full packets to
	// the circular messages buffer we can discard the full packet if the buffer is full
	std::vector<BYTE> _inputPacketBuffer;
	size_t _inputPacketBufferDataSize;

	// Circular buffer containing full messages in a stream of bytes. If this buffer is full then new messages will be discarded
	std::vector<BYTE> _messageQueueBuffer;
	size_t _messageQueueBufferReadIndex;
	size_t _messageQueueBufferWriteIndex;
	size_t _messageQueueBufferDataSize;

	// Variables used for querying a configuration variable. 
	enum ConfigurationQueryState
	{
		CQS_IDLE,
		CQS_WAITING,
		CQS_SUCCESS,
		CQS_ERROR
	};

	ConfigurationQueryState _configurationQueryState;
	std::vector<BYTE> _configurationQueryResultData;
	kmk::Event _configurationQueryEvent;

	// Add a complete message to the queue ready to be processed
	void AddToMessageQueue(BYTE *pData, size_t dataLength);

	// Get the given number of bytes from the input buffer. if peakOnly == true DO NOT remove the data from the input buffer
	// NOTE: _criticalSection should be locked BEFORE calling this function
	bool GetDataFromInputBuffer(BYTE *pDataOut, size_t numBytes, bool peekOnly);

	// Check the input buffer to see if a full report is ready to process. Return the data and remove it from the input buffer if its ready.
	// Returns false if no report is ready
	bool GetNextReport(std::vector<BYTE> &dataBufferOut, size_t &reportSizeOut);

	// Processing thread routine
    static int ProcessThreadProc(void *pArg);

	// Callback routine called when data is received from the data interface
	static void ReadDataCallbackProc(void *pArg, unsigned char *pData, size_t dataSize);

	// Callback routine when an error occurs on the data interface
	static void DataInterfaceErrorCallbackProc(void *pArg, int errorCode, String message);

	// Process a single report
    void ProcessReport(BYTE *pData);

	// Process a report containing the main spectrum data
	void ProcessSpectrum16Report(D3Spectrum16ResponseHeader *pMessage);

	// Process the return data from a configuration request
	void ProcessConfigurationReport(MessageHeader *pMessageHeader);

	// Raise an error on the error callback routine
	void RaiseError(int errorCode, String message);

public:

	D3DataProcessor(IDataInterface *pDataInterface);
	~D3DataProcessor(void);

    kmk::Endian::Order GetEndian() const { return kmk::Endian::LittleEndian;  }

	// Queue data received from the data interface. Data is not necessary a full packet
	void QueueData(int64_t timeStamp, BYTE *pData, size_t dataLength);

	// Reset the data processor ready to start again
	void Reset();
	
	// Start the processing thread (if not already running) and acquire data for the given component until StopProcessing is called. Components can run independently
	bool StartProcessing(unsigned char componentId);

	// Stop the processing thread. If force = true then stop the thread as soon as possible without finishing the processing of data in the queue - Blocks until 
	// finished. If force = false then the processing queue will be completed and this function will not block (use finished callback)
	bool StopProcessing(unsigned char componentId, bool force);
	
	// Add a component device and its associated callbacks. The D3 accepts a Sigma and TN15
	void AddComponent(uint8_t, IDevice *pDevice, CountEventCallbackFunc pCountEventFunc, 
		void *pCountEventArg, FinishedProcessingCallbackFunc pFinishedFunc, void *pFinishedArg,
		ErrorCallbackFunc pErrorFunc, void *pErrorArg);

	// After a call to RemoveComponent the component device should never be accessed from within the data processor again (possibly deleted)
	void RemoveComponent(uint8_t componentId, IDevice *pDevice);
	void RemoveComponent(unsigned char componentId);

	// Return the real time of the current / last acquisition on the component
	int64_t GetRealTime(uint8_t componentId);

    // Reset the real time of the component to 0
    void ResetRealTime(uint8_t componentId);

	// Get a configuration setting. dataLength should be set as the size of the buffer in and will be set on return to the size of the data out
	bool GetConfigurationData(uint8_t componentId, uint8_t configurationId, BYTE *pDataOut, size_t &dataLength);

	// Set a configuration setting. dataLength should be set to the length pDataIn
	bool SetConfigurationData(uint8_t componentId, uint8_t configurationId, BYTE *pDataIn, size_t dataLength);
};

}
