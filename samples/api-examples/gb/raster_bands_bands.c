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
m_text(1,0,"BANDS 0 8 16");
// example:Raster_Disable:start
Raster_Disable();
// example:Raster_Disable:end
// example:Raster_Init:start
Raster_Init();
// example:Raster_Init:end
// example:Raster_Clear:start
Raster_Clear();
// example:Raster_Clear:end
// example:Raster_Push:start
Raster_Push(0,0,0);Raster_Push(64,8,0);
// example:Raster_Push:end
// example:Raster_PushEx:start
Raster_PushEx(104,16,0,7,0,KQ_RASTER_BG|KQ_RASTER_WIN_HIDE);
// example:Raster_PushEx:end
// example:Raster_GetCount:start
result[0]=Raster_GetCount();
// example:Raster_GetCount:end
// example:Raster_GetLastError:start
result[1]=Raster_GetLastError();
// example:Raster_GetLastError:end
M_LCDC=0x91;
// example:Raster_Commit:start
result[2]=Raster_Commit();
// example:Raster_Commit:end
result[3]=165;while(1){}
}
