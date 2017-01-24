#pragma once

#include "types.h"
#include "kromek_endian.h"

namespace kmk
{

class IDevice;

// Event raised when counts come in from a detector. An event should be raised for each channel that contains new counts
typedef void (*CountEventCallbackFunc)(void *pArg, int64_t timestamp, int channel, int numCounts);
typedef void (*FinishedProcessingCallbackFunc)(void *pArg, bool wasForced);
typedef void (*ErrorCallbackFunc)(void *pArg, int code, String message);

class IDataProcessor
{
public:
	IDataProcessor() {};
	virtual ~IDataProcessor() {}

	virtual kmk::Endian::Order GetEndian() const = 0;

	virtual void QueueData(int64_t timeStamp, unsigned char *pData, size_t dataLength) = 0;
	virtual void Reset() = 0;

	// For data processors that may contain multiple components the following two functions allow components to
	// be registered.
	// ComponentId - Unique Id for the component
	// pDevice - Component device
	// pCountEventFunc - Callback func for everytime a count event is recieved
	// pCountEventArg - Arg passed into callback func
	// pFinishedFunc - Callback func for everytime acquisition completes
	// pFinishedArg - Arg passed into callback func
	// pErrorFunc - Error callback func
	// pErrorArg - Arg passed into callback func
	virtual void AddComponent(uint8_t, IDevice *pDevice, CountEventCallbackFunc pCountEventFunc, 
		void *pCountEventArg, FinishedProcessingCallbackFunc pFinishedFunc, void *pFinishedArg,
		ErrorCallbackFunc pErrorFunc, void *pErrorArg) = 0;

	// After a call to RemoveComponent the component device should never be accessed from within the data processor again (possibly deleted)
	virtual void RemoveComponent(uint8_t componentId, IDevice *pDevice) = 0;

	virtual bool StartProcessing(uint8_t componentId) = 0;

	// Stop processing data. If force = false then the data processor should only stop once its current queue is finished.
	// Otherwise the process should be stopped as soon as possible
	virtual bool StopProcessing(uint8_t componentId, bool force) = 0;

	// Return the real time of the current / last acquisition (in ms)
	virtual int64_t GetRealTime(uint8_t componentId) = 0;

    // Reset the real time to 0ms
    virtual void ResetRealTime(uint8_t componentId) = 0;

	// Get configuration data. Should return the data in the pDataOut buffer and set dataLength to the length of the returned data
	// dataLength should be passed in with the length of the pDataOut buffer
	virtual bool GetConfigurationData(uint8_t componentId, uint8_t configurationId, BYTE *pDataOut, size_t &dataLength) = 0;

	// Set a configuration setting. dataLength should be set to the length pDataIn
	virtual bool SetConfigurationData(uint8_t componentId, uint8_t configurationId, BYTE *pDataIn, size_t dataLength) = 0;
};

}
