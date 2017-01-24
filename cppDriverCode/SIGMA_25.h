#pragma once

#include "DeviceBase.h"

namespace kmk
{

class SIGMA_25 : public DeviceBase
{
public:
	static const int VendorId = 0x4d8;
	static const int ProductId = 0x022;

	SIGMA_25(IDataInterface *pInterface);
	virtual ~SIGMA_25();

	virtual String GetProductName() const { return L"SIGMA 25"; }
	virtual int GetVendorID() const {return VendorId; }
	virtual int GetProductID() const {return ProductId; }
	String GetManufacturer() const { return L"Kromek"; }

	DetectorType GetDetectorType() const { return DT_Gamma; }
	
	static void GetDetectorProperties(DetectorProperties &props);
};

// Multi component version of the sigma 25 (D3)
class SIGMA_25_D3 : public DeviceBase
{
public:
	static const int VendorId = 0x4d8;
	static const int ProductId = 0x024;

	SIGMA_25_D3(IDataInterface *pInterface, IDataProcessor *pProcessor, unsigned char componentIndex);
	virtual ~SIGMA_25_D3();

	virtual String GetProductName() const { return L"D3 Gamma"; }
	virtual int GetVendorID() const {return VendorId; }
	virtual int GetProductID() const {return ProductId; }
	String GetManufacturer() const { return L"Kromek"; }

	DetectorType GetDetectorType() const { return DT_Gamma; }

	static void GetDetectorProperties(DetectorProperties &props);
};

// Multi component version of the sigma 25 (D3S)
class SIGMA_25_D3S : public DeviceBase
{
public:
	static const int VendorId = 0x4d8;
	static const int ProductId = 0x025;
	static const int D3SProductId = 0x01D3;

	SIGMA_25_D3S(IDataInterface *pInterface, IDataProcessor *pProcessor, unsigned char componentIndex);
	virtual ~SIGMA_25_D3S();

	virtual String GetProductName() const { return L"D3S Gamma"; }
	virtual int GetVendorID() const { return VendorId; }
	virtual int GetProductID() const { return ProductId; }
	String GetManufacturer() const { return L"Kromek"; }

	DetectorType GetDetectorType() const { return DT_Gamma; }

	static void GetDetectorProperties(DetectorProperties &props);
};

}
