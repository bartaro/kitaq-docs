// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// A raw file-ID load invalidates the bank record; requiring bank 1 reloads it.
#pragma fixed_bank 0
#include "fc_fds_scene.h"
#pragma fixed_bank 2
__prg_rom u8 raw_payload[4]={11,22,33,44};
#pragma fixed_bank 0
void main(void) {
    __irq_disable();
    fds_result[0]=__fds_load_overlay(32);
    fds_result[1]=__fds_current_bank();
    fds_result[2]=__fds_is_bank_resident(1);
    fds_result[3]=raw_payload[0];fds_result[4]=raw_payload[3];
    fds_result[5]=__fds_require_bank(1);
    fds_result[6]=__fds_current_bank();
    fds_result[15]=165;
    m_init();m_text(2,2,"FDS RAW FILE-ID LOAD");m_wait();
    m_text(2,5,"FILE 32 LOAD STATUS");fds_number(25,5,fds_result[0]);m_wait();
    m_text(2,7,"FIRST / LAST BYTE");fds_number(21,7,fds_result[3]);fds_number(25,7,fds_result[4]);m_wait();
    m_text(2,9,"UNKNOWN BANK RECORD");fds_number(25,9,fds_result[1]);m_wait();
    m_text(2,11,"IS BANK 1 RESIDENT");fds_number(25,11,fds_result[2]);m_wait();
    m_text(2,13,"REQUIRE BANK 1");fds_number(25,13,fds_result[5]);m_wait();
    m_text(2,15,"RESIDENT AFTER RELOAD");fds_number(25,15,fds_result[6]);m_wait();
    while(1){m_wait();}
}
