// menu_state demonstrates a complete, reproducible library workflow.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "text.c"
#include "menu.c"
__location(0xC600) u16 result[80];
void demo_label(u8 y,const u8* label){m_text(1,y,label);}
void demo_word(u8 y,u16 value){u8 x;u16 place;place=10000;for(x=0;x<5;x++){m_put(13+x,y,(u8)(48+value/place));value=value%place;place=place/10;}}
const u8 dialogue_tiles[128] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F, 0x1F, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0xF0, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10,
    0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F, 0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0xF0, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10 ,
0, 0, 16, 16, 24, 24, 28, 28, 24, 24, 16, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 254, 254, 124, 124, 56, 56, 16, 16
};
const u8 * const choices[]={"SWORD","SHIELD","POTION"};menu_state_t menu_state;menu_t menu;item_t items[3];
void main(){u8 i;tile_example_begin();M_LCDC=0;vram_example_color(1,2,18,14,2);for(i=0;i<80;i++)result[i]=0;__vram_copy(0x8010,dialogue_tiles,128);vram_example_color(1,1,18,15,3);M_LCDC=0x91;
// example:menu_init_state:start
menu_init_state(&menu_state,1,2,18,5,choices,3);result[2]=menu_state.selected;
// example:menu_init_state:end
// example:menu_draw:start
menu_draw(&menu_state);
// example:menu_draw:end
while(menu_state.selected==255 && menu_state.cancelled==0){__wait_vblank();
// example:menu_update:start
menu_update(&menu_state);menu_draw(&menu_state);
// example:menu_update:end
}
// example:menu_get_selected:start
result[0]=menu_get_selected(&menu_state);
// example:menu_get_selected:end
// example:menu_was_cancelled:start
result[1]=menu_was_cancelled(&menu_state);
// example:menu_was_cancelled:end
result[3]=menu_get_selected(0);result[4]=menu_was_cancelled(0);

demo_label(0,"NONBLOCKING MENU");
demo_label(8,"SELECTED");demo_word(8,result[0]);
demo_label(10,"CANCELLED");demo_word(10,result[1]);
demo_label(16,"A: OK  B: CANCEL");
result[79]=0xA55A;M_LCDC=0x91;while(1){}
}
