#pragma fixed_bank 0
#include "gb_tile_example.h"
#include "sprite.c"
#include "sprite_example_tiles.h"
#include "sprite_example_checks.h"
__location(0xFF6A) u8 sprite_example_obj_index;
__location(0xFF6B) u8 sprite_example_obj_data;
void main() {
    u8 i;
    tile_example_begin();M_LCDC=0x13;
    __vram_copy(0x8800,sprite_example_tiles,32);
    if(__cgb_is_cgb()) {
        sprite_example_obj_index=0x80;
        for(i=0;i<8;i++) {
            sprite_example_obj_data=0;sprite_example_obj_data=0;
            sprite_example_obj_data=31;sprite_example_obj_data=0;
            sprite_example_obj_data=0xE0;sprite_example_obj_data=3;
            sprite_example_obj_data=0;sprite_example_obj_data=0x7C;
        }
    }
    sprite_example_draw();sprite_example_labels();
    // Rendering is stopped for this first immediate DMA transfer.
    sprite_flush_oam_now();M_LCDC=0x93;
    while(1) { sprite_flush_oam(); }
}
