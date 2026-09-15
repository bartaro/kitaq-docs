#pragma bank 0
// A cleared 24-pixel strip and a palette-index-2 border have distinct purposes.
#include "wire_cgb_example.h"
void main() {
    u8 y;
    wire_results_clear(); Wire3DCGB_Init(); wire_colors(); Wire3DCGB_BeginFrame();
    Wire3DCGB_SetLineColor(1);
    for(y=0;y<96;y++) Wire3DCGB_DrawLine2D(0,y,31,y);
    Wire3DCGB_EraseLeftGuard24Fast();
    // With this example's palette, color index 2 is blue rather than white.
    Wire3DCGB_DrawWhiteBorderFast();
    Wire3DCGB_EndFrame(); result[7]=0xA55A;
    while(1) {}
}
