// scroll_wrappers demonstrates a complete, reproducible library workflow.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "scroll.c"
__location(0xC600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
__location(0xFF43) u8 M_SCX;__location(0xFF42) u8 M_SCY;__location(0xFF4B) u8 M_WX;__location(0xFF4A) u8 M_WY;
void main(){u8 i;tile_example_begin();M_LCDC=0;vram_example_color(1,2,18,14,2);for(i=0;i<80;i++)result[i]=0;
// example:Scroll_Init:start
Scroll_Init();result[0]=M_SCX;result[1]=M_SCY;result[2]=M_WX;result[3]=M_WY;
// example:Scroll_Init:end
// example:Scroll_SetBgX:start
Scroll_SetBgX(250);result[4]=M_SCX;
// example:Scroll_SetBgX:end
// example:Scroll_SetBgY:start
Scroll_SetBgY(2);result[5]=M_SCY;
// example:Scroll_SetBgY:end
// example:Scroll_GetBgX:start
result[6]=Scroll_GetBgX();
// example:Scroll_GetBgX:end
// example:Scroll_GetBgY:start
result[7]=Scroll_GetBgY();
// example:Scroll_GetBgY:end
// example:Scroll_SetWindow:start
Scroll_SetWindow(15,8);result[8]=M_WX;result[9]=M_WY;
// example:Scroll_SetWindow:end
// example:Scroll_SetWindowX:start
Scroll_SetWindowX(23);result[10]=M_WX;
// example:Scroll_SetWindowX:end
// example:Scroll_SetWindowY:start
Scroll_SetWindowY(16);result[11]=M_WY;
// example:Scroll_SetWindowY:end
// example:Scroll_GetWindowX:start
result[12]=Scroll_GetWindowX();
// example:Scroll_GetWindowX:end
// example:Scroll_GetWindowY:start
result[13]=Scroll_GetWindowY();
// example:Scroll_GetWindowY:end
// example:Scroll_SetBgBuffered:start
Scroll_SetBgBuffered(16,24);result[14]=M_SCX;result[15]=Scroll_GetBgX();
// example:Scroll_SetBgBuffered:end
// example:Scroll_SetWindowBuffered:start
Scroll_SetWindowBuffered(39,32);result[16]=M_WX;result[17]=Scroll_GetWindowX();
// example:Scroll_SetWindowBuffered:end
// example:Scroll_Flush:start
Scroll_Flush();result[18]=M_SCX;result[19]=M_SCY;result[20]=M_WX;result[21]=M_WY;
// example:Scroll_Flush:end
// example:Scroll_BgAdd:start
Scroll_BgAdd(-20,3);result[22]=M_SCX;result[23]=M_SCY;
// example:Scroll_BgAdd:end
// example:Scroll_WindowAdd:start
Scroll_WindowAdd(4,-40);result[24]=M_WX;result[25]=M_WY;
// example:Scroll_WindowAdd:end
// example:Scroll_WindowShow:start
Scroll_WindowShow();result[26]=M_LCDC&32;
// example:Scroll_WindowShow:end
// example:Scroll_WindowHide:start
Scroll_WindowHide();result[27]=M_LCDC&32;
// example:Scroll_WindowHide:end
// example:Scroll_SetBg:start
Scroll_SetBg(8,16);result[28]=M_SCX;result[29]=M_SCY;
// example:Scroll_SetBg:end

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
