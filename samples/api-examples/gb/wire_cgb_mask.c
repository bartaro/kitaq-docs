#pragma bank 0
// Red/blue scanlines stop inside masks; green outlines identify the triangle.
#include "wire_cgb_example.h"
__prg_rom u8 silhouette[5]={0x73,0x74,0xFF,0x75,0x73};
void main() {
    u8 y;
    wire_results_clear(); Wire3DCGB_Init(); wire_colors(); Wire3DCGB_BeginFrame();
    // Clearing this first test mask must leave the upper-left scanline intact.
    Wire3DCGB_MarkTriangle2D(8,8,16,8,8,16);
    Wire3DCGB_ClearOcclusionMask();
    Wire3DCGB_MarkTriangle2D(32,16,64,16,32,48);
    Wire3DCGB_MarkPackedSilhouette2D(silhouette,5,-2,104,32);
    Wire3DCGB_SetOcclusionActive(1);
    for(y=8;y<=56;y=y+4) Wire3DCGB_DrawLine2DColor(8,y,88,y,1);
    for(y=28;y<=36;y++) Wire3DCGB_DrawLine2DColor(92,y,120,y,2);
    Wire3DCGB_SetOcclusionActive(0);
    Wire3DCGB_DrawLine2DColor(32,16,64,16,3);
    Wire3DCGB_DrawLine2DColor(64,16,32,48,3);
    Wire3DCGB_DrawLine2DColor(32,48,32,16,3);
    Wire3DCGB_EndFrame(); result[7]=0xA55A;
    while(1) {}
}
