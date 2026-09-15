// Inspect packed RAM flags and the normalized GB bit-test return value.
#include "gb_tile_color_example.h"
#include "rpg.h"
#define BIT_EXPECTED_ON 1
void bit_label(u8 row,const u8* text){m_text(1,row,text);}
void bit_value(u8 row,const u8* text,u8 value){
    bit_label(row,text);
    m_put(16,row,(u8)('0'+value/100));
    m_put(17,row,(u8)('0'+value/10%10));
    m_put(18,row,(u8)('0'+value%10));
}
#include "bit_example_checks.h"
void main(){
    tile_color_example_begin();bit_checks();
    M_LCDC=0x91;bit_show();while(1){m_wait();}
}
