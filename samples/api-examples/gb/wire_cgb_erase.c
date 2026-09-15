#pragma bank 0
// Colored panels expose triangle, span, rectangle and packed-silhouette erasure.
#include "wire_cgb_example.h"
__prg_rom u8 silhouette[5]={0x73,0x74,0xFF,0x75,0x73};
void main() {
    u8 y;
    u8 bank;
    wire_results_clear(); Wire3DCGB_Init(); wire_colors(); Wire3DCGB_BeginFrame();
    for(y=8;y<=40;y++) Wire3DCGB_DrawLine2DColor(8,y,40,y,1);
    for(y=8;y<=40;y++) Wire3DCGB_DrawLine2DColor(48,y,80,y,2);
    for(y=64;y<=72;y++) Wire3DCGB_DrawLine2DColor(88,y,120,y,3);
    // The C triangle/rectangle clearers access the stage through the current
    // WRAM window. Select bank 2 around them and restore the caller's bank.
    bank=sample_svbk; sample_svbk=2;
    Wire3DCGB_EraseTriangle2D(12,12,36,12,12,36);
    Wire3DCGB_EraseSpan2D(36,40,24);
    Wire3DCGB_EraseRect2D(56,16,72,32);
    Wire3DCGB_ErasePackedSilhouette2D(silhouette,5,-2,104,68);
    sample_svbk=bank;
    Wire3DCGB_EndFrame(); result[7]=0xA55A;
    while(1) {}
}
