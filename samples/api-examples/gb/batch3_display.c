// display: Exercise the APIs and compare the documented results.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "rpg.h"
__location(0xC600) u16 result[80];
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
u8 outer;u8 inner;
void main(){u8 i;u8 x;u8 y;tile_example_begin();M_LCDC=0;for(i=0;i<80;i++)result[i]=0;

// example:__getbgmapbase:start
M_LCDC=0;result[0]=__getbgmapbase();M_LCDC=8;result[1]=__getbgmapbase();
// example:__getbgmapbase:end

// example:__getwinmapbase:start
M_LCDC=0;result[2]=__getwinmapbase();M_LCDC=0x40;result[3]=__getwinmapbase();
// example:__getwinmapbase:end

// example:__tile_addr:start
result[4]=__tile_addr(0x9800,3,2);
// example:__tile_addr:end

// example:__scroll_bg_set:start
__scroll_bg_set(19,27);result[5]=*((u8*)0xFF43);result[6]=*((u8*)0xFF42);__scroll_bg_set(0,0);
// example:__scroll_bg_set:end

// example:__critical_enter:start
*((u8*)0xFFFF)=0;outer=__critical_enter();inner=__critical_enter();result[7]=outer;result[8]=inner;
// example:__critical_enter:end

// example:__critical_leave:start
__critical_leave(inner);__critical_leave(outer);
// example:__critical_leave:end

// example:__wait_ly:start
M_LCDC=0x91;__wait_ly(80);result[9]=*((u8*)0xFF44);
// example:__wait_ly:end

// example:__wait_vblank:start
__wait_vblank();result[10]=*((u8*)0xFF44);M_LCDC=0;__wait_vblank();__wait_ly(200);result[11]=1;
// example:__wait_vblank:end

m_text(1,0,"DISPLAY / WAIT");
m_text(1,2,"BG BASE");demo_word(2,result[0]);
m_text(1,4,"BG BASE 2");demo_word(4,result[1]);
m_text(1,6,"TILE ADDR");demo_word(6,result[4]);
m_text(1,8,"OUTER TOKEN");demo_word(8,result[7]);
m_text(1,10,"INNER TOKEN");demo_word(10,result[8]);
m_text(1,12,"TARGET LY");demo_word(12,result[9]);
m_text(1,14,"VBLANK LY");demo_word(14,result[10]);
m_text(1,16,"LCD OFF OK");demo_word(16,result[11]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
