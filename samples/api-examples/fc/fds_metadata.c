// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// Use fds_metadata.json: distinguish a present empty record from a missing ID.
#include "fc_common.h"
#include "fds_file.h"
__location(0x0600) u8 fds_result[16];
__location(0x0610) u16 fds_sizes[3];
void main(void) {
    // These BIOS-free queries need NMI for display, but no maskable IRQ.
    __irq_disable();
    fds_result[0] = __fds_file_exists(16);
    fds_sizes[0] = __fds_file_size(16);
    fds_result[1] = __fds_file_exists(17);
    fds_sizes[1] = __fds_file_size(17);
    fds_result[2] = __fds_file_exists(18);
    fds_sizes[2] = __fds_file_size(18);
    m_init();
    m_text(2,2,"FDS COMPILED FILE TABLE"); m_wait();
    m_text(2,5,"ID    EXISTS    BYTES"); m_wait();
    m_text(2,7,"16      1        513"); m_wait();
    m_text(2,9,"17      1          0"); m_wait();
    m_text(2,11,"18      0          0"); m_wait();
    if (fds_result[0]==1 && fds_sizes[0]==513 &&
        fds_result[1]==1 && fds_sizes[1]==0 &&
        fds_result[2]==0 && fds_sizes[2]==0) { m_text(2,14,"TABLE VALUES MATCH: PASS"); }
    else { m_text(2,14,"TABLE VALUES MATCH: FAIL"); }
    m_wait();
    m_text(2,17,"NO DISK DIRECTORY SCAN"); m_wait();
    while (1) { m_wait(); }
}
