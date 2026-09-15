// chain demonstrates a complete, reproducible library workflow.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "chain.c"
__location(0xC600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
Chain trail;ChainPoint storage[4];ChainPoint point;
void main(){u8 i;tile_example_begin();M_LCDC=0;vram_example_color(1,2,18,14,2);for(i=0;i<80;i++)result[i]=0;
// example:chain_init:start
chain_init(&trail,storage,4);result[0]=chain_get_count(&trail);
// example:chain_init:end
// example:chain_push_head:start
chain_push_head(&trail,8,8);chain_push_head(&trail,16,8);chain_push_head(&trail,24,16);chain_push_head(&trail,32,16);chain_push_head(&trail,40,24);
// example:chain_push_head:end
// example:chain_get_segment:start
result[1]=chain_get_segment(&trail,0,&point);result[2]=point.x;result[3]=point.y;
// example:chain_get_segment:end
// example:chain_get_count:start
result[4]=chain_get_count(&trail);
// example:chain_get_count:end
result[5]=chain_get_segment(&trail,3,&point);result[6]=point.x;result[7]=point.y;result[8]=chain_get_segment(&trail,4,&point);result[9]=point.x;result[10]=point.y;
// example:chain_clear:start
chain_clear(&trail);result[11]=chain_get_count(&trail);
// example:chain_clear:end
chain_init(&trail,storage,0);chain_push_head(&trail,1,2);result[12]=chain_get_count(&trail);result[13]=chain_get_segment(&trail,0,&point);result[14]=chain_get_count(0);

demo_label(0,"POSITION HISTORY");
demo_label(2,"NEWEST X");demo_word(2,result[2]);
demo_label(4,"NEWEST Y");demo_word(4,result[3]);
demo_label(6,"SAVED POINTS");demo_word(6,result[4]);
demo_label(8,"OLDEST X");demo_word(8,result[6]);
demo_label(10,"INVALID READ");demo_word(10,result[8]);
demo_label(12,"AFTER CLEAR");demo_word(12,result[11]);
demo_label(14,"5 PUSHES / 4 SLOTS");
demo_label(16,"OLDEST REPLACED");
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
