#pragma bank 0
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "text.c"

// Six original frame tiles plus cursor and page-wait indicators, each encoded as two identical bitplanes.
const u8 dialogue_tiles[128] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F, 0x1F, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0xF0, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10,
    0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F, 0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0xF0, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10 ,
0, 0, 16, 16, 24, 24, 28, 28, 24, 24, 16, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 254, 254, 124, 124, 56, 56, 16, 16
};

#pragma bank 1
const u8 dialogue_bank_marker=161;
#pragma bank 2
const u8 dialogue_far[]={TEXT_CTRL_NEWLINE,'B','A','N','K',' ','2',TEXT_CTRL_END};
#pragma bank 0
const u8 dialogue_near[]={'N','E','A','R',TEXT_CTRL_NEWLINE,'R','E','A','D','Y',TEXT_CTRL_WAIT,12,TEXT_CTRL_END};
void main(){
    tile_example_begin();M_LCDC=0;
    __vram_copy(0x8010,dialogue_tiles,128);
    m_text(1,0,"DIALOGUE FLOW");
    vram_example_color(1,2,18,5,2);
    M_LCDC=0x91;
    // example:text_open:start
    text_open(1,2,18,5);
    // example:text_open:end
    // example:text_set_speed:start
    text_set_speed(2);
    // example:text_set_speed:end
    // example:text_print:start
    text_print(dialogue_near);
    // example:text_print:end
    __bankswitch(1);
    // example:text_print_far:start
    text_print_far(2,dialogue_far);
    // example:text_print_far:end
    text_set_speed(0);
    m_text(1,8,"CLOSED AREA");
    text_open(1,9,18,3);
    text_print("ERASE ME");
    // example:text_close:start
    text_close();
    text_print("HIDDEN"); // With the area closed, ordinary characters are not drawn.
    // example:text_close:end
    m_text(1,14,"BANK RESTORED");
    text_print_u8(16,14,dialogue_bank_marker);
    m_text(1,16,"SPEED 2 / WAIT 12");
    while(1){m_wait();}
}
