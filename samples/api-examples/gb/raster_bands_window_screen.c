// Copyright (c) 2026 DAISUKE OBA. MIT License.
// Compare fixed and scrolling original rectangles, or window/color bands.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "scroll.c"
#include "raster.c"
__location(0xC600) u8 result[4];
void main(){u8 x;u8 y;tile_example_begin();M_LCDC=0;
    Scroll_Init();Scroll_WindowHide();__vram_fill(0x87E0,255,16);
for(y=2;y<4;y++)for(x=4;x<7;x++)m_put(x,y,126);for(y=10;y<12;y++)for(x=4;x<7;x++)m_put(x,y,126);for(y=14;y<16;y++)for(x=4;x<7;x++)m_put(x,y,126);vram_example_color(4,2,3,2,1);vram_example_color(4,10,3,2,1);vram_example_color(4,14,3,2,1);
m_text(1,0,"SCREEN X24 Y48");
// Window tile coordinates are independent of the background map.
for(y=1;y<3;y++){__vram_fill((u16)(0x9C00+(u16)y*32+1),126,2);}
if(__cgb_is_cgb()){__cgb_safe_set_vbk(1);for(y=1;y<3;y++){__vram_memset_unsafe((u16)(0x9C00+(u16)y*32+1),2,2);}__cgb_safe_set_vbk(0);}
Raster_Init();
// example:Raster_PushWindowScreen:start
Raster_PushWindowScreen(0,24,48,KQ_RASTER_WIN_SHOW);
// example:Raster_PushWindowScreen:end
result[0]=Raster_GetCount();result[1]=Raster_GetLastError();
M_LCDC=0xD1;
result[2]=Raster_Commit();
result[3]=165;while(1){}
}
