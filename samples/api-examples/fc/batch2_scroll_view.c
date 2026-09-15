// scroll_view: compare the documented positions and colors with this complete ROM.
#include "fc_common.h"
#include "scroll.c"
__location(0x0600) u16 result[80];
__prg_rom u8 colors[32]={15,48,48,48,15,22,22,22,15,18,18,18,15,26,26,26,15,48,48,48,15,22,22,22,15,18,18,18,15,26,26,26};u8 four[4];
void main(){u8 i;u8 x;u8 y;__ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();__nametable_rect(0,0,32,30,0);for(i=0;i<80;i++)result[i]=0;
__palette_bg_load(colors);__nametable_rect_nt(1,0,0,32,30,0);__vram_fill(0x27C0,0x55,64);__nametable_rect_nt(1,4,4,4,2,1);
result[79]=0xA55A;nes_scroll_set_base_ctrl(0);nes_scroll_set(264,16);nes_scroll_apply();__ppu_mask_set(0x0A);while(1){}
}
