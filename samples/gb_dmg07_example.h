#pragma once
// Original manual font, real hardware register access and the DMG-07 driver.
// Do not include link.c/link_packet.c: these drivers share the serial port.
#include "gb_tile_example.h"
#include "link_hwregs_gb.c"
#include "link_dmg07.c"
#pragma bank 0
__location(0xC600) u16 result[80];
__location(0xFF44) u8 D_LY;
u8 d_vblank;
// Keep the LCD on so that the scanline edge supplies one watchdog tick per frame.
void d_begin(){u8 i;tile_example_begin();for(i=0;i<80;i++)result[i]=0;d_vblank=0;M_LCDC=0x91;}
// Poll throughout the frame; a VBlank-only polling loop misses adapter bytes.
void d_poll(){LinkDmg07_Poll();if(D_LY>=144){if(d_vblank==0){d_vblank=1;LinkDmg07_TickFrame();}}else d_vblank=0;}
// Display an unsigned five-digit value; labels explain each observed result.
void d_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,48+value/place);value=value%place;place=place/10;}if(__cgb_is_cgb()){__cgb_safe_set_vbk(1);__vram_fill(0x9800+(u16)y*32+13,2,5);__cgb_safe_set_vbk(0);}}
