#pragma once

namespace kmk
{
	// Identifier structure used to detail which devices should be available to the driver
	struct ValidDeviceIdentifier
	{
		unsigned short productId;
		unsigned short vendorId;
	};
}