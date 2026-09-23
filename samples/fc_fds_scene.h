// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
#ifndef FC_FDS_SCENE_H
#define FC_FDS_SCENE_H
#include "fc_common.h"
#include "nes_game.h"
__location(0x0600) u8 fds_result[16];
// Reserve this area for the optional host-side calling-convention test fixture.
__location(0x0700) u8 fds_fixture_log[256];
void fds_number(u8 x,u8 y,u8 value) {
    m_put(x,y,'0'+value/100);m_put(x+1,y,'0'+(value/10)%10);m_put(x+2,y,'0'+value%10);
}
void fds_call_screen(void) {
    m_init();
    m_text(2,2,"FDS CALL AND RETURN");m_wait();
    m_text(2,5,"RETURN VALUE");fds_number(25,5,fds_result[0]);m_wait();
    m_text(2,7,"CALLBACK COUNT");fds_number(25,7,fds_result[1]);m_wait();
    m_text(2,9,"BANK EXPR COUNT");fds_number(25,9,fds_result[2]);m_wait();
    m_text(2,11,"BANK IN CALLBACK");fds_number(25,11,fds_result[3]);m_wait();
    m_text(2,13,"BANK AFTER RETURN");fds_number(25,13,fds_result[4]);m_wait();
    m_text(2,16,"CALL BANK 2 / RESTORE BANK 1");m_wait();
}
#endif
