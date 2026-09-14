// __settile_bulk_fast
// Copy `count` consecutive tile-number bytes from `src` to the VRAM byte address `dest`.
// The count is in bytes, not tile-image units; no row-stride adjustment is made. Does
// not wait for VRAM access. Call only while the LCD is off or within a caller-managed
// writable interval with enough time for the whole transfer.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_color_example.h"
const u8 example_tiles[] = {'A','B','C'};
const u8 example_attrs[] = {1,2,3};

void main() {
    u8 failures;
    failures = 0;
    tile_color_example_begin();
    __settile_bulk_fast(0x9862, example_tiles, 3);
    if (tile_example_read(0x9862, 0) != 'A') { failures++; }
    if (tile_example_read(0x9863, 0) != 'B') { failures++; }
    if (tile_example_read(0x9864, 0) != 'C') { failures++; }
    if (tile_example_read(0x9865, 0) != 0) { failures++; }
    tile_example_finish(failures, 0);
}
