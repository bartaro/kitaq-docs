// services demonstrates a complete, reproducible library workflow.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "system.c"
#include "scene.c"
__location(0xC600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
u8 frame_calls;u16 frame_seen;u8 events;u8 event_log[16];void on_frame(){frame_calls++;frame_seen=system_get_frame();}void event(u8 n){event_log[events]=n;events++;}void enter0(){event(10);}void update0(){event(11);}void draw0(){event(12);}void exit0(){event(13);}void enter1(){event(20);}void update1(){event(21);}void draw1(){event(22);}void exit1(){event(23);}SceneDef scenes[2];
void main(){u8 i;tile_example_begin();M_LCDC=0;vram_example_color(1,2,18,14,2);for(i=0;i<80;i++)result[i]=0;scenes[0].enter=enter0;scenes[0].update=update0;scenes[0].draw=draw0;scenes[0].exit=exit0;scenes[1].enter=enter1;scenes[1].update=update1;scenes[1].draw=draw1;scenes[1].exit=exit1;M_LCDC=0x91;
// example:system_init:start
system_init();result[0]=system_get_frame();
// example:system_init:end
// example:system_set_vblank_callback:start
system_set_vblank_callback(on_frame);
// example:system_set_vblank_callback:end
// example:system_wait_vblank:start
system_wait_vblank();system_wait_vblank();system_wait_vblank();result[1]=frame_calls;result[2]=frame_seen;
// example:system_wait_vblank:end
// example:system_get_frame:start
result[3]=system_get_frame();
// example:system_get_frame:end
// example:system_get_frame8:start
result[4]=system_get_frame8();
// example:system_get_frame8:end
// example:system_disable_interrupts:start
system_disable_interrupts();
// example:system_disable_interrupts:end
// example:system_enable_interrupts:start
system_enable_interrupts();
// example:system_enable_interrupts:end
system_set_vblank_callback(0);system_wait_vblank();result[5]=frame_calls;result[6]=system_get_frame();kq_system_frame=65535;system_wait_vblank();result[7]=system_get_frame();result[8]=system_get_frame8();
// example:scene_init:start
scene_init(scenes,2);scene_update();scene_draw();result[9]=events;result[10]=scene_was_changed();
// example:scene_init:end
// example:scene_change:start
scene_change(0);scene_change(9);result[11]=events;result[12]=scene_was_changed();
// example:scene_change:end
// example:scene_update:start
scene_update();result[13]=events;result[14]=scene_was_changed();
// example:scene_update:end
// example:scene_draw:start
scene_draw();result[15]=events;
// example:scene_draw:end
// example:scene_get_current:start
result[16]=scene_get_current();
// example:scene_get_current:end
// example:scene_was_changed:start
result[17]=scene_was_changed();
// example:scene_was_changed:end
scene_change(1);result[18]=events;result[19]=scene_get_current();result[20]=scene_was_changed();scene_update();scene_draw();result[21]=events;scene_change(1);result[22]=events;
// example:scene_set_table:start
scene_set_table(scenes,2);result[23]=events;result[24]=scene_was_changed();scene_draw();result[25]=events;
// example:scene_set_table:end
for(i=0;i<events;i++)result[26+i]=event_log[i];
// Stop the LCD during VBlank before preparing the final static screen.
__wait_vblank();M_LCDC=0;
demo_label(0,"FRAMES AND SCENES");
demo_label(2,"FRAME CALLS");demo_word(2,result[1]);
demo_label(4,"CALLBACK SAW");demo_word(4,result[2]);
demo_label(6,"AFTER NULL");demo_word(6,result[5]);
demo_label(8,"WRAP FRAME");demo_word(8,result[7]);
demo_label(10,"SCENE EVENTS");demo_word(10,result[22]);
demo_label(12,"FINAL SCENE");demo_word(12,result[19]);
demo_label(14,"10 11 12 13 20");
demo_label(16,"21 22 23 20");
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
