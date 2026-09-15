#pragma once
#pragma bank 0
// Setup shared by the CGB wireframe teaching examples. Compile the sample first
// and lib/wire3d_cgb.c second so the diagnostic window is reserved before globals.
#include "wire3d_cgb.h"
__location(0xC110) u16 result[8];
__location(0xFF40) u8 sample_lcdc;
__location(0xFF44) u8 sample_ly;
__location(0xFF70) u8 sample_svbk;

void wire_results_clear() {
    u8 i;
    for(i=0;i<8;i++) result[i]=0;
}

// The palette register requires an accessible window. Turn the LCD off at
// VBlank and restore its previous mode after installing black/red/blue/green.
void wire_colors() {
    u8 lcd;
    while(sample_ly>=144) {} while(sample_ly<144) {}
    lcd=sample_lcdc; sample_lcdc=0;
    Wire3DCGB_SetPaletteRGB15(0,31,31744,992);
    sample_lcdc=lcd;
}

// Four independent inclusive edges, useful for identifying old/new frame bounds.
void wire_frame(u8 x0,u8 y0,u8 x1,u8 y1,u8 color) {
    Wire3DCGB_DrawLineClipped2D(x0,y0,x1,y0,color);
    Wire3DCGB_DrawLineClipped2D(x1,y0,x1,y1,color);
    Wire3DCGB_DrawLineClipped2D(x1,y1,x0,y1,color);
    Wire3DCGB_DrawLineClipped2D(x0,y1,x0,y0,color);
}
