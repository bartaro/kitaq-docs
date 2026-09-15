#pragma bank 0
// A large frame demonstrates the 160x144 renderer and its allocated-tile count.
#include "wire_cgb_example.h"
void main() {
    wire_results_clear();
    Wire3DCGB_InitFullScreen(); wire_colors();
    Wire3DCGB_BeginFrame();
    Wire3DCGB_SetLineColor(1);
    Wire3DCGB_DrawLine2D(8,8,151,8);
    Wire3DCGB_DrawLine2D(8,8,8,135);
    Wire3DCGB_DrawLine2DColor(8,135,151,135,2);
    Wire3DCGB_DrawLine2DColor(151,8,151,135,3);
    result[0]=Wire3DCGB_GetFullScreenTileCount();
    result[1]=Wire3DCGB_GetFullScreenOverflow();
    Wire3DCGB_EndFrameFast();
    result[7]=0xA55A;
    while(1) {}
}
