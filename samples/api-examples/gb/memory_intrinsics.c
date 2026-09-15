// Compare memory-copy/fill byte counts, fixed copies, guards and argument effects.
#include "gb_tile_color_example.h"
#include "rpg.h"

void memory_label(u8 row,const u8* text){m_text(1,row,text);}
void memory_value(u8 row,const u8* text,u16 value){
    memory_label(row,text);
    m_put(16,row,(u8)('0'+value/100));
    m_put(17,row,(u8)('0'+value/10%10));
    m_put(18,row,(u8)('0'+value%10));
}
#include "memory_example_checks.h"

void main(){
    tile_color_example_begin();
    memory_checks();
    M_LCDC=0x91;
    memory_show();
    while(1){m_wait();}
}
