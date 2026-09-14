// __settilebg_unsafe
// Write one tile-number byte to the tile map; this selects an existing tile image, not
// new pixel data. LCDC bit 3 selects the background map: zero uses `0x9800`, one uses
// `0x9C00`. The destination is that base plus `32*y + x`.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_color_example.h"

void main() {
    u8 failures;
    failures = 0;
    tile_color_example_begin();
    __settilebg_unsafe(2, 3, 'A');
    if (tile_example_read(0x9C62, 0) != 'A') { failures++; }
    if (tile_example_read(0x9862, 0) != 0) { failures++; }
    tile_example_finish(failures, 1);
}
