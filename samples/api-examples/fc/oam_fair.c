#pragma fixed_bank 0
#include "fc_common.h"
#include "oam_fair_impl.h"
__prg_rom u8 demo_palette[16]={0x0F,0x16,0x2A,0x22,0x0F,0x16,0x2A,0x22,0x0F,0x16,0x2A,0x22,0x0F,0x16,0x2A,0x22};
u8 oam_fair_x[64];u8 oam_fair_y[64];u8 oam_fair_active[64];
__location(0x0200) u8 oam_fair_shadow[256];u8 oam_fair_used;
void main() {
    u8 i;
    m_init();__ppu_off();__palette_sp_load(demo_palette);
    for(i=0;i<64;i++)oam_fair_active[i]=0;
    // Keep slot 0 first, independently of the rotating pool.
    __sprite_set(0,144,31,129,0);
    oam_fair_active[13]=1;oam_fair_x[13]=148;oam_fair_y[13]=68;
    oam_fair_active[14]=1;oam_fair_x[14]=164;oam_fair_y[14]=68;
    oam_fair_active[15]=1;oam_fair_x[15]=180;oam_fair_y[15]=68;
    oam_fair_phase=0;oam_fair_limit=3;oam_fair_tile=128;oam_fair_attr=0;
    // example:OAM_FairDraw:start
    oam_fair_used=4; // Byte cursor: reserve the already prepared slot 0.
    OAM_FairDraw(); // Phase becomes 13; append pool entries 13, 14 and 15.
    // example:OAM_FairDraw:end
    m_text(1,0,"FAIR OAM");m_wait();m_text(1,4,"KEEP FIRST");m_wait();m_text(1,8,"CENTERS");m_wait();
    m_text(1,12,"PHASE");m_wait();m_put(7,12,(u8)('0'+oam_fair_phase/10));m_put(8,12,(u8)('0'+oam_fair_phase%10));m_wait();m_text(1,14,"DRAWN");m_wait();m_put(7,14,(u8)('0'+oam_fair_drawn/10));m_put(8,14,(u8)('0'+oam_fair_drawn%10));m_wait();m_text(1,16,"BYTES");m_wait();m_put(7,16,(u8)('0'+oam_fair_used/10));m_put(8,16,(u8)('0'+oam_fair_used%10));m_wait();
    __oam_dma();__ppu_ctrl_set(0x80);__ppu_mask_set(0x1E);
    // Keep this single call visible; the state test separately checks the full 64-call cycle.
    while(1){m_wait();__oam_dma();}
}
