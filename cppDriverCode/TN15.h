#pragma once

#include "IDataInterface.h"
#include "DeviceBase.h"

namespace kmk
{

class TN15 : public DeviceBase
{
public:
	static const int VendorId = 0x4d8;
	static const int ProductId = 0x30;
	
	TN15(IDataInterface *pInterface);
	virtual ~TN15(void);

	virtual String GetProductName() const { return L"TN15"; }
	virtual int GetVendorID() const {return VendorId; }
	virtual int GetProductID() const {return ProductId; }
	String GetManufacturer() const { return L"Kromek"; }

	DetectorType GetDetectorType() const { return DT_Neutron; }
	
	static void GetDetectorProperties(DetectorProperties &props);
};

// Multi component version of the TN15 (D3)
class TN15_D3 : public DeviceBase
{
public:
	static const int VendorId = 0x4d8;
	static const int ProductId = 0x31;
	
	TN15_D3(IDataInterface *pInterface, IDataProcessor *pProcessor, unsigned char componentIndex);
	virtual ~TN15_D3(void);

	virtual String GetProductName() const { return L"D3 Neutron"; }
	virtual int GetVendorID() const {return VendorId; }
	virtual int GetProductID() const {return ProductId; }
	String GetManufacturer() const { return L"Kromek"; }

	DetectorType GetDetectorType() const { return DT_Neutron; }

	static void GetDetectorProperties(DetectorProperties &props);
};

// Multi component version of the TN15 (D3S)
class TN15_D3S : public DeviceBase
{
public:
	static const int VendorId = 0x4d8;
	static const int ProductId = 0x32;

	TN15_D3S(IDataInterface *pInterface, IDataProcessor *pProcessor, unsigned char componentIndex);
	virtual ~TN15_D3S(void);

	virtual String GetProductName() const { return L"D3 Neutron"; }
	virtual int GetVendorID() const { return VendorId; }
	virtual int GetProductID() const { return ProductId; }
	String GetManufacturer() const { return L"Kromek"; }

	DetectorType GetDetectorType() const { return DT_Neutron; }

	static void GetDetectorProperties(DetectorProperties &props);
};


}
