// Inspect packed RAM flags and the FC bit-test return mask.
#include "fc_common.h"
#define BIT_EXPECTED_ON 128
__prg_rom u8 bit_palette[16]={0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22};
// Keep rendering and NMI disabled while publishing each text batch.
void bit_label(u8 row,const u8* text){m_text(1,row,text);__vramq_commit();__vramq_exec();}
void bit_value(u8 row,const u8* text,u8 value){
    bit_label(row,text);
    m_put(27,row,(u8)('0'+value/100));m_put(28,row,(u8)('0'+value/10%10));
    m_put(29,row,(u8)('0'+value%10));__vramq_commit();__vramq_exec();
}
#include "bit_example_checks.h"
void main(){
    __ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();
    __palette_bg_load(bit_palette);__nametable_rect(0,0,32,30,0);
    bit_checks();bit_show();__scroll_set(0,0);__ppu_mask_set(0x0A);while(1){}
}
