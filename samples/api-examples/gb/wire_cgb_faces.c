#pragma bank 0
// Projected model faces erase a square opening; redraw its outline in green.
#include "wire_cgb_example.h"
#include "wire_cgb_plane.h"
void main() {
    u8 y;u8 bank;
    wire_results_clear();wire_plane_setup();Wire3DCGB_Init();wire_colors();Wire3DCGB_BeginFrame();
    Wire3DCGB_SetLineColor(1);
    for(y=8;y<=88;y++) Wire3DCGB_DrawLine2D(24,y,104,y);
    bank=sample_svbk;sample_svbk=2;
    Wire3DCGB_EraseModelFaces(&plane,0,0,64,0,0,0,256);
    sample_svbk=bank;
    Wire3DCGB_DrawModelColor(&plane,0,0,64,0,0,0,3);
    result[0]=Wire3DCGB_GetLineColor();
    Wire3DCGB_EndFrame();result[7]=0xA55A;
    while(1) {}
}
