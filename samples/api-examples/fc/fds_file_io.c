// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// Read four asset bytes into a CPU buffer, update a save slot, then read it back.
// Build with fds_file_io_manifest.json; execute disk calls from common code.
#pragma fixed_bank 0
#include "fc_fds_scene.h"
void main(void) {
    u8 i;
    u8* data=(u8*)0x8500;
    u8* again=(u8*)0x8600;
    __irq_disable();__ppu_ctrl_set(0);__ppu_mask_set(0);
    // Keep rendering/NMI and non-disk IRQ sources disabled during disk I/O.
    *((u8*)0xFF)=0;*((u8*)0x4010)=0;*((u8*)0x4017)=0x40;*((u8*)0x4022)=0;
    fds_result[0]=__fds_load_file(73,data);
    fds_result[1]=data[0];fds_result[2]=data[3];
    for(i=0;i<4;i=i+1){data[i]=(i+1)*7;}
    fds_result[3]=__fds_save_file(73,data,4);
    fds_result[4]=__fds_load_file(73,again);
    fds_result[5]=again[0];fds_result[6]=again[3];
    // Check every returned byte, not only the displayed endpoints.
    for(i=0;i<4;i=i+1){if(again[i]!=(i+1)*7){fds_result[7]=1;}}
    fds_result[15]=165;
    m_init();m_text(2,2,"FDS LOAD / SAVE BUFFER");m_wait();
    m_text(2,5,"LOAD TO 8500 STATUS");fds_number(25,5,fds_result[0]);m_wait();
    m_text(2,7,"INITIAL FIRST/LAST");fds_number(21,7,fds_result[1]);fds_number(25,7,fds_result[2]);m_wait();
    m_text(2,9,"SAVE FILE 73 STATUS");fds_number(25,9,fds_result[3]);m_wait();
    m_text(2,11,"RELOAD TO 8600 STATUS");fds_number(25,11,fds_result[4]);m_wait();
    m_text(2,13,"SAVED FIRST / LAST");fds_number(21,13,fds_result[5]);fds_number(25,13,fds_result[6]);m_wait();
    m_text(2,15,"BYTE CHECK ERRORS");fds_number(25,15,fds_result[7]);m_wait();
    m_text(2,18,"STAGING 8000 / SIZE 4");m_wait();
    while(1){m_wait();}
}
