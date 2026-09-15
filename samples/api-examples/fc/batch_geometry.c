// geometry demonstrates a complete, reproducible library workflow.
#include "fc_common.h"
__prg_rom u8 demo_palette[16]={15,34,34,34,15,34,34,34,15,34,34,34,15,34,34,34};
#include "fixed.c"
#include "collision.c"

__location(0x0600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);__vramq_commit();__vramq_exec();}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}__vramq_commit();__vramq_exec();}
KQRect a;KQRect b;KQRect touch;u8 gx;u8 gy;u8 inside_a;u8 inside_b;u8 tile;struct NesBox16 na;struct NesBox16 nb;
void main(){u8 i;__ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();__palette_bg_load(demo_palette);__nametable_rect(0,0,32,30,0);for(i=0;i<80;i++)result[i]=0;a.x=1;a.y=1;a.w=8;a.h=6;b.x=5;b.y=4;b.w=8;b.h=6;touch.x=9;touch.y=1;touch.w=8;touch.h=6;na.x=1;na.y=1;na.w=8;na.h=6;nb.x=5;nb.y=4;nb.w=8;nb.h=6;
// example:kq_rect_intersect:start
result[0]=kq_rect_intersect(a,b);result[2]=kq_rect_intersect(a,touch);
// example:kq_rect_intersect:end
// example:kq_point_in_rect:start
result[1]=kq_point_in_rect(9,1,a);
for(gy=0;gy<11;gy++){for(gx=0;gx<15;gx++){
inside_a=kq_point_in_rect(gx,gy,a);inside_b=kq_point_in_rect(gx,gy,b);
tile=0;if(inside_a){tile=65;result[3]=result[3]+1;}if(inside_b)tile=66;if(inside_a && inside_b){tile=79;result[4]=result[4]+1;}
m_put(1+gx,2+gy,tile);__vramq_commit();__vramq_exec();
}}
// example:kq_point_in_rect:end
// example:nes_box16_intersects:start
result[5]=nes_box16_intersects(&na,&nb);
// example:nes_box16_intersects:end
// example:nes_box16_contains_point:start
result[6]=nes_box16_contains_point(&na,9,1);
// example:nes_box16_contains_point:end


demo_label(0,"RECTANGLE OVERLAP");
demo_label(14,"A / B / O=BOTH");
demo_label(16,"OVERLAP");demo_word(16,result[0]);
demo_label(17,"RIGHT EDGE");demo_word(17,result[1]);
demo_label(19,"NES OVERLAP");demo_word(19,result[5]);
demo_label(20,"NES EDGE");demo_word(20,result[6]);
result[79]=0xA55A;__scroll_set(0,0);__ppu_mask_set(0x0A);while(1){}
}
