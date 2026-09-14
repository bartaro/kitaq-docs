// __settileattr_bulk_fast
// Copy `count` consecutive CGB attribute bytes from `src` to `dest` in VRAM bank 1. Tile
// numbers are untouched; the destination is a byte address, not an `(x,y)` pair. Does
// not wait for VRAM access. Call only while the LCD is off or within a caller-managed
// writable interval with enough time for the whole transfer.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_example.h"
const u8 example_tiles[] = {'A','B','C'};
const u8 example_attrs[] = {1,2,3};

void main() {
    u8 failures;
    failures = 0;
    tile_example_begin();
    __settile_bulk(0x9862, example_tiles, 3);
    __settileattr_bulk_fast(0x9862, example_attrs, 3);
    if (tile_example_read(0x9862, 0) != 'A') { failures++; }
    if (tile_example_read(0x9863, 0) != 'B') { failures++; }
    if (tile_example_read(0x9864, 0) != 'C') { failures++; }
    if (tile_example_read(0x9865, 0) != 0) { failures++; }
    if (__cgb_is_cgb() && tile_example_read(0x9862, 1) != 1) { failures++; }
    if (__cgb_is_cgb() && tile_example_read(0x9864, 1) != 3) { failures++; }
    tile_example_finish(failures, 0);
}
