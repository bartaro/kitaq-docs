// actor: Exercise the APIs and compare the documented results.
#include "fc_common.h"
#include "runtime.h"
#include "metasprite.c"
#include "actor.c"
__location(0x0600) u16 result[80];
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
__prg_rom u8 colors[32]={15,48,48,48,15,22,22,22,15,18,18,18,15,26,26,26,15,48,48,48,15,22,22,22,15,18,18,18,15,26,26,26};struct NesActor a;struct NesActor b;__prg_rom u8 parts[9]={0,0,1,1,8,0,1,2,255};
void main(){u8 i;u8 x;u8 y;__ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();__palette_bg_load(manual_pal);__nametable_rect(0,0,32,30,0);for(i=0;i<80;i++)result[i]=0;
__palette_sp_load(colors+16);for(i=0;i<64;i++)nes_oam_shadow[(u16)i*4]=248;a.width=16;a.height=8;b.width=16;b.height=8;
// example:nes_actor_set_world:start
nes_actor_set_world(&a,300,95);nes_actor_set_world(&b,316,95);result[0]=a.world_x;
// example:nes_actor_set_world:end

// example:nes_actor_update_screen:start
nes_actor_update_screen(&a,268,32);result[1]=a.screen_x;result[2]=a.screen_y;
// example:nes_actor_update_screen:end

// example:nes_actor_collide:start
result[3]=nes_actor_collide(&a,&b);nes_actor_set_world(&b,315,95);result[4]=nes_actor_collide(&a,&b);
// example:nes_actor_collide:end

// example:nes_actor_draw_metasprite:start
result[5]=nes_actor_draw_metasprite(&a,0,parts);result[6]=nes_oam_shadow[3];result[7]=nes_oam_shadow[7];nes_oam_dma(2);
// example:nes_actor_draw_metasprite:end

result[79]=0xA55A;__scroll_set(0,0);__ppu_ctrl_set(0);__ppu_mask_set(0x1E);while(1){}
}
