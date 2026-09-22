// Copyright (c) 2026 DAISUKE OBA. MIT License.
// Compare fixed and scrolling original rectangles, or window/color bands.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "scroll.c"
#include "raster.c"
__location(0xC600) u8 result[4];
void main(){u8 x;u8 y;tile_example_begin();M_LCDC=0;
    Scroll_Init();Scroll_WindowHide();__vram_fill(0x87E0,255,16);
Raster_Init();
// example:Raster_PushBgColor0:start
Raster_PushBgColor0(0,0x7C00);Raster_PushBgColor0(64,0x001F);Raster_PushBgColor0(112,0x03E0);
// example:Raster_PushBgColor0:end
result[0]=Raster_GetCount();result[1]=Raster_GetLastError();
M_LCDC=0x91;
result[2]=Raster_Commit();
result[3]=165;while(1){}
}
