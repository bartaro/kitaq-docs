// attributes: Exercise the APIs and compare the documented results.
#include "fc_common.h"
#include "runtime.h"
#include "nametable_asset.c"
#include "attribute.c"
__location(0x0600) u16 result[80];
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
__prg_rom u8 colors[32]={15,48,48,48,15,22,22,22,15,18,18,18,15,26,26,26,15,48,48,48,15,22,22,22,15,18,18,18,15,26,26,26};u8 table[64];
void main(){u8 i;u8 x;u8 y;__ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();__palette_bg_load(manual_pal);__nametable_rect(0,0,32,30,0);for(i=0;i<80;i++)result[i]=0;
__palette_bg_load(colors);nes_vram_queue_clear();
// example:nes_attr_shadow_build_from_palette_map:start
for(i=0;i<64;i++)table[i]=0;table[0]=0xE4;nes_attr_shadow_build_from_palette_map(table);result[0]=nes_attr_shadow[0];
// example:nes_attr_shadow_build_from_palette_map:end
nes_attr_shadow_clear(0);
// example:nes_attr_shadow_fill_rect:start
nes_attr_shadow_fill_rect(2,4,4,4,1);nes_attr_shadow_fill_rect(10,4,4,4,2);nes_attr_shadow_fill_rect(30,28,2,2,3);result[1]=nes_attr_shadow[8];result[2]=nes_attr_shadow[9];result[3]=nes_attr_shadow[15];result[4]=nes_attr_shadow[63];
// example:nes_attr_shadow_fill_rect:end

// example:nes_attr_queue_rect:start
result[5]=nes_attr_queue_rect(0x2000,2,4,4,4);result[6]=nes_vram_queue_used;result[7]=nes_attr_queue_rect(0x2000,10,4,4,4);result[8]=nes_attr_queue_rect(0x2000,30,28,2,2);nes_vram_queue_nmi_flush();
// example:nes_attr_queue_rect:end
__nametable_rect(2,4,4,4,1);__nametable_rect(10,4,4,4,1);__nametable_rect(30,28,2,2,1);
result[79]=0xA55A;__scroll_set(0,0);__ppu_ctrl_set(0);__ppu_mask_set(0x0A);while(1){}
}
