// __settile
// Write one tile-number byte to the tile map; this selects an existing tile image, not
// new pixel data. The destination is always `0x9800 + 32*y + x`, regardless of which
// maps LCDC selects for the background and window.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_color_example.h"

void main() {
    u8 failures;
    failures = 0;
    tile_color_example_begin();
    __settile(2, 3, 'A');
    if (tile_example_read(0x9862, 0) != 'A') { failures++; }
    if (tile_example_read(0x9C62, 0) != 0) { failures++; }
    tile_example_finish(failures, 0);
}
