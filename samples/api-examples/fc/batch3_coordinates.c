// coordinates: Exercise the APIs and compare the documented results.
#include "fc_common.h"
#include "intrinsics.h"
__location(0x0600) u16 result[80];
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}

void main(){u8 i;u8 x;u8 y;__ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();__palette_bg_load(manual_pal);__nametable_rect(0,0,32,30,0);for(i=0;i<80;i++)result[i]=0;

// example:__xy_in_rect:start
result[0]=__xy_in_rect(10,20,10,20,3,2);result[1]=__xy_in_rect(13,20,10,20,3,2);result[2]=__xy_in_rect(9,20,10,20,3,2);result[3]=__xy_in_rect(255,1,250,0,10,2);result[4]=__xy_in_rect(10,20,10,20,0,2);
// example:__xy_in_rect:end

// example:__manhattan:start
result[5]=__manhattan(2,3,9,11);result[6]=__manhattan(0,0,255,255);
// example:__manhattan:end

// example:__map_index:start
result[7]=__map_index(4,3,20);result[8]=__map_index(255,255,255);
// example:__map_index:end

m_text(1,0,"COORDINATES");__vramq_commit();__vramq_exec();
m_text(1,2,"INSIDE");demo_word(2,result[0]);__vramq_commit();__vramq_exec();
m_text(1,4,"RIGHT EDGE");demo_word(4,result[1]);__vramq_commit();__vramq_exec();
m_text(1,6,"LEFT EDGE");demo_word(6,result[2]);__vramq_commit();__vramq_exec();
m_text(1,8,"HIGH X");demo_word(8,result[3]);__vramq_commit();__vramq_exec();
m_text(1,10,"DISTANCE");demo_word(10,result[5]);__vramq_commit();__vramq_exec();
m_text(1,12,"WRAP DIST");demo_word(12,result[6]);__vramq_commit();__vramq_exec();
m_text(1,14,"MAP INDEX");demo_word(14,result[7]);__vramq_commit();__vramq_exec();
m_text(1,16,"MAX INDEX");demo_word(16,result[8]);__vramq_commit();__vramq_exec();
result[79]=0xA55A;__scroll_set(0,0);__ppu_ctrl_set(0);__ppu_mask_set(0x0A);while(1){}
}
