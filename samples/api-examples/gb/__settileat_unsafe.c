// __settileat_unsafe
// Write one tile-number byte to the tile map; this selects an existing tile image, not
// new pixel data. `base` explicitly selects the map (`0x9800` or `0x9C00`); the byte
// address is `base + 32*y + x`.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_example.h"

void main() {
    u8 failures;
    failures = 0;
    tile_example_begin();
    __settileat_unsafe(0x9C00, 2, 3, 'A');
    if (tile_example_read(0x9C62, 0) != 'A') { failures++; }
    if (tile_example_read(0x9862, 0) != 0) { failures++; }
    tile_example_finish(failures, 1);
}
