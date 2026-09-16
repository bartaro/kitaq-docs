// save: Exercise the APIs and compare the documented results.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "save.c"
__location(0xC600) u16 result[80];
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
u8 payload[3];u8 readback[3];
void main(){u8 i;u8 x;u8 y;tile_example_begin();M_LCDC=0;for(i=0;i<80;i++)result[i]=0;

// example:save_init:start
save_init();save_clear(0);
// example:save_init:end

// example:save_exists:start
result[0]=save_exists(0);
// example:save_exists:end

// example:save_write:start
payload[0]=7;payload[1]=42;payload[2]=255;result[1]=save_write(0,payload,3);result[2]=save_write(4,payload,3);result[3]=save_write(0,payload,507);
// example:save_write:end

// example:save_check:start
result[4]=save_check(0);
// example:save_check:end

// example:save_read:start
readback[0]=99;result[5]=save_read(0,readback,2);result[6]=readback[0];result[7]=save_read(0,readback,3);result[8]=readback[0];result[9]=readback[2];
// example:save_read:end

// example:save_load:start
readback[1]=0;result[10]=save_load(0,readback,3);result[11]=readback[1];
// example:save_load:end

// example:__sram_read8:start
*((u8*)0x4000)=0;result[12]=__sram_read8(0xA006);result[19]=*((u8*)0xA006);
// example:__sram_read8:end

// example:__sram_write8:start
__sram_write8(0xA006,8);result[20]=*((u8*)0xA006);result[13]=save_exists(0);readback[0]=77;result[14]=save_read(0,readback,3);result[15]=readback[0];
// example:__sram_write8:end

// example:save_clear:start
save_clear(0);result[16]=save_check(0);result[17]=save_write(3,payload,0);result[18]=save_exists(3);save_clear(3);
// example:save_clear:end

m_text(1,0,"SAVE VALIDATION");
m_text(1,2,"WRITE OK");demo_word(2,result[1]);
m_text(1,4,"BAD SLOT");demo_word(4,result[2]);
m_text(1,6,"BAD LENGTH");demo_word(6,result[5]);
m_text(1,8,"LOADED BYTE");demo_word(8,result[11]);
m_text(1,10,"CHECKSUM BAD");demo_word(10,result[13]);
m_text(1,12,"DEST KEPT");demo_word(12,result[15]);
m_text(1,14,"CLEARED");demo_word(14,result[16]);
m_text(1,16,"EMPTY VALID");demo_word(16,result[18]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
