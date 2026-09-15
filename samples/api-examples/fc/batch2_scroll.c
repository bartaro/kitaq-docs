// scroll demonstrates a complete, reproducible library workflow.
#include "fc_common.h"
__prg_rom u8 demo_palette[16]={15,34,34,34,15,34,34,34,15,34,34,34,15,34,34,34};
#include "scroll.c"
__location(0x0600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);__vramq_commit();__vramq_exec();}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}__vramq_commit();__vramq_exec();}

void main(){u8 i;__ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();__palette_bg_load(demo_palette);__nametable_rect(0,0,32,30,0);for(i=0;i<80;i++)result[i]=0;
// example:nes_scroll_set_base_ctrl:start
nes_scroll_set_base_ctrl(0x93);result[0]=nes_scroll_ctrl_base;
// example:nes_scroll_set_base_ctrl:end
// example:nes_scroll_set:start
nes_scroll_set(264,272);result[1]=nes_scroll_camera_x;result[2]=nes_scroll_camera_y;
// example:nes_scroll_set:end
// example:nes_scroll_apply:start
nes_scroll_apply();result[3]=nes_scroll_ctrl_base|((nes_scroll_camera_x>>8)&1)|((nes_scroll_camera_y>>7)&2);
// example:nes_scroll_apply:end
// example:nes_camera_follow_center:start
nes_camera_follow_center(300,260,128,120);result[4]=nes_scroll_camera_x;result[5]=nes_scroll_camera_y;
// example:nes_camera_follow_center:end

__ppu_ctrl_set(0);
demo_label(0,"CAMERA TO PPU SCROLL");
demo_label(2,"CTRL BASE");demo_word(2,result[0]);
demo_label(4,"CAMERA X");demo_word(4,result[1]);
demo_label(6,"CAMERA Y");demo_word(6,result[2]);
demo_label(8,"CTRL BITS");demo_word(8,result[3]);
demo_label(10,"CENTERED X");demo_word(10,result[4]);
demo_label(12,"CENTERED Y");demo_word(12,result[5]);
demo_label(14,"Y USES 256 UNITS");
result[79]=0xA55A;__scroll_set(0,0);__ppu_mask_set(0x0A);while(1){}
}
