// danmaku: Exercise the APIs and compare the documented results.
__location(0xC000) u16 result[80];
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "danmaku.c"
#pragma bank 0
// Print one unsigned result in decimal; negative results are shown as 16-bit bit patterns.
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
__prg_rom u8 bullet_art[256]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,112,112,112,112,112,112,0,0,0,0,0,0,0,0,0,0,7,7,7,7,7,7,0,0,0,0,0,0,0,0,0,0,119,119,119,119,119,119,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,112,112,112,112,112,112,0,0,112,112,112,112,112,112,0,0,112,112,112,112,112,112,0,0,7,7,7,7,7,7,0,0,112,112,112,112,112,112,0,0,119,119,119,119,119,119,0,0,112,112,112,112,112,112,0,0,0,0,0,0,0,0,0,0,7,7,7,7,7,7,0,0,112,112,112,112,112,112,0,0,7,7,7,7,7,7,0,0,7,7,7,7,7,7,0,0,7,7,7,7,7,7,0,0,119,119,119,119,119,119,0,0,7,7,7,7,7,7,0,0,0,0,0,0,0,0,0,0,119,119,119,119,119,119,0,0,112,112,112,112,112,112,0,0,119,119,119,119,119,119,0,0,7,7,7,7,7,7,0,0,119,119,119,119,119,119,0,0,119,119,119,119,119,119,0,0,119,119,119,119,119,119};
void main(){u8 i;u8 x;u8 y;tile_example_begin();M_LCDC=0;for(i=0;i<80;i++)result[i]=0;

// example:danmaku_reset:start
danmaku_reset();result[0]=dm_count;result[1]=dm_peak;
// example:danmaku_reset:end

// example:danmaku_spawn:start
result[2]=danmaku_spawn(40,40,16,0);result[3]=danmaku_spawn(160,40,0,0);result[4]=dm_count;result[5]=dm_rejected;
// example:danmaku_spawn:end

// example:danmaku_clear:start
danmaku_clear();result[6]=dm_count;result[7]=dm_spawned;result[8]=dm_peak;
// example:danmaku_clear:end

// example:danmaku_fan:start
danmaku_fan(80,64,0,4,8,64);result[9]=dm_count;result[10]=dm_spawned;
// example:danmaku_fan:end

// example:danmaku_clear_map:start
danmaku_clear_map();result[11]=dm_map[0];
// example:danmaku_clear_map:end

// example:danmaku_step:start
dm_player_x=0;dm_player_y=0;dm_invulnerable=0;for(i=0;i<8;i++){danmaku_clear_map();danmaku_step();}result[12]=dm_count;result[13]=dm_hit;result[14]=dm_graze;
// example:danmaku_step:end
__vram_copy(0x8000,bullet_art,256);vram_example_color(0,0,20,16,1);
// example:danmaku_present_now:start
// CGB general DMA; the LCD is stopped for this complete-map upload.
danmaku_present_now();
// example:danmaku_present_now:end

result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
