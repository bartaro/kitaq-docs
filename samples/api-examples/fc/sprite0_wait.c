// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// A fresh sprite-zero/background overlap must be observed on every frame.
#include "fc_sprite0_scene.h"
void main(void) {
    s0_prepare();
    while (1) {
        s0_frame();
        __sprite0_wait_hit();
        s0_completed++;
    }
}
