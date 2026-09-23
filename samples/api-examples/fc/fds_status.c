// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// Show register status and complete the two presence waits on an inserted disk.
// This lesson does not read or write a disk file and does not call the BIOS.
#include "fc_common.h"
#include "fds.h"
__location(0x0600) u8 fds_result[16];
void main(void) {
    // These BIOS-free queries need NMI for display, but no maskable IRQ.
    __irq_disable();
    fds_result[0] = __fds_disk_ready();
    fds_result[1] = __fds_side();
    fds_result[2] = __fds_error();
    fds_result[3] = 0;
    // Never enter an unbounded wait without first checking disk presence.
    if (fds_result[0]) {
        __fds_wait_ready(); fds_result[3]++;
        __fds_wait_insert(); fds_result[3]++;
    }
    m_init();
    m_text(2,2,"FDS REGISTER STATUS"); m_wait();
    m_text(2,5,"PRESENT / PROTECT / STATUS"); m_wait();
    m_put(2,7,'0'+fds_result[0]);
    m_put(12,7,'0'+fds_result[1]);
    m_put(22,7,'0'+fds_result[2]); m_wait();
    m_text(2,10,"COMPLETED PRESENCE WAITS"); m_wait();
    m_put(2,12,'0'+fds_result[3]); m_wait();
    m_text(2,15,"NO FILE TRANSFER TESTED"); m_wait();
    while (1) { m_wait(); }
}
