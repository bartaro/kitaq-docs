#define MANUAL_SPRITE_FC
#include "fc_common.h"
#include "sprite.c"
#include "sprite_example_checks.h"
__prg_rom u8 sprite_example_palette[16]={0x0F,0x16,0x2A,0x22,0x0F,0x16,0x2A,0x22,0x0F,0x16,0x2A,0x22,0x0F,0x16,0x2A,0x22};
void main() {
    m_init();__ppu_off();
    __palette_sp_load(sprite_example_palette);
    sprite_example_draw();sprite_example_labels();
    // Rendering is stopped for this first immediate DMA transfer.
    sprite_flush_oam_now();
    __ppu_ctrl_set(0x80);__ppu_mask_set(0x1E);
    m_wait();
    while(1) { sprite_flush_oam(); }
}
