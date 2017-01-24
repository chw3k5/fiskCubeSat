#include "StdAfx.h"
#include "DeviceEnumeratorWindows.h"
#include "HIDDataInterfaceWindows.h"
#include "USBSerialDataInterfaceWindows.h"

#include <INITGUID.H>
#include <devguid.h>
#include <string>
#include <sstream>
// This file is in the Windows DDK available from Microsoft.
extern "C"
{
	#include "hidsdi.h"
	#include <setupapi.h>
	#include <dbt.h>
}

namespace kmk
{

DeviceEnumerator::DeviceEnumerator()
: _initialiseCompleteStatus(false)
, _wndHandle(NULL)
, _devicesChangedCallbackFunc(NULL)
, _devicesChangedCallbackArg(NULL)
{
}

DeviceEnumerator::~DeviceEnumerator()
{
}

bool DeviceEnumerator::Initialize(DevicesChangedCallbackFunc callbackFunc, void *pCallbackArg)
{
	_devicesChangedCallbackFunc = callbackFunc;
	_devicesChangedCallbackArg = pCallbackArg;

	if (!_processingThread.Start(ThreadProc, this))
	{
		return false;
	}

	// Wait for the window to be created
	_initialiseCompleteEvent.Wait(INFINITE);

	return _initialiseCompleteStatus;
}

void DeviceEnumerator::Shutdown()
{
	if (_wndHandle)
	{
	//	DestroyWindow(m_messageWindow);
		PostMessage(_wndHandle, WM_QUIT, 0, 0);
	}
	
	_processingThread.WaitForTermination();
	_wndHandle = NULL;

	
}

// Request to receive messages when a device is attached or removed.
// Also see WM_DEVICECHANGE in BEGIN_MESSAGE_MAP(CUsbhidiocDlg, CDialog).
void DeviceEnumerator::RegisterForDeviceNotifications()
{
	DEV_BROADCAST_DEVICEINTERFACE DevBroadcastDeviceInterface;
	HDEVNOTIFY DeviceNotificationHandle;

	//GUID hidGuid;
	//HidD_GetHidGuid(&hidGuid);

	DevBroadcastDeviceInterface.dbcc_size = sizeof(DevBroadcastDeviceInterface);
	DevBroadcastDeviceInterface.dbcc_devicetype = DBT_DEVTYP_DEVICEINTERFACE;
	//DevBroadcastDeviceInterface.dbcc_classguid = hidGuid;

	DeviceNotificationHandle = RegisterDeviceNotification(_wndHandle, &DevBroadcastDeviceInterface, DEVICE_NOTIFY_WINDOW_HANDLE | DEVICE_NOTIFY_ALL_INTERFACE_CLASSES);
}

// Enumerate any connected devices that match the deviceIdentifier details and append to the output list
void DeviceEnumerator::EnumerateDevices(const ValidDeviceIdentifier &deviceIdentifier, std::vector<IDataInterface*> &listOut)
{
	EnumerateUSBHIDDevices(deviceIdentifier, listOut);
	EnumerateUSBSerialDevices(deviceIdentifier, listOut);
}

void DeviceEnumerator::EnumerateUSBHIDDevices(const ValidDeviceIdentifier &deviceIdentifier, std::vector<IDataInterface*> &listOut)
{
	// Get a list of the HID devices that are present.
	GUID hidGuid;
	HidD_GetHidGuid(&hidGuid);

	HDEVINFO deviceInfoSet = SetupDiGetClassDevs(&hidGuid, NULL, NULL, DIGCF_DEVICEINTERFACE | DIGCF_PRESENT);
	SP_DEVICE_INTERFACE_DATA devIntData = {0};
	devIntData.cbSize = sizeof(SP_DEVICE_INTERFACE_DATA);

	// Loop through the list of devices and check the device attributes
	int deviceIndex = 0;
	while (SetupDiEnumDeviceInterfaces(deviceInfoSet, NULL, &hidGuid, deviceIndex, &devIntData))
	{
		// Detail data contains the device path
		// Determine the size of the detail data
		DWORD requiredSize = 0;
		SetupDiGetDeviceInterfaceDetail(deviceInfoSet, &devIntData, NULL, NULL, &requiredSize, NULL);
		
		// Allocate and retrive the device detail
		SP_DEVICE_INTERFACE_DETAIL_DATA *pDevIntDetailData = (SP_DEVICE_INTERFACE_DETAIL_DATA*)malloc(requiredSize);
		pDevIntDetailData->cbSize = sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA);

		if (!SetupDiGetDeviceInterfaceDetail(deviceInfoSet, &devIntData, pDevIntDetailData, requiredSize, NULL, NULL))
		{
			// Error getting details, skip device
			free(pDevIntDetailData);
			++deviceIndex;
			continue;
		}

		// Get the device path
		String devicePath = pDevIntDetailData->DevicePath;
		free(pDevIntDetailData);
		pDevIntDetailData = NULL;

		// Create the interface and check if it matches the product we are searching for
		HIDDataInterface *pInterface = new HIDDataInterface(devicePath);
		pInterface->Initialize();
		
		if (pInterface->GetProductID() == deviceIdentifier.productId && pInterface->GetVendorID() == deviceIdentifier.vendorId)
		{	// Keep
			listOut.push_back(pInterface);
		}
		else
		{	// Discard
			delete pInterface;
		}

		++deviceIndex;
	}
}

