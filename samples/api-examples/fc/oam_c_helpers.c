// Select the C runtime explicitly; nes_game.h and fc.h define conflicting macros.
#define MANUAL_FC_RUNTIME
#include "fc_common.h"
#include "runtime.c"
#include "metasprite.c"
__prg_rom u8 demo_palette[16]={0x0F,0x16,0x2A,0x22,0x0F,0x16,0x2A,0x22,0x0F,0x16,0x2A,0x22,0x0F,0x16,0x2A,0x22};
__location(0x0400) u8 demo_alternate[256];
u8 demo_parts[9];u8 demo_next;
void main() {
    u16 i;
    m_init();__ppu_off();__palette_sp_load(demo_palette);
    demo_parts[0]=0;demo_parts[1]=0;demo_parts[2]=128;demo_parts[3]=0;
    demo_parts[4]=8;demo_parts[5]=0;demo_parts[6]=128;demo_parts[7]=0x40;demo_parts[8]=255;
    // example:c_nes_metasprite_draw:start
    demo_next=nes_metasprite_draw(4,144,31,demo_parts); // C function: returns 6.
    // example:c_nes_metasprite_draw:end
    demo_next=nes_metasprite_draw(6,144,63,demo_parts); // Returns 8.
    // example:nes_metasprite_hide_from:start
    nes_metasprite_hide_from(6,2); // Hide slots 6 and 7; the pair at slots 4 and 5 remains.
    // example:nes_metasprite_hide_from:end
    __sprite_set(8,144,95,128,0);
    m_text(1,0,"C OAM HELPERS");m_wait();m_text(24,0,"NEXT");m_wait();m_put(29,0,'0');m_put(30,0,(u8)('0'+demo_next));m_wait();
    m_text(1,4,"PAIR");m_wait();m_text(1,8,"HIDE RANGE");m_wait();m_text(1,12,"PAGE 04");m_wait();
    for(i=0;i<256;i++)demo_alternate[i]=nes_oam_shadow[i];
    demo_alternate[33]=129; // Page 04 selects the green square for slot 8.
    nes_oam_dma(4);__ppu_ctrl_set(0x80);__ppu_mask_set(0x1E);
    while(1) {
        // example:c_nes_oam_dma:start
        m_wait();nes_oam_dma(4); // C function: source address high byte, 0x0400 -> 4.
        // example:c_nes_oam_dma:end
    }
}
