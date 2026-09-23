// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// Capture all raw matrix groups at startup; only interpret A after detection.
#include "fc_ports_scene.h"
void main(void){
    u8 row;
    __irq_disable();__ppu_ctrl_set(0);port_phase=1;
    port_result[0]=__fkb_detect();
    __fkb_scan(key_matrix);
    port_result[1]=__fkb_read_row_col(6,0);
    port_result[2]=0;
    if(port_result[0] && !(port_result[1]&16))port_result[2]=1;
    port_phase=2;port_result[31]=165;
    m_init();m_text(2,2,"KEYBOARD STARTUP SNAPSHOT");m_wait();
    m_text(2,4,"DEVICE DETECT");port_number(25,4,port_result[0]);m_wait();
    m_text(2,6,"ROW 6 COL 0");port_number(25,6,port_result[1]);m_wait();
    m_text(2,8,"A KEY - GUARDED");port_number(25,8,port_result[2]);m_wait();
    m_text(2,10,"ROW   COL0  COL1  (HEX)");m_wait();
    for(row=0;row<9;row++){
        m_put(3,12+row,'0'+row);port_hex(9,12+row,key_matrix[row*2]);port_hex(15,12+row,key_matrix[row*2+1]);m_wait();
    }
    m_text(2,23,"RAW MATRIX - NOT ASCII");m_wait();
    while(1){m_wait();}
}
