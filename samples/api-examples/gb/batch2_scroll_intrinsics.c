// scroll_intrinsics demonstrates a complete, reproducible library workflow.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "scroll.c"
__location(0xC600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
__location(0xFF43) u8 M_SCX;__location(0xFF42) u8 M_SCY;__location(0xFF4B) u8 M_WX;__location(0xFF4A) u8 M_WY;
void main(){u8 i;tile_example_begin();M_LCDC=0;vram_example_color(1,2,18,14,2);for(i=0;i<80;i++)result[i]=0;
__scroll_bg_set(0,0);__scroll_win_set(7,0);result[0]=M_SCX;result[1]=M_SCY;result[2]=M_WX;result[3]=M_WY;
// example:__scroll_bg_x_set:start
__scroll_bg_x_set(250);result[4]=M_SCX;
// example:__scroll_bg_x_set:end
// example:__scroll_bg_y_set:start
__scroll_bg_y_set(2);result[5]=M_SCY;
// example:__scroll_bg_y_set:end
// example:__scroll_bg_x_get:start
result[6]=__scroll_bg_x_get();
// example:__scroll_bg_x_get:end
// example:__scroll_bg_y_get:start
result[7]=__scroll_bg_y_get();
// example:__scroll_bg_y_get:end
// example:__scroll_win_set:start
__scroll_win_set(15,8);result[8]=M_WX;result[9]=M_WY;
// example:__scroll_win_set:end
// example:__scroll_win_x_set:start
__scroll_win_x_set(23);result[10]=M_WX;
// example:__scroll_win_x_set:end
// example:__scroll_win_y_set:start
__scroll_win_y_set(16);result[11]=M_WY;
// example:__scroll_win_y_set:end
// example:__scroll_win_x_get:start
result[12]=__scroll_win_x_get();
// example:__scroll_win_x_get:end
// example:__scroll_win_y_get:start
result[13]=__scroll_win_y_get();
// example:__scroll_win_y_get:end
// example:__scroll_bg_set_buffered:start
__scroll_bg_set_buffered(16,24);result[14]=M_SCX;result[15]=__scroll_bg_x_get();
// example:__scroll_bg_set_buffered:end
// example:__scroll_win_set_buffered:start
__scroll_win_set_buffered(39,32);result[16]=M_WX;result[17]=__scroll_win_x_get();
// example:__scroll_win_set_buffered:end
// example:__scroll_flush:start
__scroll_flush();result[18]=M_SCX;result[19]=M_SCY;result[20]=M_WX;result[21]=M_WY;
// example:__scroll_flush:end
// example:__scroll_bg_add:start
__scroll_bg_add(-20,3);result[22]=M_SCX;result[23]=M_SCY;
// example:__scroll_bg_add:end
// example:__scroll_win_add:start
__scroll_win_add(4,-40);result[24]=M_WX;result[25]=M_WY;
// example:__scroll_win_add:end
// example:__scroll_win_show:start
__scroll_win_show();result[26]=M_LCDC&32;
// example:__scroll_win_show:end
// example:__scroll_win_hide:start
__scroll_win_hide();result[27]=M_LCDC&32;
// example:__scroll_win_hide:end
// example:__scroll_bg_x_set_buffered:start
__scroll_bg_x_set_buffered(32);
// example:__scroll_bg_x_set_buffered:end
// example:__scroll_bg_y_set_buffered:start
__scroll_bg_y_set_buffered(40);
// example:__scroll_bg_y_set_buffered:end
// example:__scroll_win_x_set_buffered:start
__scroll_win_x_set_buffered(55);
// example:__scroll_win_x_set_buffered:end
// example:__scroll_win_y_set_buffered:start
__scroll_win_y_set_buffered(48);
// example:__scroll_win_y_set_buffered:end
__scroll_flush();result[28]=M_SCX;result[29]=M_SCY;result[30]=M_WX;result[31]=M_WY;
Scroll_SetBg(0,0);Scroll_SetWindow(7,0);
demo_label(0,"SCROLL: NOW / LATER");
demo_label(2,"BG X BEFORE");demo_word(2,result[14]);
demo_label(4,"BG X FLUSH");demo_word(4,result[18]);
demo_label(6,"WIN X BEFORE");demo_word(6,result[16]);
demo_label(8,"WIN X FLUSH");demo_word(8,result[20]);
demo_label(10,"BG X WRAPS");demo_word(10,result[22]);
demo_label(12,"WIN Y WRAPS");demo_word(12,result[25]);
demo_label(14,"WINDOW SHOW");demo_word(14,result[26]);
demo_label(16,"WINDOW HIDE");demo_word(16,result[27]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
