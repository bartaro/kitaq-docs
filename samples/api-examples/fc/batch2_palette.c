// palette: compare the documented positions and colors with this complete ROM.
#include "fc_common.h"
#include "palette.c"
#include "runtime.h"
__location(0x0600) u16 result[80];
__prg_rom u8 colors[32]={15,48,48,48,15,22,22,22,15,18,18,18,15,26,26,26,15,48,48,48,15,22,22,22,15,18,18,18,15,26,26,26};u8 four[4];
void main(){u8 i;u8 x;u8 y;__ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();__nametable_rect(0,0,32,30,0);for(i=0;i<80;i++)result[i]=0;
// example:nes_palette_copy:start
nes_palette_copy(colors);result[0]=nes_palette_shadow[5];
// example:nes_palette_copy:end
// example:nes_palette_apply_now:start
nes_palette_apply_now(colors);
// example:nes_palette_apply_now:end
// example:nes_palette_apply_shadow_now:start
nes_palette_apply_shadow_now();
// example:nes_palette_apply_shadow_now:end
// example:nes_palette_queue_all:start
nes_vram_queue_clear();result[1]=nes_palette_queue_all(colors);result[2]=nes_vram_queue_used;nes_vram_queue_nmi_flush();
// example:nes_palette_queue_all:end
four[0]=15;four[1]=26;four[2]=26;four[3]=26;// example:nes_palette_queue_bg4:start
result[3]=nes_palette_queue_bg4(3,four);nes_vram_queue_nmi_flush();
// example:nes_palette_queue_bg4:end
four[1]=18;four[2]=18;four[3]=18;// example:nes_palette_queue_sprite4:start
result[4]=nes_palette_queue_sprite4(2,four);nes_vram_queue_nmi_flush();
// example:nes_palette_queue_sprite4:end
__nametable_rect(2,4,4,4,1);__nametable_rect(10,4,4,4,1);__nametable_rect(18,4,4,4,1);__attr_set(2,4,0x55);__attr_set(6,4,0x55);__attr_set(10,4,0xAA);__attr_set(14,4,0xAA);__attr_set(18,4,0xFF);__attr_set(22,4,0xFF);__sprite_set(0,16,95,1,1);__sprite_set(1,80,95,1,2);__sprite_set(2,144,95,1,3);__oam_dma();
m_text(1,0,"BG AND SPRITE PALETTES");__vramq_commit();__vramq_exec();
m_text(1,16,"TOP: RED BLUE GREEN");__vramq_commit();__vramq_exec();
m_text(1,18,"SPRITES USE THEIR COLORS");__vramq_commit();__vramq_exec();
result[79]=0xA55A;__scroll_set(0,0);__ppu_ctrl_set(0);__ppu_mask_set(0x1E);while(1){}
}
