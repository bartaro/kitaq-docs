// math demonstrates a complete, reproducible library workflow.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "fixed.c"

__location(0xC600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
KQRect a;KQRect b;KQRect touch;
void main(){u8 i;tile_example_begin();M_LCDC=0;vram_example_color(1,2,18,14,2);for(i=0;i<80;i++)result[i]=0;a.x=8;a.y=8;a.w=8;a.h=8;b.x=12;b.y=12;b.w=8;b.h=8;touch.x=16;touch.y=8;touch.w=8;touch.h=8;
// example:fix_from_int:start
result[0]=fix_from_int(-3);
// example:fix_from_int:end
// example:fix_to_int:start
result[1]=fix_to_int(-384);
// example:fix_to_int:end
// example:fix_mul:start
result[2]=fix_mul(384,512);
// example:fix_mul:end
// example:fix_div:start
result[3]=fix_div(768,512);
// example:fix_div:end
// example:fix_lerp:start
result[4]=fix_lerp(0,1024,128);
// example:fix_lerp:end
// example:kq_abs_s16:start
result[5]=kq_abs_s16(-123);
// example:kq_abs_s16:end
// example:kq_min_s16:start
result[6]=kq_min_s16(-7,4);
// example:kq_min_s16:end
// example:kq_max_s16:start
result[7]=kq_max_s16(-7,4);
// example:kq_max_s16:end
// example:kq_clamp_s16:start
result[8]=kq_clamp_s16(25,-10,10);
// example:kq_clamp_s16:end
// example:kq_rect_intersect:start
result[9]=kq_rect_intersect(a,b);
// example:kq_rect_intersect:end
// example:kq_point_in_rect:start
result[10]=kq_point_in_rect(16,8,a);
// example:kq_point_in_rect:end
result[11]=fix_mul(271,271);
result[12]=fix_div(256,0);
result[13]=fix_lerp(0,1024,255);
result[14]=kq_point_in_rect(8,8,a);
result[15]=kq_point_in_rect(8,16,a);
result[16]=kq_rect_intersect(a,touch);
result[17]=fix_to_int(-1);
result[18]=kq_clamp_s16(-11,-10,10);
result[19]=kq_clamp_s16(3,-10,10);


demo_label(0,"FIXED / COLLISION");
demo_label(2,"-3 RAW");if((result[0]&0x8000)!=0){m_put(12,2,45);demo_word(2,(u16)(0-result[0]));}else demo_word(2,result[0]);
demo_label(4,"-1.5 FLOOR");if((result[1]&0x8000)!=0){m_put(12,4,45);demo_word(4,(u16)(0-result[1]));}else demo_word(4,result[1]);
demo_label(6,"1.5 X 2");if((result[2]&0x8000)!=0){m_put(12,6,45);demo_word(6,(u16)(0-result[2]));}else demo_word(6,result[2]);
demo_label(8,"3 / 2 RAW");if((result[3]&0x8000)!=0){m_put(12,8,45);demo_word(8,(u16)(0-result[3]));}else demo_word(8,result[3]);
demo_label(10,"HALF OF 4");if((result[4]&0x8000)!=0){m_put(12,10,45);demo_word(10,(u16)(0-result[4]));}else demo_word(10,result[4]);
demo_label(12,"OVERLAP");if((result[9]&0x8000)!=0){m_put(12,12,45);demo_word(12,(u16)(0-result[9]));}else demo_word(12,result[9]);
demo_label(14,"RIGHT EDGE");if((result[10]&0x8000)!=0){m_put(12,14,45);demo_word(14,(u16)(0-result[10]));}else demo_word(14,result[10]);
demo_label(16,"SIGNED RAW VALUES");
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
