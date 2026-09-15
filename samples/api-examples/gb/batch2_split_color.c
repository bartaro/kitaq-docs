// split_color: compare the documented positions and colors with this complete ROM.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "scroll.c"
__location(0xC600) u16 result[80];

void main(){u8 i;u8 x;u8 y;tile_example_begin();M_LCDC=0;__vram_fill(0x87E0,255,16);for(i=0;i<80;i++)result[i]=0;
Scroll_Init();Scroll_WindowHide();Scroll_SplitReset();// example:Scroll_SplitPushBgColor0:start
Scroll_SplitPushBgColor0(0,0x7C00);Scroll_SplitPushBgColor0(64,0x001F);Scroll_SplitPushBgColor0(112,0x03E0);
// example:Scroll_SplitPushBgColor0:end
M_LCDC=0x91;Scroll_SplitCommit();
result[79]=0xA55A;while(1){}
}
