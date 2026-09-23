// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// Load a data window explicitly, reuse its residency, then restore boot bank 1.
#pragma fixed_bank 0
#include "fc_fds_scene.h"
#pragma fixed_bank 2
__prg_rom u8 bank_payload[4]={11,22,33,44};
#pragma fixed_bank 0
void main(void) {
    __irq_disable();
    fds_result[0]=__fds_load_bank(2);
    fds_result[1]=__fds_current_bank();
    fds_result[2]=__fds_require_bank(2);
    fds_result[3]=bank_payload[0];fds_result[4]=bank_payload[3];
    fds_result[5]=nes_fds_load_bank(1);
    fds_result[6]=__fds_current_bank();
    fds_result[7]=__fds_require_bank(1);
    fds_result[8]=__fds_load_bank(0);
    fds_result[9]=__fds_load_bank(255);
    fds_result[15]=165;
    m_init();m_text(2,2,"FDS DATA WINDOW");m_wait();
    m_text(2,5,"LOAD BANK 2 STATUS");fds_number(25,5,fds_result[0]);m_wait();
    m_text(2,7,"FIRST / LAST BYTE");fds_number(21,7,fds_result[3]);fds_number(25,7,fds_result[4]);m_wait();
    m_text(2,9,"REQUIRE SAME BANK");fds_number(25,9,fds_result[2]);m_wait();
    m_text(2,11,"RESTORE BANK 1");fds_number(25,11,fds_result[5]);m_wait();
    m_text(2,13,"RESIDENT BANK");fds_number(25,13,fds_result[6]);m_wait();
    m_text(2,16,"INVALID BANKS 0 / 255");m_wait();
    fds_number(2,18,fds_result[8]);fds_number(8,18,fds_result[9]);m_wait();
    while(1){m_wait();}
}
