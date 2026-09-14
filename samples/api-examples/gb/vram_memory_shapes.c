// Compare immediate VRAM copies and fills, including computed transfer lengths.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
const u8 shape_patterns[48]={255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,128,128,192,192,224,224,240,240,248,248,252,252,254,254,255,255};
u8 strip[3];
u16 length_base;
u16 length_extra;
u8 failures;
u8 row;
u8 column;
u8* map;
u16 computed_length() {
    return length_base+length_extra;
}
// The caller supplies a byte offset within the 32x32 map while the LCD is off.
u8 map_byte(u16 offset) {
    return *(map+offset);
}
void main() {
    tile_example_begin();
    M_LCDC=0;
    __vram_copy(0x8010,shape_patterns,48);
    row=2;
    while (row<=10) {
        vram_example_color(2,row,3,1,(u8)((row-2)%3+1));
        row++;
    }
    vram_example_color(2,11,1,1,1);
    vram_example_color(2,12,1,1,2);
    vram_example_color(4,12,1,1,3);
    strip[0]=1; strip[1]=2; strip[2]=3;
    length_base=2;
    length_extra=1;
    failures=0;
    map=(u8*)0x9800;
    // example:__vram_memcpy:start
    __vram_memcpy(0x9842,strip,length_base+length_extra); // Three map bytes at tile (2,2).
    // example:__vram_memcpy:end
    // example:__vram_copy:start
    __vram_copy(0x9862,strip,3); // The copy alias uses the same CPU transfer.
    // example:__vram_copy:end
    // example:__vram_copy_hblank:start
    __vram_copy_hblank(0x9882,strip,3); // Immediate safe copy; no scheduled HBlank DMA.
    // example:__vram_copy_hblank:end
    // example:__vram_copy_dma:start
    __vram_copy_dma(0x98A2,strip,3); // This alias also uses CPU writes, not a DMA engine.
    // example:__vram_copy_dma:end
    // example:__vram_memcpy_unsafe:start
    // The LCD is off throughout these unchecked writes.
    __vram_memcpy_unsafe(0x98C2,strip,computed_length());
    // example:__vram_memcpy_unsafe:end
    // example:__vram_memset:start
    __vram_memset(0x98E2,1,length_base+length_extra); // Three solid tiles, not three tile patterns.
    // example:__vram_memset:end
    // example:__vram_fill:start
    __vram_fill(0x9902,1,computed_length());
    // example:__vram_fill:end
    // example:__fill_tilemap:start
    __fill_tilemap(0x9922,1,length_base+length_extra); // Explicit address and byte count, not a whole-map clear.
    // example:__fill_tilemap:end
    // example:__vram_memset_unsafe:start
    __vram_memset_unsafe(0x9942,1,computed_length()); // Safe here because the LCD is off.
    // example:__vram_memset_unsafe:end
    row=2;
    while (row<=10) {
        column=0;
        while (column<3) {
            if (row<=6) {
                if (map_byte((u16)row*32+2+column)!=strip[(__safe_index u8)column]) failures++;
            } else {
                if (map_byte((u16)row*32+2+column)!=1) failures++;
            }
            column++;
        }
        if (map_byte((u16)row*32+1)!=0 || map_byte((u16)row*32+5)!=0) failures++;
        row++;
    }
    // Zero counts must leave the sentinel unchanged.
    *(map+11*32+2)=1;
    __vram_memcpy(0x9962,strip,0);
    __vram_memset(0x9962,0,0);
    __vram_memcpy_unsafe(0x9962,strip,0);
    __vram_memset_unsafe(0x9962,0,0);
    if (map_byte(11*32+2)!=1) failures++;
    M_LCDC=0x91;
    // These safe writes exercise the LCD-on path; the unsafe variants are never used here.
    __vram_memcpy(0x9982,strip,1);
    __vram_memset(0x9984,1,1);
    m_text(1,0,"VRAM MEMORY SHAPES");
    m_text(7,2,"MEMCPY");
    m_text(7,3,"COPY");
    m_text(7,4,"HBLANK");
    m_text(7,5,"DMA");
    m_text(7,6,"COPY UNSAFE");
    m_text(7,7,"MEMSET");
    m_text(7,8,"FILL");
    m_text(7,9,"FILL TILEMAP");
    m_text(7,10,"FILL UNSAFE");
    m_text(7,11,"ZERO COUNT");
    m_text(7,12,"LCD ON");
    m_text(1,15,"FAILED CHECKS");
    m_put(16,15,(u8)('0'+failures/100));
    m_put(17,15,(u8)('0'+(failures/10)%10));
    m_put(18,15,(u8)('0'+failures%10));
    while (1) m_wait();
}
