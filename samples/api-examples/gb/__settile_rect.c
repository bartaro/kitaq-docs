// __settile_rect
// Fill a `w` by `h` rectangle in the LCDC-selected BG map with one tile number. Rows are
// 32 bytes apart; this repeats a tile, rather than copying an image array. Waits for
// writable VRAM when necessary. The LCD-on path uses interrupt masking and can enable
// interrupts afterward; it is not a promise to preserve the caller's interrupt state or
// to finish within one VBlank.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_color_example.h"

void main() {
    u8 failures;
    failures = 0;
    tile_color_example_begin();
    __settile_rect(2, 3, 3, 2, 'A');
    if (tile_example_read(0x9C62, 0) != 'A') { failures++; }
    if (tile_example_read(0x9C84, 0) != 'A') { failures++; }
    if (tile_example_read(0x9C65, 0) != 0) { failures++; }
    tile_example_finish(failures, 1);
}
