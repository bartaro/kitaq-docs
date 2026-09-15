// debug demonstrates a complete, reproducible library workflow.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "debug.c"
__location(0xC600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
const DebugTraceEntry* entries;u8 side_effect;
void main(){u8 i;tile_example_begin();M_LCDC=0;vram_example_color(1,2,18,14,2);for(i=0;i<80;i++)result[i]=0;
// example:debug_init:start
debug_init();result[0]=debug_get_trace_count();
// example:debug_init:end
// example:debug_set_frame:start
debug_set_frame(513);
// example:debug_set_frame:end
// example:debug_mark_frame:start
debug_mark_frame("BEGIN");
// example:debug_mark_frame:end
// example:debug_trace_u8:start
debug_trace_u8("BYTE",255);
// example:debug_trace_u8:end
// example:debug_trace_u16:start
debug_trace_u16("WORD",4660);
// example:debug_trace_u16:end
// example:debug_assert_fail:start
debug_assert_fail(42);
// example:debug_assert_fail:end
// example:KITAQGB_TRACE_U8:start
KITAQGB_TRACE_U8("CAST",0x1234);
// example:KITAQGB_TRACE_U8:end
// example:KITAQGB_TRACE_U16:start
KITAQGB_TRACE_U16("WORD2",500);
// example:KITAQGB_TRACE_U16:end
// example:KITAQGB_TRACE:start
KITAQGB_TRACE("SCORE",600);
// example:KITAQGB_TRACE:end
// example:KITAQGB_MARK_FRAME:start
KITAQGB_MARK_FRAME("END");
// example:KITAQGB_MARK_FRAME:end
// example:KITAQGB_ASSERT:start
KITAQGB_ASSERT(1);KITAQGB_ASSERT(0);
// example:KITAQGB_ASSERT:end
// example:KITAQGB_ASSERT_CODE:start
KITAQGB_ASSERT_CODE(1,++side_effect);KITAQGB_ASSERT_CODE(0,77);
// example:KITAQGB_ASSERT_CODE:end
// example:debug_get_trace_count:start
result[1]=debug_get_trace_count();
// example:debug_get_trace_count:end
// example:debug_get_trace_log:start
entries=debug_get_trace_log();for(i=0;i<10;i++){result[2+i]=entries[i].value;result[12+i]=entries[i].frame;}
// example:debug_get_trace_log:end
// example:debug_get_last_assert:start
result[22]=debug_get_last_assert();
// example:debug_get_last_assert:end
result[23]=side_effect;result[24]=entries[0].name[0];for(i=0;i<40;i++)debug_trace_u8("FULL",i);debug_assert_fail(999);result[25]=debug_get_trace_count();result[26]=debug_get_last_assert();result[27]=entries[31].value;debug_init();result[28]=debug_get_trace_count();result[29]=debug_get_last_assert();result[30]=entries[0].value;

demo_label(0,"BOUNDED TRACE LOG");
demo_label(2,"BEGIN");demo_word(2,result[2]);
demo_label(3,"BYTE");demo_word(3,result[3]);
demo_label(4,"WORD");demo_word(4,result[4]);
demo_label(5,"ASSERT 42");demo_word(5,result[5]);
demo_label(6,"BYTE CAST");demo_word(6,result[6]);
demo_label(7,"WORD2");demo_word(7,result[7]);
demo_label(8,"SCORE");demo_word(8,result[8]);
demo_label(9,"END");demo_word(9,result[9]);
demo_label(10,"ASSERT 1");demo_word(10,result[10]);
demo_label(11,"ASSERT 77");demo_word(11,result[11]);
demo_label(12,"FRAME TAG");demo_word(12,result[12]);
demo_label(13,"FULL COUNT");demo_word(13,result[25]);
demo_label(14,"LAST ASSERT");demo_word(14,result[26]);
demo_label(15,"RESET COUNT");demo_word(15,result[28]);
demo_label(16,"FULL LOG DROPS NEW");
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
