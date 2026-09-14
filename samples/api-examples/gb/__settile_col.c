// __settile_col
// Copy `len` successive tile numbers from `src` vertically, starting at `(x,y)` in the
// LCDC-selected BG map. The source advances one byte and the destination 32 bytes per
// tile. Waits for writable VRAM when necessary. The LCD-on path uses interrupt masking
// and can enable interrupts afterward; it is not a promise to preserve the caller's
// interrupt state or to finish within one VBlank.
// Expected: FAILED CHECKS 000, with the written tile data in the selected map.
#include "gb_tile_color_example.h"
const u8 example_tiles[] = {'A','B','C'};

void main() {
    u8 failures;
    failures = 0;
    tile_color_example_begin();
    __settile_col(2, 3, example_tiles, 3);
    if (tile_example_read(0x9C62, 0) != 'A') { failures++; }
    if (tile_example_read(0x9CA2, 0) != 'C') { failures++; }
    if (tile_example_read(0x9C63, 0) != 0) { failures++; }
    tile_example_finish(failures, 1);
}
