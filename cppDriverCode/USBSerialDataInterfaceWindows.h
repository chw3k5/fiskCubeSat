#pragma once

#include <windows.h>
#include "types.h"
#include "Thread.h"
#include "Lock.h"
#include "IDataInterface.h"
#include "Event.h"
#include <vector>
#include <map>

namespace kmk
{

// Data interface for a serial port connection

class USBSerialDataInterface : public IDataInterface
{
private:
	String _comPortName;

	HANDLE _fileHandle;
	kmk::Thread _readThread;
	bool _readThreadRunning;
	kmk::Event _cancelIOEvent;
	kmk::Event _writeDataReadyEvent;

	std::vector<char> _writeBuffer;
    DWORD _writeBufferIndex;

	// Callback to pass data to once read from the port
	DataReadyCallbackFunc _dataReadyCallback;
	void *_dataReadyCallbackArg;

	// Callback raised whenever an error occurs
	ErrorCallbackFunc _errorCallback;
	void *_errorCallbackArg;

	// Product and vendor id of the device, actually passed into the constructor as a serial port does not
	// have access to these values directly
	unsigned short _vendorID;
	unsigned short _productID;
	InterfaceProperties _ifProperties;
	
	kmk::CriticalSection _readCriticalSection;
	kmk::CriticalSection _writeCriticalSection;

	// Open the file device
	bool OpenDevice();

	// Close the file device
	bool Close();

	// Raise the error callback
	void RaiseError(int errorCode, String message);

	// Send any data in the send buffer to the device
	bool SendDataBufferToDevice(OVERLAPPED &overlap);

	// Main thread routine
    static int ReadDataThread(void *pThis);

public:

	unsigned int GetHash();
	unsigned short GetVendorID();
	unsigned short GetProductID();
	
	USBSerialDataInterface(String comPortName, int productID, int vendorID, const String& location = L"");
	~USBSerialDataInterface();

	// Initialise the device once detected but before being opened
	bool Initialize();

	// Returns if the device file is open
	bool IsOpen();
	
	// Begin reading data from the device until StopReading is called
	bool BeginReading();

	// Stop reading data from the device
	bool StopReading();

	// Get and set configuration settings. The actual response data is returned in the main file stream
	bool GetConfigurationSetting(unsigned char *pDataBuffer, size_t dataLength);
	bool SetConfigurationSetting(unsigned char *pData, size_t dataLength);

	void SetDataReadyCallback(DataReadyCallbackFunc pFunc, void *pArg);
	void SetErrorCallback(ErrorCallbackFunc func, void *pArg);

	String GetInterfaceProperty(const String& name);
};

}
