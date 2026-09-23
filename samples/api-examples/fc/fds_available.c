// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// Build for FDS and NROM to compare the compile-time mapper selection.
#include "fc_common.h"
#include "fds.h"
__location(0x0600) u8 fds_result[16];
void main(void) {
    // These BIOS-free queries need NMI for display, but no maskable IRQ.
    __irq_disable();
    fds_result[0] = __fds_available();
    m_init();
    m_text(2,2,"FDS BUILD SELECTION"); m_wait();
    m_text(2,5,"FDS=1 / CARTRIDGE=0"); m_wait();
    m_number(fds_result[0]); m_wait();
    while (1) { m_wait(); }
}
