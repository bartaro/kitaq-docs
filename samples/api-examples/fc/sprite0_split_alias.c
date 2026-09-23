// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// nes_game.h exposes the same split operation as a convenience macro.
#include "fc_sprite0_scene.h"
#include "nes_game.h"
void main(void) {
    s0_prepare();
    while (1) {
        s0_frame();
        nes_split_scroll_sprite0(32,0);
        s0_completed++;
    }
}
