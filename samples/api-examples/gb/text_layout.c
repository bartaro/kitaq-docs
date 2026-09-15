#pragma bank 0
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "text.c"

// Six original frame tiles, each encoded as two identical bitplanes.
const u8 text_frame_tiles[96] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F, 0x1F, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0xF0, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10,
    0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F, 0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0xF0, 0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10
};

void main() {
    tile_example_begin();
    M_LCDC = 0;
    __vram_copy(0x8010, text_frame_tiles, 96);
    m_text(1,0,"TEXT PLACEMENT");
    // example:text_window:start
    text_window(1,2,18,5);
    // example:text_window:end
    // example:text_print_xy:start
    text_print_xy(2,3,"HELLO!");
    // example:text_print_xy:end
    m_text(2,5,"KEEP ERASE KEEP");
    // example:text_clear_rect:start
    text_clear_rect(7,5,5,1);
    // example:text_clear_rect:end
    m_text(1,8,"U8");
    // example:text_print_u8:start
    text_print_u8(11,8,255);
    // example:text_print_u8:end
    m_text(1,10,"U16");
    // example:text_print_u16:start
    text_print_u16(11,10,65535);
    // example:text_print_u16:end
    m_text(1,12,"S16");
    // example:text_print_s16:start
    text_print_s16(11,12,(s16)32768);
    // example:text_print_s16:end
    // A short write leaves the unused tail of a previously drawn value.
    m_text(1,14,"OVERWRITE");
    text_print_u16(11,14,12345);
    text_print_u8(11,14,7);
    // Reserve and erase the whole field before drawing a shorter value.
    m_text(1,16,"CLEAN");
    text_print_u16(11,16,12345);
    text_clear_rect(11,16,5,1);
    text_print_u8(11,16,7);
    vram_example_color(1,2,18,5,1);
    vram_example_color(11,8,5,3,2);
    vram_example_color(11,12,6,1,3);
    M_LCDC = 0x91;
    while (1) { m_wait(); }
}
