// __settilemap_rect
// Copy a tightly packed `w*h` array of tile numbers to a rectangle at `(x,y)` in the map
// selected by `base`. Source rows have `w` bytes; destination rows have a 32-byte
// stride. Waits for writable VRAM when necessary. The LCD-on path uses interrupt masking
// and can enable interrupts afterward; it is not a promise to preserve the caller's
// interrupt state or to finish within one VBlank.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_example.h"
const u8 example_tiles[] = {'A','B','C','D','E','F'};

void main() {
    u8 failures;
    failures = 0;
    tile_example_begin();
    __settilemap_rect(0x9C00, 2, 3, 3, 2, example_tiles);
    if (tile_example_read(0x9C62, 0) != 'A') { failures++; }
    if (tile_example_read(0x9C84, 0) != 'F') { failures++; }
    if (tile_example_read(0x9C65, 0) != 0) { failures++; }
    tile_example_finish(failures, 1);
}
