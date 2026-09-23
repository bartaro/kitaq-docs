// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// CNROM maps one complete 8 KiB CHR bank for all three CHR-selection names.
#include "fc_common.h"
__location(0x2007) u8 chr_data;
__location(0x0600) u8 chr_result[16];
u8 chr_marker(void) {
    u8 ignored;
    __ppu_addr(0x03FF); ignored=chr_data; return chr_data;
}
void chr_number(u8 y,u8 value) {
    m_put(24,y,'0'+value/10); m_put(25,y,'0'+value%10);
}
void main(void) {
    __irq_disable(); __ppu_mask_set(0); __ppu_ctrl_set(0);
    __chr_bank_set(2); chr_result[0]=chr_marker();
    __chr_bank_set0(1); chr_result[1]=chr_marker();
    __chr_bank_set1(3); chr_result[2]=chr_marker();
    __chr_bank_set(0); m_init();
    m_text(1,1,"CNROM / 8 KIB CHR BANKS"); m_wait();
    m_text(1,5,"SET 2 / MARKER"); chr_number(5,chr_result[0]); m_wait();
    m_text(1,8,"SET0 1 / MARKER"); chr_number(8,chr_result[1]); m_wait();
    m_text(1,11,"SET1 3 / MARKER"); chr_number(11,chr_result[2]); m_wait();
    m_text(1,16,"ALL THREE NAMES SELECT"); m_wait();
    m_text(1,18,"THE WHOLE PATTERN TABLE"); m_wait();
    chr_result[15]=165;
    while (1) { m_wait(); }
}
