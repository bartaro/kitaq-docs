#pragma once
#include "fc_common.h"
__prg_rom u8 fc_oam_palette[16]={0x0F,0x16,0x2A,0x22,0x0F,0x16,0x2A,0x22,0x0F,0x16,0x2A,0x22,0x0F,0x16,0x2A,0x22};
// dx, dy, tile, attributes; a final dx=255 ends the stream.
__prg_rom u8 fc_oam_pair[9]={0,0,128,0,8,0,128,0x40,255};
u8 fc_oam_next;
void fc_oam_prepare() {
    m_init();__ppu_off();__palette_sp_load(fc_oam_palette);
    // example:__oam_clear:start
    __sprite_set(63,144,111,128,0); // Seed the CLEAR row with a visible entry.
    __oam_clear(); // Set every Y byte to 240; tile, attributes and X are retained.
    // example:__oam_clear:end
    // example:__sprite_set:start
    __sprite_set(0,144,15,128,0); // An 8x8 arrow at visible position (144,16).
    // example:__sprite_set:end
    __sprite_set(1,16,31,128,0);
    // example:__sprite_move:start
    __sprite_move(1,144,31); // Move to (144,32), retaining tile 128 and attributes 0.
    // example:__sprite_move:end
    __sprite_set(2,144,47,128,0);
    // example:__sprite_tile:start
    __sprite_tile(2,129); // Select the green square at (144,48).
    // example:__sprite_tile:end
    __sprite_set(3,144,63,128,0);
    // example:__sprite_attr:start
    __sprite_attr(3,0xC0); // Flip the arrow horizontally and vertically.
    // example:__sprite_attr:end
    __sprite_set(4,144,79,128,0);
    // example:__sprite_hide:start
    __sprite_hide(4); // The HIDE row remains empty after DMA.
    // example:__sprite_hide:end
    // example:__metasprite_draw:start
    fc_oam_next=__metasprite_draw(5,136,95,fc_oam_pair); // Returns 7 after two entries.
    // example:__metasprite_draw:end
    __sprite_set(7,144,127,128,0); // Transfer-source marker: an arrow in page 02.
}
void fc_oam_labels() {
    m_text(1,0,"FC OAM EXAMPLE");m_wait();
    m_text(24,0,"NEXT");m_wait();m_put(29,0,'0');m_put(30,0,(u8)('0'+fc_oam_next));m_wait();
    m_text(1,2,"SET");m_wait();m_text(1,4,"MOVE");m_wait();
    m_text(1,6,"TILE");m_wait();m_text(1,8,"ATTR");m_wait();
    m_text(1,10,"HIDE");m_wait();m_text(1,12,"META");m_wait();
    m_text(1,14,"CLEAR");m_wait();m_text(1,16,"TRANSFER");m_wait();
}
