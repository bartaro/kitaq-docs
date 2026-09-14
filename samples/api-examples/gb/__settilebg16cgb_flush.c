// __settilebg16cgb_flush
// Transfer two adjacent tile rows from the RAM buffer to the LCDC-selected BG map. The
// source offset is `64*y + x`; `count` bytes are copied from that row and from the row
// 32 bytes below it. Write a tile number and its CGB attribute. On DMG, only the tile-
// number write is performed. On CGB, enter with VRAM bank 0 selected; attributes use
// bank 1 and the call finishes with `VBK=0`.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_example.h"
u8 example_tiles[1024];
u8 example_attrs[1024];
void __memset(void* dest, u8 value, u16 len);
void __settilebg16_buf(u8* buf, u8 x, u8 y, u8 tile);
void __settilebg16cgb_buf(u8* tilebuf, u8* attrbuf, u8 x, u8 y, u8 tile, u8 attr);
void __settilebg16_flush(const u8* buf, u8 y, u8 x, u8 count);
void __settilebg16cgb_flush(const u8* tilebuf, const u8* attrbuf, u8 y, u8 x, u8 count);

void main() {
    u8 failures;
    failures = 0;
    tile_example_begin();
    __memset(example_tiles, 0, 1024);
    __memset(example_attrs, 0, 1024);
    example_tiles[66]='A'; example_tiles[67]='B';
    example_tiles[98]='C'; example_tiles[99]='D';
    example_attrs[66]=2; example_attrs[67]=2;
    example_attrs[98]=2; example_attrs[99]=2;
    __settilebg16cgb_flush(example_tiles, example_attrs, 1, 2, 2);
    if (tile_example_read(0x9C42, 0) != 'A') { failures++; }
    if (tile_example_read(0x9C43, 0) != 'B') { failures++; }
    if (tile_example_read(0x9C62, 0) != 'C') { failures++; }
    if (tile_example_read(0x9C63, 0) != 'D') { failures++; }
    if (example_tiles[66] != 'A') { failures++; }
    if (example_tiles[99] != 'D') { failures++; }
    if (tile_example_read(0x9C44, 0) != 0) { failures++; }
    if (example_attrs[66] != 2) { failures++; }
    if (example_attrs[99] != 2) { failures++; }
    if (__cgb_is_cgb() && tile_example_read(0x9C42, 1) != 2) { failures++; }
    if (__cgb_is_cgb() && tile_example_read(0x9C63, 1) != 2) { failures++; }
    tile_example_finish(failures, 1);
}
