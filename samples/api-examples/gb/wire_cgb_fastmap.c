#pragma bank 0
// FastMap uses precomputed outline tiles rather than a pixel stage upload.
#include "wire_cgb_example.h"
void main() {
    u8 bank;
    wire_results_clear(); Wire3DCGB_InitFastMapLite(); wire_colors();
    bank=sample_svbk;sample_svbk=2;
    Wire3DCGB_FastMapBegin();
    Wire3DCGB_FastMapCell(1,1,1,15); // This first red square must disappear.
    Wire3DCGB_FastMapFlush();
    Wire3DCGB_FastMapBeginTilesOnly();
    Wire3DCGB_FastMapCell(13,1,1,1);
    Wire3DCGB_FastMapCell(13,1,1,4); // Same-color top and left sides combine.
    Wire3DCGB_FastMapRect(4,2,9,7,2,15);
    Wire3DCGB_FastMapCell(2,9,3,15);
    Wire3DCGB_FastMapFlushTilesOnly();
    sample_svbk=bank;result[7]=0xA55A;
    while(1) {}
}
