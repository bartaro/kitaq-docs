// math: Exercise the APIs and compare the documented results.
#include "fc_common.h"
#include "intrinsics.h"
__location(0x0600) u16 result[80];
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
u16 v0;u16 v1;u16 v2;u8 v3;u8 v4;u8 v5;
void main(){u8 i;u8 x;u8 y;__ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();__palette_bg_load(manual_pal);__nametable_rect(0,0,32,30,0);for(i=0;i<80;i++)result[i]=0;

// example:__mul8x8_hi:start
// Compare literal coefficients with values read from RAM.
result[0]=__mul8x8_hi(255,255);
v0=255;v1=255;
result[1]=__mul8x8_hi(v0,v1);
// example:__mul8x8_hi:end

// example:__mul16x8:start
// Compare literal coefficients with values read from RAM.
result[2]=__mul16x8(513,127);
v0=513;v1=127;
result[3]=__mul16x8(v0,v1);
// example:__mul16x8:end

// example:__smul16x8:start
// Compare literal coefficients with values read from RAM.
result[4]=__smul16x8(-513,-64);
v0=-513;v1=-64;
result[5]=__smul16x8(v0,v1);
// Reverse coefficient signs and verify negative products.
result[6]=__smul16x8(-513,64);
v0=-513;v1=64;
result[7]=__smul16x8(v0,v1);
// example:__smul16x8:end

// example:__mac16:start
// Compare literal coefficients with values read from RAM.
result[8]=__mac16(65500,513,127);
v0=65500;v1=513;v2=127;
result[9]=__mac16(v0,v1,v2);
// example:__mac16:end

// example:__smac16:start
// Compare literal coefficients with values read from RAM.
result[10]=__smac16(65500,-513,-64);
v0=65500;v1=-513;v2=-64;
result[11]=__smac16(v0,v1,v2);
// Reverse coefficient signs and verify negative products.
result[12]=__smac16(65500,-513,64);
v0=65500;v1=-513;v2=64;
result[13]=__smac16(v0,v1,v2);
// example:__smac16:end

// example:__smul16x8_q1_7:start
// Compare literal coefficients with values read from RAM.
result[14]=__smul16x8_q1_7(-513,-64);
v0=-513;v1=-64;
result[15]=__smul16x8_q1_7(v0,v1);
// Reverse coefficient signs and verify negative products.
result[16]=__smul16x8_q1_7(-513,64);
v0=-513;v1=64;
result[17]=__smul16x8_q1_7(v0,v1);
// example:__smul16x8_q1_7:end

// example:__smac16_q1_7:start
// Compare literal coefficients with values read from RAM.
result[18]=__smac16_q1_7(65500,-513,-64);
v0=65500;v1=-513;v2=-64;
result[19]=__smac16_q1_7(v0,v1,v2);
// Reverse coefficient signs and verify negative products.
result[20]=__smac16_q1_7(65500,-513,64);
v0=65500;v1=-513;v2=64;
result[21]=__smac16_q1_7(v0,v1,v2);
// example:__smac16_q1_7:end

// example:__dot2_q8_8:start
// Compare literal coefficients with values read from RAM.
result[22]=__dot2_q8_8(513,769,64,127);
v0=513;v1=769;v2=64;v3=127;
result[23]=__dot2_q8_8(v0,v1,v2,v3);
// example:__dot2_q8_8:end

// example:__dot3_q8_8:start
// Compare literal coefficients with values read from RAM.
result[24]=__dot3_q8_8(513,769,1025,64,127,3);
v0=513;v1=769;v2=1025;v3=64;v4=127;v5=3;
result[25]=__dot3_q8_8(v0,v1,v2,v3,v4,v5);
// example:__dot3_q8_8:end

// example:__sdot2_q8_8:start
// Compare literal coefficients with values read from RAM.
result[26]=__sdot2_q8_8(-513,769,-64,127);
v0=-513;v1=769;v2=-64;v3=127;
result[27]=__sdot2_q8_8(v0,v1,v2,v3);
// Reverse coefficient signs and verify negative products.
result[28]=__sdot2_q8_8(-513,769,64,-127);
v0=-513;v1=769;v2=64;v3=-127;
result[29]=__sdot2_q8_8(v0,v1,v2,v3);
// example:__sdot2_q8_8:end

// example:__sdot3_q8_8:start
// Compare literal coefficients with values read from RAM.
result[30]=__sdot3_q8_8(-513,769,-1025,-64,127,-3);
v0=-513;v1=769;v2=-1025;v3=-64;v4=127;v5=-3;
result[31]=__sdot3_q8_8(v0,v1,v2,v3,v4,v5);
// Reverse coefficient signs and verify negative products.
result[32]=__sdot3_q8_8(-513,769,-1025,64,-127,3);
v0=-513;v1=769;v2=-1025;v3=64;v4=-127;v5=3;
result[33]=__sdot3_q8_8(v0,v1,v2,v3,v4,v5);
// example:__sdot3_q8_8:end

// example:__sdot2_q1_7:start
// Compare literal coefficients with values read from RAM.
result[34]=__sdot2_q1_7(-513,769,-64,127);
v0=-513;v1=769;v2=-64;v3=127;
result[35]=__sdot2_q1_7(v0,v1,v2,v3);
// Reverse coefficient signs and verify negative products.
result[36]=__sdot2_q1_7(-513,769,64,-127);
v0=-513;v1=769;v2=64;v3=-127;
result[37]=__sdot2_q1_7(v0,v1,v2,v3);
// example:__sdot2_q1_7:end

// example:__sdot3_q1_7:start
// Compare literal coefficients with values read from RAM.
result[38]=__sdot3_q1_7(-513,769,-1025,-64,127,-3);
v0=-513;v1=769;v2=-1025;v3=-64;v4=127;v5=-3;
result[39]=__sdot3_q1_7(v0,v1,v2,v3,v4,v5);
// Reverse coefficient signs and verify negative products.
result[40]=__sdot3_q1_7(-513,769,-1025,64,-127,3);
v0=-513;v1=769;v2=-1025;v3=64;v4=-127;v5=3;
result[41]=__sdot3_q1_7(v0,v1,v2,v3,v4,v5);
// example:__sdot3_q1_7:end

m_text(1,0,"INTEGER MATH");__vramq_commit();__vramq_exec();
m_text(1,2,"mul8x8_hi");demo_word(2,result[0]);__vramq_commit();__vramq_exec();
m_text(1,4,"mul16x8");demo_word(4,result[2]);__vramq_commit();__vramq_exec();
m_text(1,6,"smul16x8");demo_word(6,result[4]);__vramq_commit();__vramq_exec();
m_text(1,8,"mac16");demo_word(8,result[8]);__vramq_commit();__vramq_exec();
m_text(1,10,"smac16");demo_word(10,result[10]);__vramq_commit();__vramq_exec();
m_text(1,12,"smul16x8Q7");demo_word(12,result[14]);__vramq_commit();__vramq_exec();
m_text(1,14,"smac16Q7");demo_word(14,result[18]);__vramq_commit();__vramq_exec();
m_text(1,16,"dot2");demo_word(16,result[22]);__vramq_commit();__vramq_exec();
result[79]=0xA55A;__scroll_set(0,0);__ppu_ctrl_set(0);__ppu_mask_set(0x0A);while(1){}
}
