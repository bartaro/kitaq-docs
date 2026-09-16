// nametable: Exercise the APIs and compare the documented results.
#include "fc_common.h"
#include "runtime.h"
#include "nametable_asset.c"
#include "attribute.c"
__location(0x0600) u16 result[80];
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
__prg_rom u8 colors[32]={15,48,48,48,15,22,22,22,15,18,18,18,15,26,26,26,15,48,48,48,15,22,22,22,15,18,18,18,15,26,26,26};__prg_rom u8 empty[960]={0};u8 table[64];u8 row[32];u8 patch[12];
void main(){u8 i;u8 x;u8 y;__ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();__palette_bg_load(manual_pal);__nametable_rect(0,0,32,30,0);for(i=0;i<80;i++)result[i]=0;
__palette_bg_load(colors);nes_vram_queue_clear();
// example:nes_nt_base_from_index:start
result[0]=nes_nt_base_from_index(5);
// example:nes_nt_base_from_index:end

// example:nes_attr_base_from_nt:start
result[1]=nes_attr_base_from_nt(0x2400);
// example:nes_attr_base_from_nt:end

// example:nes_attr_shadow_clear:start
nes_attr_shadow_clear(0x55);result[2]=nes_attr_shadow[63];
// example:nes_attr_shadow_clear:end

// example:nes_attr_shadow_copy:start
for(i=0;i<64;i++)table[i]=0x55;nes_attr_shadow_copy(table);result[3]=nes_attr_shadow[0];
// example:nes_attr_shadow_copy:end

// example:nes_nametable_apply_now:start
nes_nametable_apply_now(0x2000,empty,table);
// example:nes_nametable_apply_now:end

// example:nes_attr_shadow_set_quad:start
nes_attr_shadow_set_quad(4,8,2);result[4]=nes_attr_shadow[17];
// example:nes_attr_shadow_set_quad:end

// example:nes_attr_apply_now:start
nes_attr_apply_now(0x2000);
// example:nes_attr_apply_now:end

// example:nes_attr_queue_all:start
result[5]=nes_attr_queue_all(0x2000);result[6]=nes_vram_queue_used;nes_vram_queue_nmi_flush();
// example:nes_attr_queue_all:end
for(i=0;i<32;i++)row[i]=0;for(i=2;i<6;i++)row[i]=1;
// example:nes_nt_stream_row:start
nes_nt_stream_row(0x2000,2,row);
// example:nes_nt_stream_row:end

// example:nes_nt_queue_row:start
result[7]=nes_nt_queue_row(0x2000,4,row);nes_vram_queue_nmi_flush();
// example:nes_nt_queue_row:end
for(i=0;i<12;i++)patch[i]=0;patch[0]=1;patch[1]=1;patch[4]=1;patch[5]=1;patch[8]=1;patch[9]=1;
// example:nes_nt_stream_rect:start
// A pitch of four skips two source bytes at the end of each row.
nes_nt_stream_rect(0x2000,4,8,2,2,4,patch);
// example:nes_nt_stream_rect:end

// example:nes_nt_queue_rect:start
result[8]=nes_nt_queue_rect(0x2000,10,8,2,3,4,patch);result[9]=nes_vram_queue_used;nes_vram_queue_nmi_flush();
// example:nes_nt_queue_rect:end

// example:nes_nt_queue_fill_rect:start
result[10]=nes_nt_queue_fill_rect(0x2000,16,8,4,3,1);result[11]=nes_vram_queue_used;nes_vram_queue_nmi_flush();
// example:nes_nt_queue_fill_rect:end

result[79]=0xA55A;__scroll_set(0,0);__ppu_ctrl_set(0);__ppu_mask_set(0x0A);while(1){}
}
