// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
#ifndef FC_SPRITE0_SCENE_H
#define FC_SPRITE0_SCENE_H
#include "fc_common.h"
__location(0x0600) u8 s0_completed;
__prg_rom u8 s0_palette[16]={0x0F,0x21,0x16,0x30,0x0F,0x21,0x16,0x30,0x0F,0x21,0x16,0x30,0x0F,0x21,0x16,0x30};

void s0_prepare(void) {
    u8 x; u8 y;
    m_init(); __ppu_off(); __palette_bg_load(s0_palette);
    __palette_sp_load(s0_palette);
    // The CHR asset contains original solid tiles 240=blue, 241=red, 242=white.
    // The upper/lower bars have identical map coordinates before scrolling.
    for (y=6;y<26;y++) {
        __nametable_rect(8,y,4,1,240);
        __nametable_rect(20,y,4,1,241);
    }
    // A white horizontal band guarantees an opaque background at the marker.
    __nametable_rect(0,12,32,1,242);
    // OAM Y is one less than the visible coordinate. Behind-background priority
    // hides the marker while still allowing its opaque pixels to set the hit.
    __sprite_set(0,16,95,242,0x20); __oam_dma();
    __scroll_set(0,0); __ppu_ctrl_set(0x80); __ppu_mask_set(0x1E);
    m_text(1,1,"SPRITE ZERO / SCROLL SPLIT"); m_wait();
    m_text(1,3,"TOP: BLUE 64 / RED 160"); m_wait();
    s0_completed=0;
}

// Restore the top-of-screen scroll during VBlank, then let the caller wait
// for a fresh hit. NMI stays enabled; CPU IRQs are irrelevant to sprite hits.
void s0_frame(void) { m_wait(); }
#endif
