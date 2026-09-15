// split_intrinsics: compare the documented positions and colors with this complete ROM.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "scroll.c"
__location(0xC600) u16 result[80];

void main(){u8 i;u8 x;u8 y;tile_example_begin();M_LCDC=0;__vram_fill(0x87E0,255,16);for(i=0;i<80;i++)result[i]=0;
Scroll_Init();Scroll_WindowHide();for(y=2;y<4;y++)for(x=4;x<7;x++)__settile_xy(x,y,126);for(y=10;y<12;y++)for(x=4;x<7;x++)__settile_xy(x,y,126);for(y=14;y<16;y++)for(x=4;x<7;x++)__settile_xy(x,y,126);vram_example_color(4,2,3,2,1);vram_example_color(4,10,3,2,1);vram_example_color(4,14,3,2,1);// example:__scroll_split_reset:start
__scroll_split_reset();
// example:__scroll_split_reset:end
// example:__scroll_split_push:start
__scroll_split_push(64,8,0);
// example:__scroll_split_push:end
// example:__scroll_split_push_ex:start
__scroll_split_push_ex(104,16,0,7,0,KQ_SCROLL_SPLIT_USE_BG|KQ_SCROLL_SPLIT_WIN_HIDE);
// example:__scroll_split_push_ex:end
M_LCDC=0x91;// example:__scroll_split_commit:start
__scroll_split_commit();
// example:__scroll_split_commit:end

result[79]=0xA55A;while(1){}
}
