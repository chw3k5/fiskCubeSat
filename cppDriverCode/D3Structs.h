#pragma once

namespace kmk
{
// Commands
const int REPORT_ID_SET_GAIN			= 0x02;
const int REPORT_ID_SET_BIAS			= 0x07;
const int REPORT_ID_SET_SERIAL_NO		= 0x08;
const int REPORT_ID_SET_LLD				= 0x09;
const int REPORT_ID_SET_OTG				= 0x46;
const int REPORT_ID_SET_DFU				= 0x47;
// Requests
const int REPORT_ID_GET_GAIN			= 0x82;
const int REPORT_ID_GET_BIAS			= 0x87;
const int REPORT_ID_GET_SERIAL_NO		= 0x88;
const int REPORT_ID_GET_LLD				= 0x89;
const int REPORT_ID_INTERNAL_ERROR		= 0xc0;
const int REPORT_ID_GET_16BIT_SPECTRUM	= 0xc1;
const int REPORT_ID_D3_START			= 0xc4;
const int REPORT_ID_GET_STATUS			= 0xc5;
const int REPORT_ID_GET_OTG				= 0xc6;

#pragma pack (push, 1)

// Header structure that starts all content in messages from and to the device
struct ContentHeader
{
	uint8_t componentID;
	uint8_t reportID;
};

// Header structure that starts all messages from and to a multi detector device
struct MessageHeader
{
	uint16_t messageSize;
	uint8_t sequence;
	ContentHeader contentHeader;
};

// A basic template for configuration requests. A report that contains only a reportID
struct D3BasicRequestHeader
{
	uint16_t messageSize;
	uint8_t sequence;
	uint8_t componentID;
	uint8_t reportID;
	uint16_t crc;
};

struct D3StartResponseHeader
{
	// Report id
	const static int REPORT_ID = 0xc4;

	MessageHeader header;
	uint16_t version;
  	char serial[50];
	uint16_t crc;
};

// Main spectrum data returned in this structure
struct D3Spectrum16ResponseHeader
{
	const static int REPORT_ID = 0xc1;
	static const int SPECTRUM_SIZE = 4096;
  	
	MessageHeader m_message;
  	uint32_t realTimeMS;
	uint16_t neutronCounts;
	uint16_t gammaSpectrum[SPECTRUM_SIZE];
	uint16_t crc;
};

// Error message returned from the D3
struct D3InternalErrorMessage
{
	const static int REPORT_ID = 0xc0;
	static const int BUFFER_SIZE = 50;

  	MessageHeader m_message;
	uint8_t m_errorId;
  	char m_errorText[BUFFER_SIZE];
	uint16_t m_crc;
};

// Get configuration request struct
struct D3GetConfiguration
{
	MessageHeader m_message;
	uint16_t m_crc;
};

// 16 bit configuration setting
struct D3Configuration16
{
	const static int REPORT_ID_SET_BIAS = 0x07;
	const static int REPORT_ID_SET_LLD = 0x09;
	const static int REPORT_ID_GET_BIAS = 0x87;
	const static int REPORT_ID_GET_LLD = 0x89;
	const static int REPORT_ID_GET_VERSION = 0x8a;

	MessageHeader m_message;
	uint16_t data;
	uint16_t m_crc;
};

// 8 but configuration setting
struct D3Configuration8
{
	const static int REPORT_ID_SET_GAIN = 0x02;
	const static int REPORT_ID_SET_OTG = 0x46;
	const static int REPORT_ID_GET_GAIN = 0x82;
	const static int REPORT_ID_GET_OTG = 0xc6;

	MessageHeader m_message;
	uint8_t data;
	uint16_t m_crc;
};

// Report returned when requesting the serial number
struct D3ConfigurationSerial
{
	const static int REPORT_ID_GET_SERIAL = 0x88;
	static const int BUFFER_SIZE = 50;

	MessageHeader m_message;
	char data[BUFFER_SIZE];
	uint16_t m_crc;
};

#pragma pack (pop)

}