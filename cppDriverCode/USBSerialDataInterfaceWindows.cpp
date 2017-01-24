#include "StdAfx.h"
#include "USBSerialDataInterfaceWindows.h"
#include <assert.h>
#include "IDevice.h"

#define INPUT_BUFFER_LENGTH 1024
#define MAX_SERIAL_RX_BUFFER 16 
#define MAX_SERIAL_TX_BUFFER 16 

// Size of the output buffer. Data is buffered for writing until the main file thread is ready to send it
#define WRITE_BUFFER_LENGTH 1024

// Enable this to output the raw data comming into the serial port into a 'data.dump'
// file. Data will be appended to an existing file so make sure you delete old data before
// running
//#define OUTPUT_RAW_DATA

#ifdef OUTPUT_RAW_DATA
#pragma message( "WARNING: Build configured to output raw data from serial port! DO NOT RELEASE!"  )
#endif


namespace kmk
{



USBSerialDataInterface::USBSerialDataInterface(String comPortName, int productID, int vendorID, const String& location)
: _comPortName(comPortName)
, _fileHandle(NULL)
, _dataReadyCallback(NULL)
, _dataReadyCallbackArg(NULL)
, _errorCallback(NULL)
, _errorCallbackArg(NULL)
, _readThreadRunning(false)
, _productID(productID)
, _vendorID(vendorID)
, _cancelIOEvent(FALSE, FALSE, L"")
, _writeBufferIndex(0)
{
	// Add the property info
	_ifProperties.insert(std::make_pair(IFPROP_LOCATION, location));
}

USBSerialDataInterface::~USBSerialDataInterface(void)
{
	kmk::Lock lock(_readCriticalSection);
	
	// Stop reading if the device is open
	if (_readThreadRunning)
	{
		StopReading();
	}
}

bool USBSerialDataInterface::Initialize()
{
	_writeBuffer.resize(WRITE_BUFFER_LENGTH);
	return true;
}

unsigned int USBSerialDataInterface::GetHash()
{
	unsigned int hash = 0; 
	for(size_t i = 0; i < _comPortName.length(); ++i)  
		hash = 65599 * hash + _comPortName.c_str()[i]; 
	return hash ^ (hash >> 16); 
}

unsigned short USBSerialDataInterface::GetVendorID()
{
	return _vendorID;
}

unsigned short USBSerialDataInterface::GetProductID()
{
	return _productID;
}

String USBSerialDataInterface::GetInterfaceProperty(const String& name)
{
	InterfaceProperties::iterator i = _ifProperties.find(name);
	return (i != _ifProperties.end()) ? i->second : L"";
}

void USBSerialDataInterface::SetDataReadyCallback(DataReadyCallbackFunc pFunc, void *pArg) 
{
	kmk::Lock lock(_readCriticalSection);
	_dataReadyCallback = pFunc; 
	_dataReadyCallbackArg = pArg;
}

void USBSerialDataInterface::SetErrorCallback(ErrorCallbackFunc func, void *pArg)
{
	kmk::Lock lock(_readCriticalSection);
	_errorCallback = func; 
	_errorCallbackArg = pArg;
}

// Return if the file handle is open
bool USBSerialDataInterface::IsOpen()
{
	kmk::Lock lock(_readCriticalSection);

	return _fileHandle != NULL;
}

// Open the device ready for reading
bool USBSerialDataInterface::OpenDevice()
{
	if (IsOpen())
		return true;

	// Open for reading and writing via overlapped (async) functions

	_fileHandle = CreateFile(_comPortName.c_str(), GENERIC_READ | GENERIC_WRITE, FILE_SHARE_WRITE | FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_FLAG_OVERLAPPED, 0);
	if (_fileHandle == NULL)
	{
		return false;
	}

	// Setup prefered buffer sizes
    SetupComm(_fileHandle, MAX_SERIAL_RX_BUFFER, MAX_SERIAL_TX_BUFFER);

	// Set timeouts (Probably need tweaking!)
	COMMTIMEOUTS cto;
	GetCommTimeouts(_fileHandle, &cto);
	cto.ReadIntervalTimeout = MAXDWORD;
	cto.ReadTotalTimeoutConstant = 0;
	cto.ReadTotalTimeoutMultiplier = 0;
	cto.WriteTotalTimeoutConstant = 0;
	cto.WriteTotalTimeoutMultiplier = 0;
	if (!SetCommTimeouts(_fileHandle,&cto))
	{
		CloseHandle(_fileHandle);
		_fileHandle = NULL;
		return false;
	}
	
	// Set the serial port settings
	DCB dcb;
	dcb.DCBlength = sizeof(dcb);
	GetCommState(_fileHandle, &dcb);
	
	dcb.BaudRate = CBR_115200;
	dcb.fDtrControl = DTR_CONTROL_DISABLE;
	dcb.fRtsControl = RTS_CONTROL_DISABLE;
	dcb.fOutxCtsFlow = FALSE;
	dcb.fOutxDsrFlow = FALSE;
	dcb.fOutX = FALSE;
	dcb.fInX = FALSE;
	dcb.Parity = NOPARITY;
	dcb.StopBits = ONESTOPBIT;
	dcb.ByteSize = 8;

	if (!SetCommState(_fileHandle, &dcb))
	{
		CloseHandle(_fileHandle);
		_fileHandle = NULL;
		return false;
	}

	// Clear any data already on the serial port or waiting to be sent
	_writeBufferIndex = 0;
	_writeDataReadyEvent.Reset();
	
	PurgeComm(_fileHandle, PURGE_TXCLEAR | PURGE_RXCLEAR | PURGE_TXABORT | PURGE_RXABORT);

	return true;
}

// Close the device if open
bool USBSerialDataInterface::Close()
{
	kmk::Lock lock(_readCriticalSection);

	if (_fileHandle != NULL)
	{
		CloseHandle(_fileHandle);
		_fileHandle = NULL;
		return true;
	}

	return false;
}

// Start reading data on a seperate thread and pass all data through into the data processor
bool USBSerialDataInterface::BeginReading()
{
	kmk::Lock lock(_readCriticalSection);

	if (_readThreadRunning)
		return false;

	if (!OpenDevice())
		return false;

	_cancelIOEvent.Reset();
	_readThreadRunning = true;

	if (!_readThread.Start(ReadDataThread, this))
	{
		_readThreadRunning = false;
		Close();
		return false;
	}

	return true;
}

// Stop reading data from the device and kill the thread
bool USBSerialDataInterface::StopReading()
{
	{
		kmk::Lock lock(_readCriticalSection);

		if (!_readThreadRunning)
			return false;

		_readThreadRunning = false;
	}

	_cancelIOEvent.Signal();

	// Wait for the thread to end before continuing
	_readThread.WaitForTermination();
	return true;
}

// Get a configuration setting. The actual configuration response will be returned across the serial port
bool USBSerialDataInterface::GetConfigurationSetting(unsigned char *pReportdata, size_t dataLength)
{
	return SetConfigurationSetting(pReportdata, dataLength);
}

// Send a configuration setting / report data
bool USBSerialDataInterface::SetConfigurationSetting(unsigned char *pData, size_t dataLength)
{
	kmk::Lock lock(_writeCriticalSection);

	// Check for space in output buffer
	if (_writeBufferIndex + dataLength > _writeBuffer.size())
		return false;

	// Add to output buffer
	memcpy_s(&_writeBuffer[_writeBufferIndex], _writeBuffer.size() - _writeBufferIndex, pData, dataLength);
    _writeBufferIndex += (DWORD)dataLength;
	_writeDataReadyEvent.Signal();
	return true;
}

bool USBSerialDataInterface::SendDataBufferToDevice(OVERLAPPED &overlap)
{
	bool success = false;

	// Write the data
	DWORD bytesWritten = 0;
	overlap.InternalHigh = overlap.Internal = 0;
	WriteFile(_fileHandle, &_writeBuffer[0], _writeBufferIndex, NULL, &overlap);
	DWORD error = GetLastError();
	switch (error)
	{
	case ERROR_SUCCESS:
	case ERROR_IO_PENDING:
		success = true;
		break;

	default:
		success = false;
		break;
	}

	if (success)
	{
		// Make sure the write finishes before we continue
		if (!GetOverlappedResult(_fileHandle, &overlap, &bytesWritten, TRUE))
			success = false;
	}

	if (!success || bytesWritten != _writeBufferIndex)
	{
		RaiseError(ERROR_WRITE_FAILED, L"Write Data Error!");
	}

	_writeBufferIndex = 0;
	_writeDataReadyEvent.Reset();
	return success;
}

// Thread function for reading data from the device until stopped. Pass all data up via the DataReadyCallback
int USBSerialDataInterface::ReadDataThread(void *pArg)
{
	USBSerialDataInterface *pThis = (USBSerialDataInterface*)pArg;

#ifdef OUTPUT_RAW_DATA

	FILE *fp = fopen("data.dump", "a");

#endif

	try
	{	
		OVERLAPPED overlap = {0};
		overlap.hEvent = CreateEvent(NULL, TRUE, FALSE, NULL);

		// Device should already be open before the thread is started
		if (!pThis->IsOpen())
		{
			pThis->RaiseError(ERROR_DEVICE_OPEN_FAILED, L"Can not open device");
			return false;
		}

		// Allocate a memory buffer
        DWORD dataBufferSize = INPUT_BUFFER_LENGTH;
		std::vector<BYTE> dataBuffer;
		dataBuffer.resize(dataBufferSize);
		bool keepRunning = true;

		while(true)
		{
			bool success = false;
			{
				kmk::Lock lock(pThis->_readCriticalSection);
				keepRunning = pThis->_readThreadRunning;
			}

			if (!keepRunning)
				break;

			// Any data in the output buffer ready to send?
			{
				kmk::Lock lock(pThis->_writeCriticalSection);
				if (pThis->_writeBufferIndex != 0)
				{
					pThis->SendDataBufferToDevice(overlap);
				}
			}

			// Begin a new read operation
			success = false;
			DWORD readBytes = 0;
			overlap.InternalHigh = overlap.Internal = 0;

			ReadFile(pThis->_fileHandle, &dataBuffer[0], dataBufferSize, NULL, &overlap);
			DWORD error = GetLastError();
			switch (error)
			{
			case ERROR_SUCCESS:
				success = true;
				break;
			case ERROR_IO_PENDING:
				// Wait for the read response, cancel event or some data ready for writing
				{
					HANDLE pHandles[3] = { overlap.hEvent, pThis->_cancelIOEvent, pThis->_writeDataReadyEvent };
					DWORD waitResult = WaitForMultipleObjects(3, pHandles, FALSE, INFINITE);

					if (waitResult == WAIT_OBJECT_0) // ReadFile response
					{
						success = true;
					}
					else if (waitResult == WAIT_OBJECT_0 + 1) // Cancel event
					{
						// Cancel any pending IO
						CancelIo(pThis->_fileHandle);

						// Wait for the cancel to complete
						GetOverlappedResult(pThis->_fileHandle, &overlap, &readBytes, TRUE);
					}
					else if (waitResult == WAIT_OBJECT_0 + 2) // Write data ready
					{
						// Cancel the read request and allow it to complete in case some bytes are included
						CancelIo(pThis->_fileHandle);
						success = true;
					}
				}
				break;
			default:
				success = false;
				break;
			}

			// If the read request completed then report any bytes to the callback
			if (success)
			{
				if (GetOverlappedResult(pThis->_fileHandle, &overlap, &readBytes, TRUE))
				{
					// Have data?
					if (readBytes > 0)
					{
#ifdef OUTPUT_RAW_DATA
						fwrite(&dataBuffer[0], sizeof(char), readBytes, fp);
						fflush(fp);
#endif

						// Raise the data callback
						if (pThis->_dataReadyCallback != NULL)
						{
							(*pThis->_dataReadyCallback)(pThis->_dataReadyCallbackArg, &dataBuffer[0], readBytes);
						}
					}					
				}
			}
		}

#ifdef OUTPUT_RAW_DATA
		fclose(fp);
#endif

		// Clean up
		CloseHandle(overlap.hEvent);

		// Close the device once we have finished
		pThis->Close();
	}
	catch(std::exception ex)
	{
		pThis->RaiseError(ERROR_READ_FAILED, L"Unexpected error!");
	}
	
	return 0;
}

void USBSerialDataInterface::RaiseError(int errorCode, String message)
{
	if (_errorCallback != NULL)
	{
		(*_errorCallback)(_errorCallbackArg, errorCode, message);
	}
}

}
