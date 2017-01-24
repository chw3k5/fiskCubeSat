#pragma once

#include "DeviceBase.h"

namespace kmk
{

// GR1 / GR1A based detector
class GR1 : public DeviceBase
{
public:
	static const int VendorId = 0x4d8;
	static const int ProductId = 0x0;

	GR1(IDataInterface *pInterface);
	virtual ~GR1();

	virtual String GetProductName() const { return L"GR1"; }
	virtual int GetVendorID() const {return VendorId; }
	virtual int GetProductID() const {return ProductId; }

	DetectorType GetDetectorType() const { return DT_Gamma; }

	static void GetDetectorProperties(DetectorProperties &propsOut);

	String GetManufacturer() const { return L"Kromek"; }
	
};

// GR1 / GR1A based detector
class GR1A : public GR1
{
public:
	static const int VendorId = 0x4d8;
	static const int ProductId = 0x101;

	GR1A(IDataInterface *pInterface);
	virtual ~GR1A();

	virtual String GetProductName() const { return L"GR1A"; }
	virtual int GetVendorID() const {return VendorId; }
	virtual int GetProductID() const {return ProductId; }
	String GetManufacturer() const { return L"Kromek"; }
};

}
