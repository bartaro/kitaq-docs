// __settilewin
// Write one tile-number byte to the tile map; this selects an existing tile image, not
// new pixel data. LCDC bit 6 selects the window map: zero uses `0x9800`, one uses
// `0x9C00`. These are map coordinates, not the window's screen position.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_example.h"

void main() {
    u8 failures;
    failures = 0;
    tile_example_begin();
    __settilewin(2, 3, 'A');
    if (tile_example_read(0x9C62, 0) != 'A') { failures++; }
    if (tile_example_read(0x9862, 0) != 0) { failures++; }
    tile_example_finish(failures, 1);
}
