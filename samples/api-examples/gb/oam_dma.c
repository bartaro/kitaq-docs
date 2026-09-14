#pragma fixed_bank 0
#include "gb_tile_example.h"
#include "sprite_example_tiles.h"
void __oam_dma(u16 src_ptr);
// DMA takes the page address: reserve all 160 bytes at a 256-byte boundary.
__location(0xC400) u8 raw_oam[160];
__location(0xFF6A) u8 demo_obj_index;
__location(0xFF6B) u8 demo_obj_data;
void main() {
    u8 i;
    __asm { DI }
    tile_example_begin();M_LCDC=0x13;
    __vram_copy(0x8800,sprite_example_tiles,32);
    if(__cgb_is_cgb()) {
        demo_obj_index=0x80;
        // Transparent, red, green and blue in CGB object palette 0.
        demo_obj_data=0;demo_obj_data=0;
        demo_obj_data=31;demo_obj_data=0;
        demo_obj_data=0xE0;demo_obj_data=3;
        demo_obj_data=0;demo_obj_data=0x7C;
    }
    // Y=0 hides all unused slots. Each slot is Y, X, tile number, attributes.
    for(i=0;i<160;i++)raw_oam[i]=0;
    // Hardware positions include an X offset of 8 and a Y offset of 16.
    raw_oam[0]=48;raw_oam[1]=96;raw_oam[2]=128;raw_oam[3]=0;
    raw_oam[4]=72;raw_oam[5]=96;raw_oam[6]=128;raw_oam[7]=0x20;
    raw_oam[8]=96;raw_oam[9]=96;raw_oam[10]=129;raw_oam[11]=0;
    m_text(1,0,"OAM DMA");m_text(1,4,"NORMAL");
    m_text(1,7,"FLIP X");m_text(1,10,"SQUARE");
    // The LCD is off for this initial copy. The intrinsic waits for completion.
    __oam_dma((u16)raw_oam);M_LCDC=0x93;
    while(1) {
        // Transfer at VBlank so sprite evaluation never sees a partially copied page.
        m_wait();__oam_dma((u16)raw_oam);
    }
}
