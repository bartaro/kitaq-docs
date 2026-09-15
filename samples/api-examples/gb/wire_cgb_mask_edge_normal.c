#pragma bank 0
// A right-edge triangle must not wrap its one-pixel guard to the left edge.
#include "wire_cgb_example.h"
void main() {
    u8 y;
    wire_results_clear(); Wire3DCGB_Init(); wire_colors();
    Wire3DCGB_BeginFrame(); Wire3DCGB_ClearOcclusionMask();
    Wire3DCGB_MarkTriangle2D(119,16,127,16,127,24);
    Wire3DCGB_SetOcclusionActive(1);
    for(y=16;y<=24;y++) Wire3DCGB_DrawLine2DColor(0,y,127,y,1);
    Wire3DCGB_SetOcclusionActive(0);
    Wire3DCGB_DrawLine2DColor(127,32,127,95,2);
    Wire3DCGB_EndFrame(); result[7]=0xA55A; while(1) {}
}
