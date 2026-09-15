#pragma bank 0
// Replace a nearly full tile list with a blue border; every old red point disappears.
#include "wire_cgb_example.h"
void main() {
    u8 i;
    wire_results_clear(); Wire3DCGB_InitFullScreen(); wire_colors();
    Wire3DCGB_BeginFrame(); Wire3DCGB_SetLineColor(1);
    for(i=0;i<127;i++) Wire3DCGB_DrawPoint2D((i%20)*8+4,(i/20)*8+4);
    result[0]=Wire3DCGB_GetFullScreenTileCount();
    result[1]=Wire3DCGB_GetFullScreenOverflow();
    Wire3DCGB_EndFrame();
    Wire3DCGB_BeginFrame();
    // Reversed endpoints also exercise leftward and upward tile crossings.
    wire_frame(159,143,0,0,2);
    result[2]=Wire3DCGB_GetFullScreenTileCount();
    result[3]=Wire3DCGB_GetFullScreenOverflow();
    Wire3DCGB_EndFrame(); result[7]=0xA55A;
    while(1) {}
}
