#pragma bank 0
// An invalid coordinate latches the frame fault; BeginFrame resets it.
#include "wire_cgb_example.h"
u8* tile_payload;
void main() {
    wire_results_clear(); Wire3DCGB_InitFullScreen(); wire_colors();
    Wire3DCGB_BeginFrame(); Wire3DCGB_DrawPoint2D(160,0);
    result[0]=Wire3DCGB_GetFullScreenOverflow();
    Wire3DCGB_DrawPoint2D(8,8); result[1]=Wire3DCGB_GetFullScreenTileCount();
    // Allocation precedes the fault test, but the pixel write is suppressed.
    tile_payload=(u8*)0xD500;result[4]=*tile_payload;
    Wire3DCGB_BeginFrame();result[2]=Wire3DCGB_GetFullScreenOverflow();
    Wire3DCGB_SetLineColor(0); Wire3DCGB_DrawPoint2D(159,143);
    result[3]=Wire3DCGB_GetFullScreenTileCount();
    Wire3DCGB_EndFrame();result[7]=0xA55A;while(1){}
}
