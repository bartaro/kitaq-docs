// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// Call actual bank-2 code and observe restoration of the caller's bank window.
#pragma fixed_bank 0
#include "fc_fds_scene.h"
u8 choose_overlay(void){fds_result[2]++;return 2;}
#pragma fixed_bank 2
u8 overlay_answer(void){fds_result[1]++;fds_result[3]=__fds_current_bank();return 42;}
#pragma fixed_bank 0
void main(void) {
    __irq_disable();fds_result[1]=0;fds_result[2]=0;
    fds_result[0]=__fds_overlay_farcall(choose_overlay(),overlay_answer);
    fds_result[4]=__fds_current_bank();fds_result[15]=165;
    fds_call_screen();while(1){m_wait();}
}
