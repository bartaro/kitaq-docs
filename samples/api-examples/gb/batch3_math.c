// math: Exercise the APIs and compare the documented results.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
__location(0xC600) u16 result[80];
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
u16 v0;u16 v1;u16 v2;u8 v3;u8 v4;u8 v5;
void main(){u8 i;u8 x;u8 y;tile_example_begin();M_LCDC=0;for(i=0;i<80;i++)result[i]=0;

// example:__smac16_q1_7:start
// Compare literal coefficients with values read from RAM.
result[0]=__smac16_q1_7(65500,-513,-64);
v0=65500;v1=-513;v2=-64;
result[1]=__smac16_q1_7(v0,v1,v2);
// Reverse coefficient signs and verify negative products.
result[2]=__smac16_q1_7(65500,-513,64);
v0=65500;v1=-513;v2=64;
result[3]=__smac16_q1_7(v0,v1,v2);
// example:__smac16_q1_7:end

// example:__mul8x8_hi:start
// Compare literal coefficients with values read from RAM.
result[4]=__mul8x8_hi(255,255);
v0=255;v1=255;
result[5]=__mul8x8_hi(v0,v1);
// example:__mul8x8_hi:end

// example:__dot3_q8_8:start
// Compare literal coefficients with values read from RAM.
result[6]=__dot3_q8_8(513,769,1025,64,127,3);
v0=513;v1=769;v2=1025;v3=64;v4=127;v5=3;
result[7]=__dot3_q8_8(v0,v1,v2,v3,v4,v5);
// example:__dot3_q8_8:end

// example:__sdot3_q8_8:start
// Compare literal coefficients with values read from RAM.
result[8]=__sdot3_q8_8(-513,769,-1025,-64,127,-3);
v0=-513;v1=769;v2=-1025;v3=-64;v4=127;v5=-3;
result[9]=__sdot3_q8_8(v0,v1,v2,v3,v4,v5);
// Reverse coefficient signs and verify negative products.
result[10]=__sdot3_q8_8(-513,769,-1025,64,-127,3);
v0=-513;v1=769;v2=-1025;v3=64;v4=-127;v5=3;
result[11]=__sdot3_q8_8(v0,v1,v2,v3,v4,v5);
// example:__sdot3_q8_8:end

// example:__smul16x8_q1_7:start
// Compare literal coefficients with values read from RAM.
result[12]=__smul16x8_q1_7(-513,-64);
v0=-513;v1=-64;
result[13]=__smul16x8_q1_7(v0,v1);
// Reverse coefficient signs and verify negative products.
result[14]=__smul16x8_q1_7(-513,64);
v0=-513;v1=64;
result[15]=__smul16x8_q1_7(v0,v1);
// example:__smul16x8_q1_7:end

// example:__sdot3_q1_7:start
// Compare literal coefficients with values read from RAM.
result[16]=__sdot3_q1_7(-513,769,-1025,-64,127,-3);
v0=-513;v1=769;v2=-1025;v3=-64;v4=127;v5=-3;
result[17]=__sdot3_q1_7(v0,v1,v2,v3,v4,v5);
// Reverse coefficient signs and verify negative products.
result[18]=__sdot3_q1_7(-513,769,-1025,64,-127,3);
v0=-513;v1=769;v2=-1025;v3=64;v4=-127;v5=3;
result[19]=__sdot3_q1_7(v0,v1,v2,v3,v4,v5);
// example:__sdot3_q1_7:end

// example:__sdot2_q1_7:start
// Compare literal coefficients with values read from RAM.
result[20]=__sdot2_q1_7(-513,769,-64,127);
v0=-513;v1=769;v2=-64;v3=127;
result[21]=__sdot2_q1_7(v0,v1,v2,v3);
// Reverse coefficient signs and verify negative products.
result[22]=__sdot2_q1_7(-513,769,64,-127);
v0=-513;v1=769;v2=64;v3=-127;
result[23]=__sdot2_q1_7(v0,v1,v2,v3);
// example:__sdot2_q1_7:end

// example:__mul16x8:start
// Compare literal coefficients with values read from RAM.
result[24]=__mul16x8(513,127);
v0=513;v1=127;
result[25]=__mul16x8(v0,v1);
// example:__mul16x8:end

// example:__smac16:start
// Compare literal coefficients with values read from RAM.
result[26]=__smac16(65500,-513,-64);
v0=65500;v1=-513;v2=-64;
result[27]=__smac16(v0,v1,v2);
// Reverse coefficient signs and verify negative products.
result[28]=__smac16(65500,-513,64);
v0=65500;v1=-513;v2=64;
result[29]=__smac16(v0,v1,v2);
// example:__smac16:end

// example:__sdot2_q8_8:start
// Compare literal coefficients with values read from RAM.
result[30]=__sdot2_q8_8(-513,769,-64,127);
v0=-513;v1=769;v2=-64;v3=127;
result[31]=__sdot2_q8_8(v0,v1,v2,v3);
// Reverse coefficient signs and verify negative products.
result[32]=__sdot2_q8_8(-513,769,64,-127);
v0=-513;v1=769;v2=64;v3=-127;
result[33]=__sdot2_q8_8(v0,v1,v2,v3);
// example:__sdot2_q8_8:end

// example:__mac16:start
// Compare literal coefficients with values read from RAM.
result[34]=__mac16(65500,513,127);
v0=65500;v1=513;v2=127;
result[35]=__mac16(v0,v1,v2);
// example:__mac16:end

// example:__dot2_q8_8:start
// Compare literal coefficients with values read from RAM.
result[36]=__dot2_q8_8(513,769,64,127);
v0=513;v1=769;v2=64;v3=127;
result[37]=__dot2_q8_8(v0,v1,v2,v3);
// example:__dot2_q8_8:end

m_text(1,0,"FIXED MATH");
m_text(1,2,"smac16Q7");demo_word(2,result[0]);
m_text(1,4,"mul8x8_hi");demo_word(4,result[4]);
m_text(1,6,"dot3");demo_word(6,result[6]);
m_text(1,8,"sdot3");demo_word(8,result[8]);
m_text(1,10,"smul16x8Q7");demo_word(10,result[12]);
m_text(1,12,"sdot3Q7");demo_word(12,result[16]);
m_text(1,14,"sdot2Q7");demo_word(14,result[20]);
m_text(1,16,"mul16x8");demo_word(16,result[24]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
