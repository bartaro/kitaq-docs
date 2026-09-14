#pragma once
// Color the tile-number examples without changing their map attributes.
#include "gb_tile_example.h"

void tile_color_example_begin() {
    tile_example_begin();
    if (__cgb_is_cgb()) {
        // Palette 0, color 3: blue (RGB555 0x7C00). The LCD is still off.
        // Map bytes and attribute bytes remain available for the API assertions.
        T_BGPI = 0x86;
        T_BGPD = 0;
        T_BGPD = 0x7C;
    }
}
