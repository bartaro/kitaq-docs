// script: Exercise the APIs and compare the documented results.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "flags.c"
#include "text.c"
#include "script.c"
__location(0xC600) u16 result[80];
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
#pragma fixed_bank 2
__prg_rom u8 target[6]={2,19,0,7,1,0};
#pragma fixed_bank 1
typedef __packed struct {u8 op;u8 bank;const u8* dest;} Jump;
__prg_rom Jump entry[1]={{4,2,target}};
#pragma fixed_bank 0

void main(){u8 i;u8 x;u8 y;tile_example_begin();M_LCDC=0;for(i=0;i<80;i++)result[i]=0;

// example:script_run:start
flag_clear(19);script_run(1,(const u8*)&entry);result[0]=flag_get(19);
// example:script_run:end

// example:script_wait_frames:start
script_wait_frames(2);result[1]=script_step();result[2]=script_step();
// example:script_wait_frames:end

// example:script_step:start
result[3]=script_step();result[4]=flag_get(19);result[5]=script_step();result[6]=script_step();result[7]=script_step();
// example:script_step:end

m_text(1,0,"BANKED SCRIPT");
m_text(1,2,"BEFORE RUN");demo_word(2,result[0]);
m_text(1,4,"WAIT STEP 1");demo_word(4,result[1]);
m_text(1,6,"WAIT STEP 2");demo_word(6,result[2]);
m_text(1,8,"JUMP / WAIT");demo_word(8,result[3]);
m_text(1,10,"TARGET FLAG");demo_word(10,result[4]);
m_text(1,12,"WAIT COUNT");demo_word(12,result[5]);
m_text(1,14,"END");demo_word(14,result[6]);
m_text(1,16,"INACTIVE");demo_word(16,result[7]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
