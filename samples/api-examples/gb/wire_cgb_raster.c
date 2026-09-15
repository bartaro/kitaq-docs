#pragma bank 0
// CGB raster paths: a red frame, blue diagonal, green marker and clipped line.
// Build this source together with lib/wire3d_cgb.c in an MBC5 256 KB CGB ROM.
#include "wire3d_cgb.h"
__location(0xFF40) u8 sample_lcdc;
__location(0xFF44) u8 sample_ly;
__location(0xFF4D) u8 sample_key1;
__location(0xC110) u16 result[8];
__prg_rom u8 lower_lines[8]={80,56,112,56,112,56,112,80};

void main() {
    u8 i;
    for(i=0;i<8;i++) result[i]=0;
    Wire3DCGB_EnableDoubleSpeed();
    Wire3DCGB_Init(); // Already at double speed: its internal request is a no-op.
    result[2]=(u8)(sample_key1&128);
    // Palette writes are performed with the LCD off, after entering VBlank.
    while(sample_ly>=144) {} while(sample_ly<144) {}
    sample_lcdc=0;
    Wire3DCGB_SetPaletteRGB15(WIRE3DCGB_RGB15(0,0,0),WIRE3DCGB_RGB15(31,0,0),WIRE3DCGB_RGB15(0,0,31),WIRE3DCGB_RGB15(0,31,0));
    sample_lcdc=0x81;
    Wire3DCGB_SetScreenOffset(0,0);
    Wire3DCGB_SetCamera(0,0,0,0,0,0);
    Wire3DCGB_BeginFrame();
    Wire3DCGB_SetLineColor(1);
    Wire3DCGB_DrawLine2D(8,8,56,8);
    Wire3DCGB_DrawLine2D(56,8,56,40);
    Wire3DCGB_DrawLine2D(56,40,8,40);
    Wire3DCGB_DrawLine2D(8,40,8,8);
    Wire3DCGB_DrawLine2DColor(8,40,56,8,2);
    result[0]=Wire3DCGB_GetLineColor(); // Temporary blue restores red.
    Wire3DCGB_SetLineColor(3);
    Wire3DCGB_DrawPoint2D(64,48);
    Wire3DCGB_DrawLineClipped2D(-10,72,140,72,3);
    Wire3DCGB_DrawLineList2DColor(lower_lines,2,2);
    result[1]=Wire3DCGB_GetLineColor(); // The blue line list restores green.
    Wire3DCGB_PutBgTile(18,1,0x80); // Queue the supplied zero glyph outside the viewport.
    Wire3DCGB_EndFrame();
    result[7]=0xA55A;
    while(1) {}
}
