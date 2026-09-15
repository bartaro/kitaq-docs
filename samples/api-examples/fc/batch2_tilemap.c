// tilemap demonstrates a complete, reproducible library workflow.
#include "fc_common.h"
__prg_rom u8 demo_palette[16]={15,34,34,34,15,34,34,34,15,34,34,34,15,34,34,34};
#include "tilemap.c"
__location(0x0600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);__vramq_commit();__vramq_exec();}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}__vramq_commit();__vramq_exec();}
struct NesTilemap map;u8 tiles[15];
void main(){u8 i;__ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();__palette_bg_load(demo_palette);__nametable_rect(0,0,32,30,0);for(i=0;i<80;i++)result[i]=0;for(i=0;i<15;i++)tiles[i]=0;tiles[7]=5;map.tiles=tiles;map.width=5;map.height=3;map.solid_from=5;
// example:nes_tilemap_index:start
result[0]=nes_tilemap_index(&map,2,1);
// example:nes_tilemap_index:end
// example:nes_tilemap_get:start
result[1]=nes_tilemap_get(&map,2,1);result[2]=nes_tilemap_get(&map,5,1);
// example:nes_tilemap_get:end
// example:nes_tilemap_point_solid:start
result[3]=nes_tilemap_point_solid(&map,2,1);result[4]=nes_tilemap_point_solid(&map,0,0);result[5]=nes_tilemap_point_solid(&map,5,0);
// example:nes_tilemap_point_solid:end
// example:nes_world_to_tile8_x:start
result[6]=nes_world_to_tile8_x(23);result[7]=nes_world_to_tile8_x(24);
// example:nes_world_to_tile8_x:end
// example:nes_world_to_tile8_y:start
result[8]=nes_world_to_tile8_y(15);result[9]=nes_world_to_tile8_y(16);
// example:nes_world_to_tile8_y:end
// example:nes_tilemap_world_point_solid:start
result[10]=nes_tilemap_world_point_solid(&map,16,8);result[11]=nes_tilemap_world_point_solid(&map,0,0);
// example:nes_tilemap_world_point_solid:end
// example:nes_tilemap_world_box_solid:start
result[12]=nes_tilemap_world_box_solid(&map,8,8,16,8);result[13]=nes_tilemap_world_box_solid(&map,0,0,40,24);
// example:nes_tilemap_world_box_solid:end


demo_label(0,"TILEMAP / COLLISION");
demo_label(2,"INDEX 2 1");demo_word(2,result[0]);
demo_label(4,"TILE 2 1");demo_word(4,result[1]);
demo_label(6,"OUTSIDE");demo_word(6,result[2]);
demo_label(8,"SOLID POINT");demo_word(8,result[10]);
demo_label(10,"CORNER HIT");demo_word(10,result[12]);
demo_label(12,"INNER ONLY");demo_word(12,result[13]);
demo_label(14,"BOX: FOUR CORNERS");
demo_label(16,"NO INTERIOR SCAN");
result[79]=0xA55A;__scroll_set(0,0);__ppu_mask_set(0x0A);while(1){}
}
