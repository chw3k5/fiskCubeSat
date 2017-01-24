#pragma once

#include "IDataProcessor.h"
#include <vector>
#include "Thread.h"
#include "Lock.h"
#include "Event.h"
#include "RollingQueue.h"
#include "IDataInterface.h"

namespace kmk
{

// Data processor for detectors that receive event counts via a report containing a list of channel numbers that events occured on (Most detectors)
class IntervalCountProcessor : public IDataProcessor
{
private:

	enum ThreadStatus
	{
		TS_STOP,	// Thread is stopped / should be stopped immediatly
		TS_RUNNING, // Thread is running / should continue running
		TS_FINISH	// Thread is running / should finish current queue then stop
	};

	// Data interface to write to
	IDataInterface *_pDataInterface;

	// Event callback raised for every count received
	CountEventCallbackFunc _countEventCallback;
	void *_countEventCallbackArg;

	// Callback raised once processing has finished
	FinishedProcessingCallbackFunc _finishedCallback;
	void *_finishedCallbackArg;

	// Callback raised if an error during acquisition occurs
	ErrorCallbackFunc _errorCallback;
	void *_errorCallbackArg;

	// Thread members
	kmk::Thread _thread;
	kmk::CriticalSection _criticalSection;
	kmk::Event _waitEvent;
	
	// Because the processor can be running for both configuration settings and the detector we need different states for each
	// The detector status
	ThreadStatus _detectorStatus;
	ThreadStatus _requiredThreadStatus;

	// We need to construct two input buffers. The first will be used as soon as data comes in to construct a full packet.
	// Only when we have a full packet will it be added to the full circular message buffer. By only trying to add full packets to
	// the circular messages buffer we can discard the full packet if the buffer is full
	std::vector<BYTE> _inputPacketBuffer;
	size_t _inputPacketBufferDataSize;
	RollingQueue _dataQueue;
	
	int64_t _startAcquisitionTime; // Time at which the current / last acquisition was started
	int64_t _endAcquisitionTime; // Time at which acquisition was last stopped
 
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

	// Main processing thread routine
    static int ProcessThreadProc(void *pArg);

	static void ReadDataCallbackProc(void *pThis, unsigned char *pData, size_t dataSize);
	static void DataInterfaceErrorCallbackProc(void *pArg, int errorCode, String message);

	// Return the size of a packet based on its report id as the size is not contained in the report
	int DeterminePacketSize(BYTE reportId);

	// Process a report
	void ProcessReport(int64_t timestamp, unsigned char *pData, size_t dataSize);

	// Process a report containing the count data
	void ProcessDataReport(int64_t timestamp, BYTE *pData, size_t dataSize);

	// Process a reponse to a configuration request
	void ProcessConfigurationReport(BYTE *pData, size_t dataSize);
	
	// Raise an error callback
	void RaiseError(int errorCode, String message);

public:

	IntervalCountProcessor(IDataInterface *pDataInterface);
	~IntervalCountProcessor(void);

    kmk::Endian::Order GetEndian() const { return kmk::Endian::BigEndian; }

	// Queue data received from the data interface. 
	void QueueData(int64_t timeStamp, unsigned char *pData, size_t dataLength);
	
	// Reset the data processor ready to start again
	void Reset();
	
	// Add a component device. Only a single component is supported
	void AddComponent(uint8_t componentId, IDevice *pDevice, CountEventCallbackFunc pCountEventFunc, 
			void *pCountEventArg, FinishedProcessingCallbackFunc pFinishedFunc, void *pFinishedArg,
			ErrorCallbackFunc pErrorFunc, void *pErrorArg);

	// After a call to RemoveComponent the component device should never be accessed from within the data processor again (possibly deleted)
	void RemoveComponent(uint8_t componentId, IDevice *pDevice);

	// Start the processing thread (if not already running) and acquire data for the given component until StopProcessing is called.
	bool StartProcessing(uint8_t componentId);
	
	// Stop the processing thread. If force = true then stop the thread as soon as possible without finishing the processing of data in the queue - Blocks until 
	// finished. If force = false then the processing queue will be completed and this function will not block (use finished callback)
	bool StopProcessing(uint8_t componentId, bool force);
	
	// Return the real time of the current / last acquisition on the component
	int64_t GetRealTime(uint8_t componentId);

    // Reset the real time to 0 of the component
    void ResetRealTime(uint8_t componentId);
	
	// Get a configuration setting. dataLength should be set as the size of the buffer in and will be set on return to the size of the data out
	bool GetConfigurationData(uint8_t componentId, uint8_t configurationId, BYTE *pDataOut, size_t &dataLength);

	// Set a configuration setting. dataLength should be set to the length pDataIn
	bool SetConfigurationData(uint8_t componentId, uint8_t configurationId, BYTE *pDataIn, size_t dataLength);
};

}
