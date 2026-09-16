// metatile: Exercise the APIs and compare the documented results.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "map.c"
__location(0xC600) u16 result[80];
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
u8 ids[6];metatile_t defs[2];metatile_map_t level;
void main(){u8 i;u8 x;u8 y;tile_example_begin();M_LCDC=0;for(i=0;i<80;i++)result[i]=0;
__vram_fill(0x87E0,255,16);__memset(ids,0,6);__memset(defs,0,sizeof(defs));defs[1].tile_tl=126;defs[1].tile_tr=126;defs[1].tile_bl=126;defs[1].tile_br=126;defs[1].collision=1;defs[1].palette=3;defs[1].event=7;ids[0]=1;level.width=3;level.height=2;level.bank_tiles=0;level.metatile_ids=ids;level.metatiles=defs;
// example:map_load_metatile:start
map_load_metatile(0,&level);result[0]=*((u8*)0x9800);
// example:map_load_metatile:end

// example:map_get_metatile:start
result[1]=map_get_metatile(0,0);result[2]=map_get_metatile(3,0);
// example:map_get_metatile:end

// example:map_get_attr:start
result[3]=map_get_attr(0,0);
// example:map_get_attr:end

// example:map_is_solid:start
result[4]=map_is_solid(0,0);result[5]=map_is_solid(1,0);result[6]=map_is_solid(3,0);
// example:map_is_solid:end

// example:map_get_event:start
result[7]=map_get_event(0,0);result[8]=map_get_event(3,0);
// example:map_get_event:end

// example:map_draw_visible:start
map_draw_visible(1,0);result[9]=*((u8*)0x9800);
// example:map_draw_visible:end

// example:map_mark_dirty:start
ids[1]=1;map_mark_dirty(1,0);result[10]=*((u8*)0x9800);
// example:map_mark_dirty:end

// example:map_flush_dirty:start
map_flush_dirty();result[11]=*((u8*)0x9800);
// example:map_flush_dirty:end
// Palette metadata is applied by this application, independently of map drawing.
vram_example_color(0,0,2,2,map_get_attr(1,0));
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
