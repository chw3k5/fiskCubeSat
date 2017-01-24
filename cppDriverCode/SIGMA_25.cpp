#include "stdafx.h"
#include "SIGMA_25.h"
#include "IntervalCountProcessor.h"

#define EVENT_DEADTIME 5.813E-05
#define DEFAULT_LLD 80
#define DEFAULT_GAIN			0
#define DEFAULT_DIFF_GAIN		240
#define DEFAULT_HIGH_VOLTAGE	0
#define DEFAULT_WARMUP_TIME		60

namespace kmk
{

SIGMA_25::SIGMA_25(IDataInterface *pInterface)
: DeviceBase(pInterface, new IntervalCountProcessor(pInterface))
{
}

SIGMA_25::~SIGMA_25(void)
{
}

/*static*/ void SIGMA_25::GetDetectorProperties(DetectorProperties &props)
{
	props.detectorType = DT_Gamma;
	props.materialType = MT_CSI;
	props.materialWidth = 2.54;
	props.materialHeight = 2.54;
	props.materialDepth = 2.54;

	props.defaultDeadTime = EVENT_DEADTIME;
	props.defaultGain = DEFAULT_GAIN;
	props.defaultDiffGain = DEFAULT_DIFF_GAIN;
	props.defaultHighVoltage = DEFAULT_HIGH_VOLTAGE;
	props.defaultLLD = DEFAULT_LLD;
	props.defaultPolarity = NOT_USED;
}


SIGMA_25_D3::SIGMA_25_D3(IDataInterface *pInterface, IDataProcessor *pProcessor, unsigned char componentIndex)
: DeviceBase(pInterface, pProcessor, componentIndex)
{
}

SIGMA_25_D3::~SIGMA_25_D3()
{
}

/*static*/ void SIGMA_25_D3::GetDetectorProperties(DetectorProperties &props)
{
	props.detectorType = DT_Gamma;
	props.materialType = MT_CSI;
	props.materialWidth = 2.54;
	props.materialHeight = 2.54;
	props.materialDepth = 2.54;

	props.defaultDeadTime = EVENT_DEADTIME;
	props.defaultGain = DEFAULT_GAIN;
	props.defaultDiffGain = DEFAULT_DIFF_GAIN;
	props.defaultHighVoltage = DEFAULT_HIGH_VOLTAGE;
	props.defaultLLD = DEFAULT_LLD;
	props.defaultPolarity = NOT_USED;
}


SIGMA_25_D3S::SIGMA_25_D3S(IDataInterface *pInterface, IDataProcessor *pProcessor, unsigned char componentIndex)
	: DeviceBase(pInterface, pProcessor, componentIndex)
{
}

SIGMA_25_D3S::~SIGMA_25_D3S()
{
}

/*static*/ void SIGMA_25_D3S::GetDetectorProperties(DetectorProperties &props)
{
	props.detectorType = DT_Gamma;
	props.materialType = MT_CSI;
	props.materialWidth = 2.54;
	props.materialHeight = 2.54;
	props.materialDepth = 2.54;

	props.defaultDeadTime = EVENT_DEADTIME;
	props.defaultGain = DEFAULT_GAIN;
	props.defaultDiffGain = DEFAULT_DIFF_GAIN;
	props.defaultHighVoltage = DEFAULT_HIGH_VOLTAGE;
	props.defaultLLD = DEFAULT_LLD;
	props.defaultPolarity = NOT_USED;
}
}
