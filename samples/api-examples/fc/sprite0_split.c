// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// Keep the top aligned and shift the lower bars left by 32 pixels after the hit.
#include "fc_sprite0_scene.h"
void main(void) {
    s0_prepare();
    while (1) {
        s0_frame();
        __split_scroll_sprite0(32,0);
        s0_completed++;
    }
}
