#pragma once
// Load the original manual font and link implementation into one program.
#include "gb_tile_example.h"
#include "link_hwregs_gb.c"
#include "link.c"
#include "link_packet.c"
#pragma bank 0
__location(0xC600) u16 result[80];
// Keep the LCD active while VBlank-based waits run.
void lesson_begin(){u8 i;tile_example_begin();for(i=0;i<80;i++)result[i]=0;M_LCDC=0x91;}
void lesson_delay(u8 frames){u8 i;for(i=0;i<frames;i++)m_wait();}
// Display one result as an unsigned five-digit number.
void lesson_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,48+value/place);value=value%place;place=place/10;}}
