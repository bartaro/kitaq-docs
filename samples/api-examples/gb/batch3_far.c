// far: Exercise the APIs and compare the documented results.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "rpg.h"
__location(0xC600) u16 result[80];
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
#pragma fixed_bank 1
__prg_rom u8 bank_bytes[3]={0x34,0x12,0xAB};
#pragma fixed_bank 0
far_ptr_t far;u8 copy[3];
void main(){u8 i;u8 x;u8 y;tile_example_begin();M_LCDC=0;for(i=0;i<80;i++)result[i]=0;

// example:far_read8:start
far.bank=1;far.ptr=bank_bytes;result[0]=far_read8(far);
// example:far_read8:end

// example:far_read16:start
result[1]=far_read16(far);
// example:far_read16:end

// example:far_read_block:start
far_read_block(copy,far,3);result[2]=copy[2];
// example:far_read_block:end

m_text(1,0,"BANKED ROM DATA");
m_text(1,4,"FIRST BYTE");demo_word(4,result[0]);
m_text(1,8,"LITTLE WORD");demo_word(8,result[1]);
m_text(1,12,"BLOCK LAST");demo_word(12,result[2]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
