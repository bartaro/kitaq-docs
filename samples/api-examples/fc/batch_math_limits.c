// math_limits demonstrates a complete, reproducible library workflow.
#include "fc_common.h"
__prg_rom u8 demo_palette[16]={15,34,34,34,15,34,34,34,15,34,34,34,15,34,34,34};
#include "fixed.c"
__location(0x0600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);__vramq_commit();__vramq_exec();}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}__vramq_commit();__vramq_exec();}

void main(){u8 i;__ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();__palette_bg_load(demo_palette);__nametable_rect(0,0,32,30,0);for(i=0;i<80;i++)result[i]=0;
// example:kq_abs_s16:start
result[0]=kq_abs_s16(-123);
// example:kq_abs_s16:end
// example:kq_min_s16:start
result[1]=kq_min_s16(-7,4);
// example:kq_min_s16:end
// example:kq_max_s16:start
result[2]=kq_max_s16(-7,4);
// example:kq_max_s16:end
// example:kq_clamp_s16:start
result[3]=kq_clamp_s16(25,-10,10);
// example:kq_clamp_s16:end
result[4]=kq_clamp_s16(-11,-10,10);result[5]=kq_clamp_s16(3,-10,10);

demo_label(0,"MAGNITUDE / LIMITS");
demo_label(2,"ABS -123");if((result[0]&0x8000)!=0){m_put(12,2,45);__vramq_commit();__vramq_exec();demo_word(2,(u16)(0-result[0]));}else demo_word(2,result[0]);
demo_label(4,"MIN -7,4");if((result[1]&0x8000)!=0){m_put(12,4,45);__vramq_commit();__vramq_exec();demo_word(4,(u16)(0-result[1]));}else demo_word(4,result[1]);
demo_label(6,"MAX -7,4");if((result[2]&0x8000)!=0){m_put(12,6,45);__vramq_commit();__vramq_exec();demo_word(6,(u16)(0-result[2]));}else demo_word(6,result[2]);
demo_label(8,"CLAMP 25");if((result[3]&0x8000)!=0){m_put(12,8,45);__vramq_commit();__vramq_exec();demo_word(8,(u16)(0-result[3]));}else demo_word(8,result[3]);
demo_label(10,"CLAMP -11");if((result[4]&0x8000)!=0){m_put(12,10,45);__vramq_commit();__vramq_exec();demo_word(10,(u16)(0-result[4]));}else demo_word(10,result[4]);
demo_label(12,"CLAMP 3");if((result[5]&0x8000)!=0){m_put(12,12,45);__vramq_commit();__vramq_exec();demo_word(12,(u16)(0-result[5]));}else demo_word(12,result[5]);
demo_label(14,"RANGE -10 TO 10");
demo_label(16,"SIGNED RAW VALUES");
result[79]=0xA55A;__scroll_set(0,0);__ppu_mask_set(0x0A);while(1){}
}
