#pragma bank 0
// One point per tile exposes the 127-tile limit without relying on text alone.
#include "wire_cgb_example.h"
void main() {
    u8 i;
    wire_results_clear();
    Wire3DCGB_InitFullScreen(); wire_colors();
    Wire3DCGB_BeginFrame(); Wire3DCGB_SetLineColor(3);
    for(i=0;i<128;i++) Wire3DCGB_DrawPoint2D((i%20)*8+4,(i/20)*8+4);
    result[0]=Wire3DCGB_GetFullScreenTileCount();
    result[1]=Wire3DCGB_GetFullScreenOverflow();
    Wire3DCGB_EndFrame();
    result[7]=0xA55A;
    while(1) {}
}
