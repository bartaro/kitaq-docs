// geometry demonstrates a complete, reproducible library workflow.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "fixed.c"

__location(0xC600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
KQRect a;KQRect b;KQRect touch;u8 gx;u8 gy;u8 inside_a;u8 inside_b;u8 tile;
void main(){u8 i;tile_example_begin();M_LCDC=0;vram_example_color(1,2,18,14,2);for(i=0;i<80;i++)result[i]=0;a.x=1;a.y=1;a.w=8;a.h=6;b.x=5;b.y=4;b.w=8;b.h=6;touch.x=9;touch.y=1;touch.w=8;touch.h=6;
// example:kq_rect_intersect:start
result[0]=kq_rect_intersect(a,b);result[2]=kq_rect_intersect(a,touch);
// example:kq_rect_intersect:end
// example:kq_point_in_rect:start
result[1]=kq_point_in_rect(9,1,a);
for(gy=0;gy<11;gy++){for(gx=0;gx<15;gx++){
inside_a=kq_point_in_rect(gx,gy,a);inside_b=kq_point_in_rect(gx,gy,b);
tile=0;if(inside_a){tile=65;result[3]=result[3]+1;}if(inside_b)tile=66;if(inside_a && inside_b){tile=79;result[4]=result[4]+1;}
m_put(1+gx,2+gy,tile);if(tile!=0)vram_example_color(1+gx,2+gy,1,1,tile==65?1:(tile==66?2:3));
}}
// example:kq_point_in_rect:end


demo_label(0,"RECTANGLE OVERLAP");
demo_label(14,"A / B / O=BOTH");
demo_label(16,"OVERLAP");demo_word(16,result[0]);
demo_label(17,"RIGHT EDGE");demo_word(17,result[1]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
