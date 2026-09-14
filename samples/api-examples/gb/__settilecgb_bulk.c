// __settilecgb_bulk
// Copy `count` tile numbers from `tile_src`, then `count` attributes from `attr_src`, to
// the same map addresses starting at `dest`. These are separate byte arrays, not
// interleaved pairs. Waits for writable VRAM when necessary. The LCD-on path uses
// interrupt masking and can enable interrupts afterward; it is not a promise to preserve
// the caller's interrupt state or to finish within one VBlank.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_example.h"
const u8 example_tiles[] = {'A','B','C'};
const u8 example_attrs[] = {1,2,3};

void main() {
    u8 failures;
    failures = 0;
    tile_example_begin();
    __settilecgb_bulk(0x9862, example_tiles, example_attrs, 3);
    if (tile_example_read(0x9862, 0) != 'A') { failures++; }
    if (tile_example_read(0x9863, 0) != 'B') { failures++; }
    if (tile_example_read(0x9864, 0) != 'C') { failures++; }
    if (tile_example_read(0x9865, 0) != 0) { failures++; }
    if (__cgb_is_cgb() && tile_example_read(0x9862, 1) != 1) { failures++; }
    if (__cgb_is_cgb() && tile_example_read(0x9864, 1) != 3) { failures++; }
    tile_example_finish(failures, 0);
}
