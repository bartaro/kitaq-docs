// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// Inspect startup residency and the linker-generated overlay function table.
// Overlay functions are retained via a runtime branch, but never executed here.
#include "fc_common.h"
#include "fds_overlay.h"
__location(0x0600) u8 fds_result[16];
__location(0x060F) u8 request_overlay;
#pragma bank 2
u8 lesson_overlay_a(void) { return 21; }
u8 lesson_overlay_b(void) { return 34; }
#pragma bank 0
void main(void) {
    // These BIOS-free queries need NMI for display, but no maskable IRQ.
    __irq_disable();
    request_overlay=0;
    fds_result[0] = __fds_current_bank();
    fds_result[1] = __fds_is_bank_resident(1);
    fds_result[2] = __fds_is_bank_resident(2);
    fds_result[3] = __fds_overlay_function_count();
    if (request_overlay) {
        fds_result[4]=lesson_overlay_a(); fds_result[5]=lesson_overlay_b();
    }
    m_init();
    m_text(2,2,"FDS OVERLAY RECORDS"); m_wait();
    m_text(2,5,"CURRENT BANK"); m_put(25,5,'0'+fds_result[0]); m_wait();
    m_text(2,7,"BANK 1 RESIDENT"); m_put(25,7,'0'+fds_result[1]); m_wait();
    m_text(2,9,"BANK 2 RESIDENT"); m_put(25,9,'0'+fds_result[2]); m_wait();
    m_text(2,11,"OVERLAY FUNCTIONS"); m_put(25,11,'0'+fds_result[3]); m_wait();
    m_text(2,14,"NO OVERLAY LOAD TESTED"); m_wait();
    while (1) { m_wait(); }
}
