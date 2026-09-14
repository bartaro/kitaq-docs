#pragma once
// Color only the drawing region on CGB; DMG keeps its monochrome palette.
// Call while the LCD is off. Coordinates and dimensions are 8x8 map cells.
void vram_example_color(u8 x,u8 y,u8 width,u8 height,u8 palette) {
    u8 row;
    if (__cgb_is_cgb()) {
        __cgb_safe_set_vbk(1);
        row=0;
        while (row<height) {
            __vram_memset_unsafe(0x9800+((u16)y+row)*32+x,palette,width);
            row++;
        }
        __cgb_safe_set_vbk(0);
    }
}