// Parse the vendor and product IDs from the given path
// This new function simply searches for VID_ and PID_ and converts the next 4 chars to a hex value
bool ParseHardwareID(wchar_t *pString, int &productIDOut, int &vendorIDOut)
{
	std::wstring str = pString;
	size_t pos = str.find(L"PID_");
	if (pos != std::wstring::npos && pos < str.length() - 7) // allow for PID_xxxx
	{
		std::wstringstream stream(str.substr(pos + 4, 4));
		stream >> std::hex >> productIDOut;
		pos = str.find(L"VID_");
		if (pos != std::wstring::npos && pos < str.length() - 7) // allow for VID_xxxx
		{
			std::wstringstream stream(str.substr(pos + 4, 4));
			stream >> std::hex >> vendorIDOut;
			return true;
		}
	}
	return false;
}


void DeviceEnumerator::EnumerateUSBSerialDevices(const ValidDeviceIdentifier &deviceIdentifier, std::vector<IDataInterface*> &listOut)
{
	// {FE900ED2-9EF1-4b20-BF6D-9646D0B99E41}
	/*static const GUID INTERFACE_GUID = { 0xfe900ed2, 0x9ef1, 0x4b20, { 0xbf, 0x6d, 0x96, 0x46, 0xd0, 0xb9, 0x9e, 0x41 } };
	GUID guid = INTERFACE_GUID;

	// Get a list of the HID devices that are present.
	HDEVINFO deviceInfoSet = SetupDiGetClassDevs(&guid, NULL, NULL, DIGCF_DEVICEINTERFACE | DIGCF_PRESENT);
	SP_DEVICE_INTERFACE_DATA devIntData = {0};
	devIntData.cbSize = sizeof(SP_DEVICE_INTERFACE_DATA);

	// Loop through the list of devices and check the device attributes
	int deviceIndex = 0;
	while (SetupDiEnumDeviceInterfaces(deviceInfoSet, NULL, &guid, deviceIndex, &devIntData))
	{
		// Detail data contains the device path
		// Determine the size of the detail data
		DWORD requiredSize = 0;
		SetupDiGetDeviceInterfaceDetail(deviceInfoSet, &devIntData, NULL, NULL, &requiredSize, NULL);
		
		// Allocate and retrive the device detail
		SP_DEVICE_INTERFACE_DETAIL_DATA *pDevIntDetailData = (SP_DEVICE_INTERFACE_DETAIL_DATA*)malloc(requiredSize);
		pDevIntDetailData->cbSize = sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA);

		if (!SetupDiGetDeviceInterfaceDetail(deviceInfoSet, &devIntData, pDevIntDetailData, requiredSize, NULL, NULL))
		{
			// Error getting details, skip device
			free(pDevIntDetailData);
			++deviceIndex;
			continue;
		}

		// Get the device path
		String devicePath = pDevIntDetailData->DevicePath;
		free(pDevIntDetailData);
		pDevIntDetailData = NULL;
	}*/

	GUID *pGuid = (GUID*)&GUID_DEVCLASS_PORTS;

	// Find all 'PORT' devices attached to the pc
	HDEVINFO deviceInfoSet = SetupDiGetClassDevs(pGuid, NULL, NULL, DIGCF_PRESENT);
	SP_DEVINFO_DATA devInfoData = {0};
	devInfoData.cbSize = sizeof(SP_DEVINFO_DATA);
	
	int DeviceIndex = 0;
	wchar_t buffer[500];
	DWORD Size = 500;
	
	// Enumerate over all ports
	while (SetupDiEnumDeviceInfo(deviceInfoSet, DeviceIndex, &devInfoData)) 
	{
		DeviceIndex++;

		// Open the registry entry for this device
		HKEY regKeyHandle = SetupDiOpenDevRegKey (deviceInfoSet, &devInfoData,DICS_FLAG_GLOBAL, 0,DIREG_DEV, KEY_READ );
		if (regKeyHandle == INVALID_HANDLE_VALUE)
			continue;

		// We need some way to identify the product and vendor id of this device, Symbolic name appears to be good for this
		Size = 500;
		//if (RegQueryValueEx(regKeyHandle, TEXT("SymbolicName"), NULL, NULL, (LPBYTE)buffer, &Size) != ERROR_SUCCESS)
		if (!SetupDiGetDeviceRegistryProperty(deviceInfoSet, &devInfoData, SPDRP_HARDWAREID, NULL, (LPBYTE)buffer, Size, NULL))
			continue;

		std::wstring devicePort(L"\\\\.\\");
		int productID, vendorID;
		if (!ParseHardwareID(buffer, productID, vendorID))
			continue;

		// Get the name of the com port
		Size = 500;
		if (RegQueryValueEx(regKeyHandle, TEXT("PortName"), NULL, NULL, (LPBYTE)buffer, &Size) != ERROR_SUCCESS)
			continue;

		devicePort += buffer;

		// Get the location of the device
		Size = 500;
		if (!SetupDiGetDeviceRegistryProperty(deviceInfoSet, &devInfoData, SPDRP_LOCATION_INFORMATION, NULL, (LPBYTE)buffer, Size, NULL))
			continue;

		std::wstring location(buffer);

		// Close the registry key as we no longer need it
		RegCloseKey(regKeyHandle);
		regKeyHandle = NULL;
	
		// Does this device match the type we are looking for?
		if (productID == deviceIdentifier.productId && vendorID == deviceIdentifier.vendorId)
		{
			// Yes - Add it
			USBSerialDataInterface *pInterface = new USBSerialDataInterface(devicePort, productID, vendorID, location);
			pInterface->Initialize();
			listOut.push_back(pInterface);
		}
	
	}
}

