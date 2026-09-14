// __settileatcgb_unsafe
// Write a tile number and its CGB attribute. On DMG, only the tile-number write is
// performed. On CGB, enter with VRAM bank 0 selected; attributes use bank 1 and the call
// finishes with `VBK=0`. `base` explicitly selects the map (`0x9800` or `0x9C00`); the
// byte address is `base + 32*y + x`.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_example.h"

void main() {
    u8 failures;
    failures = 0;
    tile_example_begin();
    __settileatcgb_unsafe(0x9C00, 2, 3, 'A', KQ_CGB_ATTR(2, 0, 0, 0, 0));
    if (tile_example_read(0x9C62, 0) != 'A') { failures++; }
    if (tile_example_read(0x9862, 0) != 0) { failures++; }
    if (__cgb_is_cgb() && tile_example_read(0x9C62, 1) != 2) { failures++; }
    if (__cgb_is_cgb() && tile_example_read(0x9862, 1) != 0) { failures++; }
    tile_example_finish(failures, 1);
}
