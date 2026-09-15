// camera_view: compare the documented positions and colors with this complete ROM.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "scroll.c"
#include "camera.c"
__location(0xC600) u16 result[80];
Camera8_8 view;
void main(){u8 i;u8 x;u8 y;tile_example_begin();M_LCDC=0;__vram_fill(0x87E0,255,16);for(i=0;i<80;i++)result[i]=0;
for(y=4;y<7;y++)for(x=4;x<8;x++)__settile_xy(x,y,126);vram_example_color(4,4,4,3,1);for(y=0;y<8;y++)for(x=0;x<8;x++){if(x==0||x==7||y==0||y==7)*((u8*)(0x9C00+(u16)y*32+x))=126;}*((u8*)0x9C42)=126;*((u8*)0x9C43)=126;*((u8*)0x9C62)=126;*((u8*)0x9C63)=126;if(__cgb_is_cgb()){__cgb_safe_set_vbk(1);for(y=0;y<8;y++)__vram_memset_unsafe(0x9C00+(u16)y*32,2,8);__vram_memset_unsafe(0x9C42,3,2);__vram_memset_unsafe(0x9C62,3,2);__cgb_safe_set_vbk(0);}Camera_Init(&view);Camera_Set(&view,2048,4096);Camera_ApplyBg(&view);Scroll_SetWindow(103,80);Scroll_WindowShow();
result[79]=0xA55A;M_LCDC=0xF1;while(1){}
}
