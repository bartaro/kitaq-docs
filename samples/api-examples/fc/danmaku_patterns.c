// Copyright (c) 2026 DAISUKE OBA. SPDX-License-Identifier: MIT
// Twenty yellow bullets demonstrate single spawns and an evenly spaced fan.
// The cyan diamond below them occupies reserved OAM slot zero as a player.
// This snapshot advances logic sixteen steps, then keeps the result on screen.
#include "danmaku.c"
__location(0x0600) u16 bullet_result[12];
__location(0x0200) u8 sample_shadow_oam[256];
__location(0x2002) u8 sample_ppu_status;
__prg_rom const u8 bullet_bitmap[8]={24,60,126,255,255,126,60,24};
__prg_rom const u8 bullet_palette[16]={
    15,40,40,40, 15,44,44,44, 15,40,40,40, 15,40,40,40
};
void main(void) {
    u8 i;
    __ppu_mask_set(0);__ppu_ctrl_set(0);
    __palette_bg_load(bullet_palette);__palette_sp_load(bullet_palette);
    __vram_fill(0,0,32);__ppu_addr(16);
    for(i=0;i<8;i++)__ppu_data(bullet_bitmap[i]);
    __oam_clear();
    // The player center is (112,192), outside both demonstration patterns.
    dm_player_x=112;dm_player_y=192;dm_invulnerable=0;
    danmaku_reset();
    // Clear removes bullets but retains the cumulative spawn counter.
    danmaku_spawn(48,180,0,0);
    danmaku_clear();bullet_result[0]=dm_count;bullet_result[1]=dm_spawned;
    danmaku_reset();bullet_result[2]=dm_spawned;

    // Q4.4 velocity 16 is one pixel per logic step. Four bullets move apart.
    danmaku_spawn(48,64,16,0);
    danmaku_spawn(48,64,0,16);
    danmaku_spawn(48,64,-16,0);
    danmaku_spawn(48,64,0,-16);
    // Sixteen directions, separated by two of the 32 angle steps, at 2 px/step.
    danmaku_fan(160,104,0,2,16,32);
    for(i=0;i<16;i++)danmaku_step();
    bullet_result[3]=dm_count;bullet_result[4]=dm_hit;bullet_result[5]=dm_graze;

    // Reserve slot zero. The library only writes the range requested below.
    __sprite_set(0,108,187,1,1);
    bullet_result[6]=danmaku_draw(1,8,1,0);
    // Record the first limited draw to demonstrate the rotating slot order.
    bullet_result[7]=sample_shadow_oam[7];bullet_result[8]=sample_shadow_oam[4];
    bullet_result[9]=danmaku_draw(1,24,1,0);
    bullet_result[10]=dm_spawned;
    // Upload the shadow OAM once in VBlank; logic and drawing never do DMA.
    while((sample_ppu_status&128)!=0) {}
    while((sample_ppu_status&128)==0) {}
    __oam_dma();__ppu_mask_set(0x14);
    bullet_result[11]=0xA55A;
    while(1) {}
}