// Window procedure for the invisible message window (Required for detecting usb device changes in windows).
LRESULT CALLBACK DeviceEnumerator::DummyWndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
	static DeviceEnumerator *pThis = NULL;

	 switch(message)
	 {
	 case WM_CREATE:
		 {
			// Grab the param passed into the create window func
			CREATESTRUCT *pData = (CREATESTRUCT*)lParam;
			pThis = (DeviceEnumerator*)pData->lpCreateParams;
		 }
		 break;
	   case WM_CLOSE:
		 PostQuitMessage(0);
		 break;

	   case WM_DEVICECHANGE:
			// Raise usb device changed event
		{
			if (pThis != NULL)
			{
				// Raise the callback function 
				if (pThis->_devicesChangedCallbackFunc != NULL)
				{
					(*pThis->_devicesChangedCallbackFunc)(pThis->_devicesChangedCallbackArg);
				}
			}
			break;
		}

	   case WM_QUIT:
		   DestroyWindow(hWnd);
		   break;

	   default:
		 return DefWindowProc(hWnd, message, wParam, lParam);
	 }
	return 0;

}

int DeviceEnumerator::ThreadProc(void *pArg)
{
	DeviceEnumerator *pThis = (DeviceEnumerator*)pArg;

	// Create an invisible dummy window to receive notifications of device changes.
	WNDCLASSEX wc;
	memset(&wc, NULL, sizeof(WNDCLASSEX));
    wc.cbSize        = sizeof(WNDCLASSEX);
    wc.lpfnWndProc   = DummyWndProc;
    wc.hInstance     = GetModuleHandle(NULL);
    wc.lpszClassName = L"DummyWindow";
	RegisterClassEx(&wc);

	pThis->_wndHandle =  CreateWindowEx(NULL, L"DummyWindow", L"DummyWindow",0 , 0, 0,0, 0, HWND_MESSAGE, NULL, GetModuleHandle(NULL), pThis);	

	if (pThis->_wndHandle == NULL)
	{
		// Error, notify original thread
		pThis->_initialiseCompleteStatus = false;
		pThis->_initialiseCompleteEvent.Signal();
		return 0;
	}

	pThis->RegisterForDeviceNotifications();

	// Inform the original thread initialization is complete
	pThis->_initialiseCompleteStatus = true;
	pThis->_initialiseCompleteEvent.Signal();

	// Process messages until a quit message.
	MSG WndMsg;
	while (GetMessage(&WndMsg,NULL,0,0))
    {
	   TranslateMessage(&WndMsg);
	   DispatchMessage(&WndMsg);
    }

   return 0;
}



}
