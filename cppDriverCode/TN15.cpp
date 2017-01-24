#include "stdafx.h"
#include "TN15.h"
#include "IntervalCountProcessor.h"

#define EVENT_DEADTIME 5.813E-05
#define DEFAULT_LLD 250
#define DEFAULT_GAIN			0
#define DEFAULT_DIFF_GAIN		240
#define DEFAULT_HIGH_VOLTAGE	0
#define DEFAULT_WARMUP_TIME		60

namespace kmk
{

TN15::TN15(IDataInterface *pInterface)
: DeviceBase(pInterface, new IntervalCountProcessor(pInterface))
{
}

TN15::~TN15()
{
}

/*static*/ void TN15::GetDetectorProperties(DetectorProperties &props)
{
	props.detectorType = DT_Neutron;
	props.materialType = MT_CSI;
	props.materialWidth = 2.54;
	props.materialHeight = 2.54;
	props.materialDepth = 5.1;

	props.defaultDeadTime = EVENT_DEADTIME;
	props.defaultGain = DEFAULT_GAIN;
	props.defaultDiffGain = DEFAULT_DIFF_GAIN;
	props.defaultHighVoltage = DEFAULT_HIGH_VOLTAGE;
	props.defaultLLD = DEFAULT_LLD;
	props.defaultPolarity = NOT_USED;
}

// D3 component version of the TN15
TN15_D3::TN15_D3(IDataInterface *pInterface, IDataProcessor *pProcessor, unsigned char componentIndex)
: DeviceBase(pInterface, pProcessor, componentIndex)
{
}

TN15_D3::~TN15_D3()
{
}

/*static*/ void TN15_D3::GetDetectorProperties(DetectorProperties &props)
{
	props.detectorType = DT_Neutron;
	props.materialType = MT_CSI;
	props.materialWidth = 2.54;
	props.materialHeight = 2.54;
	props.materialDepth = 5.1;

	props.defaultDeadTime = EVENT_DEADTIME;
	props.defaultGain = DEFAULT_GAIN;
	props.defaultDiffGain = DEFAULT_DIFF_GAIN;
	props.defaultHighVoltage = DEFAULT_HIGH_VOLTAGE;
	props.defaultLLD = DEFAULT_LLD;
	props.defaultPolarity = NOT_USED;
}

// D3 component version of the TN15
TN15_D3S::TN15_D3S(IDataInterface *pInterface, IDataProcessor *pProcessor, unsigned char componentIndex)
	: DeviceBase(pInterface, pProcessor, componentIndex)
{
}

TN15_D3S::~TN15_D3S()
{
}

/*static*/ void TN15_D3S::GetDetectorProperties(DetectorProperties &props)
{
	props.detectorType = DT_Neutron;
	props.materialType = MT_CSI;
	props.materialWidth = 2.54;
	props.materialHeight = 2.54;
	props.materialDepth = 5.1;

	props.defaultDeadTime = EVENT_DEADTIME;
	props.defaultGain = DEFAULT_GAIN;
	props.defaultDiffGain = DEFAULT_DIFF_GAIN;
	props.defaultHighVoltage = DEFAULT_HIGH_VOLTAGE;
	props.defaultLLD = DEFAULT_LLD;
	props.defaultPolarity = NOT_USED;
}

}
