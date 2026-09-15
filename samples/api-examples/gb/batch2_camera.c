// camera demonstrates a complete, reproducible library workflow.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "scroll.c"
#include "camera.c"
__location(0xC600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
Camera8_8 cam;__location(0xFF43) u8 M_SCX;__location(0xFF42) u8 M_SCY;
void main(){u8 i;tile_example_begin();M_LCDC=0;vram_example_color(1,2,18,14,2);for(i=0;i<80;i++)result[i]=0;
// example:Camera_Init:start
Camera_Init(&cam);result[0]=cam.fx;result[1]=cam.use_target;result[2]=cam.use_bounds;
// example:Camera_Init:end
// example:Camera_Set:start
Camera_Set(&cam,2560,5120);result[3]=cam.fx;result[4]=cam.fy;
// example:Camera_Set:end
// example:Camera_SetTarget:start
Camera_SetTarget(&cam,4608,3072);result[5]=cam.use_target;
// example:Camera_SetTarget:end
// example:Camera_StepTowardTarget:start
Camera_StepTowardTarget(&cam,1);result[6]=cam.fx;result[7]=cam.fy;
// example:Camera_StepTowardTarget:end
// example:Camera_ClearTarget:start
Camera_ClearTarget(&cam);result[8]=cam.use_target;result[9]=cam.target_fx;
// example:Camera_ClearTarget:end
// example:Camera_SetBounds:start
Camera_SetBounds(&cam,0,0,3072,3584);result[10]=cam.fx;result[11]=cam.fy;
// example:Camera_SetBounds:end
// example:Camera_ClearBounds:start
Camera_ClearBounds(&cam);result[12]=cam.use_bounds;
// example:Camera_ClearBounds:end
// example:Camera_Add:start
Camera_Add(&cam,256,512);result[13]=cam.fx;result[14]=cam.fy;
// example:Camera_Add:end
// example:Camera_ClampToSize:start
Camera_ClampToSize(&cam,176,160,160,144);result[15]=cam.max_fx;result[16]=cam.max_fy;
// example:Camera_ClampToSize:end
// example:Camera_WorldToScreenX:start
result[17]=Camera_WorldToScreenX(&cam,40);
// example:Camera_WorldToScreenX:end
// example:Camera_WorldToScreenY:start
result[18]=Camera_WorldToScreenY(&cam,40);
// example:Camera_WorldToScreenY:end
// example:Camera_ScreenToWorldX:start
result[19]=Camera_ScreenToWorldX(&cam,27);
// example:Camera_ScreenToWorldX:end
// example:Camera_ScreenToWorldY:start
result[20]=Camera_ScreenToWorldY(&cam,24);
// example:Camera_ScreenToWorldY:end
// example:Camera_ApplyBg:start
Camera_ApplyBg(&cam);result[21]=M_SCX;result[22]=M_SCY;
// example:Camera_ApplyBg:end
// example:Camera_ApplyBgBuffered:start
Camera_Set(&cam,2048,4096);Camera_ApplyBgBuffered(&cam);result[23]=M_SCX;Scroll_Flush();result[24]=M_SCX;result[25]=M_SCY;
// example:Camera_ApplyBgBuffered:end
// example:camera_set:start
camera_set(5,6);result[26]=camera_world_to_screen_x(20);
// example:camera_set:end
// example:camera_follow_xy:start
camera_follow_xy(100,90,80,72);result[27]=camera_world_to_screen_x(100);result[28]=camera_world_to_screen_y(90);
// example:camera_follow_xy:end
// example:camera_clamp:start
camera_clamp(176,160,160,144);result[29]=camera_world_to_screen_x(100);result[30]=camera_world_to_screen_y(90);
// example:camera_clamp:end
// example:camera_apply:start
camera_apply();result[31]=M_SCX;result[32]=M_SCY;
// example:camera_apply:end
// example:camera_world_to_screen_x:start
result[33]=camera_world_to_screen_x(20);
// example:camera_world_to_screen_x:end
// example:camera_world_to_screen_y:start
result[34]=camera_world_to_screen_y(20);
// example:camera_world_to_screen_y:end

Scroll_SetBg(0,0);
demo_label(0,"CAMERA / Q8.8");
demo_label(2,"FOLLOW X RAW");demo_word(2,result[6]);
demo_label(4,"FOLLOW Y RAW");demo_word(4,result[7]);
demo_label(6,"BOUND X RAW");demo_word(6,result[10]);
demo_label(8,"BOUND Y RAW");demo_word(8,result[11]);
demo_label(10,"WORLD TO X");demo_word(10,result[17]);
demo_label(12,"STAGED X");demo_word(12,result[23]);
demo_label(14,"FLUSHED X");demo_word(14,result[24]);
demo_label(16,"SHARED X");demo_word(16,result[31]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
