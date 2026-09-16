// map_path: Exercise the APIs and compare the documented results.
__location(0xC000) u16 result[80];
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "map.c"
#include "slg_path.c"
#include "slg_unit.c"
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
__prg_rom u8 tiles[30]={0,0,0,0,0,0,0,0,126,0,0,0,0,0,126,0,0,0,0,0,126,0,0,0,0,0,0,0,0,0};
__prg_rom u8 blocks[4]={0,65,16,0};
__prg_rom u8 events[30]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9};
__prg_rom map_t maps[1]={{6,5,0,tiles,blocks,events}};
u8 costs[30];u8 mask[30];u8 route[30];unit_t hero;
void main(){u8 i;u8 x;u8 y;tile_example_begin();M_LCDC=0;for(i=0;i<80;i++)result[i]=0;
__vram_fill(0x87E0,255,16);
// example:map_current_width:start
result[0]=map_current_width();
// example:map_current_width:end

// example:map_current_height:start
result[1]=map_current_height();
// example:map_current_height:end

// example:map_load:start
map_load(0,maps);result[2]=map_current_width();result[3]=map_current_height();
// example:map_load:end

// example:map_is_blocked:start
result[4]=map_is_blocked(2,2);result[5]=map_is_blocked(6,2);result[6]=map_is_blocked(1,2);
// example:map_is_blocked:end

// example:map_trigger_at:start
result[7]=map_trigger_at(5,4);result[8]=map_trigger_at(6,4);
// example:map_trigger_at:end

// example:camera_center:start
camera_center(5,4);result[9]=*((u8*)0xFF43);result[10]=*((u8*)0xFF42);
// example:camera_center:end
hero.x=0;hero.y=2;hero.hp=5;hero.move=3;hero.atk_min=1;hero.atk_max=2;hero.acted=0;
// example:unit_can_act:start
result[11]=unit_can_act(&hero);hero.acted=1;result[12]=unit_can_act(&hero);hero.acted=0;
// example:unit_can_act:end

// example:range_fill_move:start
range_fill_move(0,2,3,costs);for(i=0;i<30;i++)result[13+i]=costs[i];
// example:range_fill_move:end

// example:unit_move_range:start
result[43]=unit_move_range(&hero,mask);result[44]=mask[12];result[45]=mask[14];
// example:unit_move_range:end

// example:unit_attack_range:start
result[46]=unit_attack_range(&hero,mask);result[47]=mask[12];result[48]=mask[14];
// example:unit_attack_range:end

// example:path_find_bfs:start
result[49]=path_find_bfs(0,2,5,2,route,30);x=0;y=2;for(i=0;i<result[49];i++){if(route[i]==0)y--;if(route[i]==1)x++;if(route[i]==2)y++;if(route[i]==3)x--;}result[50]=x;result[51]=y;result[52]=path_find_bfs(0,2,5,2,route,2);result[53]=path_find_bfs(0,2,2,2,route,30);
// example:path_find_bfs:end
// Draw two enlarged grids: movement costs on the left; a shortest route on the right.
__vram_fill(0x9800,0,1024);for(y=0;y<5;y++)for(x=0;x<6;x++){if(map_is_blocked(x,y)){__settile_xy(1+x,3+y,126);__settile_xy(11+x,3+y,126);vram_example_color(1+x,3+y,1,1,1);vram_example_color(11+x,3+y,1,1,1);}else if(costs[y*6+x]!=255){m_put(1+x,3+y,48+costs[y*6+x]);vram_example_color(1+x,3+y,1,1,2);}}path_find_bfs(0,2,5,2,route,30);x=0;y=2;m_put(11+x,3+y,83);for(i=0;i<result[49];i++){if(route[i]==0)y--;if(route[i]==1)x++;if(route[i]==2)y++;if(route[i]==3)x--;m_put(11+x,3+y,42);vram_example_color(11+x,3+y,1,1,3);}m_put(16,5,71);
m_text(1,0,"MOVE COST / PATH");
m_text(1,10,"WALL = SOLID");
m_text(1,12,"S START / G GOAL");
m_text(1,14,"PATH LENGTH");demo_word(14,result[49]);
m_text(1,16,"TOO SHORT");demo_word(16,result[52]);
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
