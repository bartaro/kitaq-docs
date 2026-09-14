// __settilebg16_buf
// Write a 16×16-pixel cell into a RAM tile-map buffer: the four 8×8 tile numbers are
// `tile,tile+1` on top and `tile+2,tile+3` below. Values wrap at 256. This does not
// transfer anything to VRAM.
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
    __settilebg16_buf(example_tiles, 1, 1, 'A');
    // The buffer operation must not write to VRAM yet.
    if (tile_example_read(0x9C42, 0) != 0) { failures++; }
    // Transfer the prepared cell so its four characters can be seen.
    __settilebg16_flush(example_tiles, 1, 2, 2);
    if (tile_example_read(0x9C42, 0) != 'A') { failures++; }
    if (tile_example_read(0x9C43, 0) != 'B') { failures++; }
    if (tile_example_read(0x9C62, 0) != 'C') { failures++; }
    if (tile_example_read(0x9C63, 0) != 'D') { failures++; }
    if (example_tiles[66] != 'A') { failures++; }
    if (example_tiles[99] != 'D') { failures++; }
    if (tile_example_read(0x9C44, 0) != 0) { failures++; }
    tile_example_finish(failures, 1);
}
