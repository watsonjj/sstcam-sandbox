#include <stdio.h>
#include <stdint.h>
#include <iostream>

typedef struct dataPacket {
	uint16_t nWaveforms:7;
	uint16_t ZS_en:1;
	uint16_t lastSub:1;
	uint16_t firstSub:1;
	uint16_t nGroup:6;
	uint16_t tack0:16;
	uint16_t ctaID:8;
	uint16_t detectorID:8;
	uint16_t eventSeq:8;
	uint16_t detectorTag:8;
	uint16_t tack1:16;
	uint16_t tack2:16;
	uint16_t tack3:16;
	uint16_t column:6;
	uint16_t stale:1;
	uint16_t zeroSupressed:1;
	uint16_t bp:5;
	uint16_t row:3;
} dataPacket;

int main() 
{ 
	uint16_t n = 16;
	uint8_t dataA[] = {32,  34,  72,  96, 0, 0, 236, 160, 62, 208, 1, 248, 0, 0, 5, 168};
	uint8_t* data = &dataA[0];

	uint16_t nWaveforms = data[0] & 0x7F;
	uint16_t column = data[14] & 0x3F;
	uint16_t row = (data[15] >> 5) & 0x7;
	uint16_t bp = data[15] & 0x1F;
	// for (int i=0; i<n; i++) {
		// std::cout << uint16_t(data[i]) << std::endl;
	// }
	// std::cout << sizeof(dataA) << std::endl;

	dataPacket* b = (dataPacket*)data;
	std::cout << nWaveforms << " " << b->nWaveforms << std::endl;
	std::cout << column << " " << b->column << std::endl;
	std::cout << row << " " << b->row << std::endl;
	std::cout << bp << " " << b->bp << std::endl;
	// dataPacket dp;
	// dataPacket* dp = static_cast<dataPacket*>(data);
    // memcpy(&data, dp, sizeof(data));
}
