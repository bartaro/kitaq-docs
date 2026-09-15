// Compare memory-copy/fill byte counts, fixed copies, guards and argument effects.
#include "fc_common.h"
__prg_rom u8 memory_palette[16]={0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22};

// Publish each short text batch while rendering and NMI are disabled.
void memory_label(u8 row,const u8* text){
    m_text(1,row,text);__vramq_commit();__vramq_exec();
}
void memory_value(u8 row,const u8* text,u16 value){
    memory_label(row,text);
    m_put(27,row,(u8)('0'+value/100));
    m_put(28,row,(u8)('0'+value/10%10));
    m_put(29,row,(u8)('0'+value%10));
    __vramq_commit();__vramq_exec();
}
#include "memory_example_checks.h"

void main(void){
    __ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();
    __palette_bg_load(memory_palette);__nametable_rect(0,0,32,30,0);
    memory_checks();memory_show();
    __scroll_set(0,0);__ppu_mask_set(0x0A);
    while(1){}
}
