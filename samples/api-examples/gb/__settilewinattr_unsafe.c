// __settilewinattr_unsafe
// Write only the CGB attribute byte; leave the tile number unchanged. Attribute bits
// select palette, tile-data bank, flips and priority. LCDC bit 6 selects the window map:
// zero uses `0x9800`, one uses `0x9C00`. These are map coordinates, not the window's
// screen position.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_example.h"

void main() {
    u8 failures;
    failures = 0;
    tile_example_begin();
    __settileat(0x9C00, 2, 3, 'A');
    __settilewinattr_unsafe(2, 3, KQ_CGB_ATTR(2, 0, 0, 0, 0));
    if (tile_example_read(0x9C62, 0) != 'A') { failures++; }
    if (tile_example_read(0x9862, 0) != 0) { failures++; }
    if (__cgb_is_cgb() && tile_example_read(0x9C62, 1) != 2) { failures++; }
    if (__cgb_is_cgb() && tile_example_read(0x9862, 1) != 0) { failures++; }
    tile_example_finish(failures, 1);
}
