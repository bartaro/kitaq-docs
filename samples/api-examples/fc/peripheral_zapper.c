// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// Compare raw and normalized port inputs; this is not an optical hit test.
#include "fc_ports_scene.h"
void main(void){
    __irq_disable();__ppu_ctrl_set(0);port_phase=1;
    port_result[0]=__zapper_raw1();port_result[1]=__zapper_trigger1();port_result[2]=__zapper_light1();
    port_result[3]=__zapper_raw2();port_result[4]=__zapper_trigger2();port_result[5]=__zapper_light2();
    port_result[6]=__zapper_trigger();port_result[7]=__zapper_light();
    port_phase=2;port_result[31]=165;
    m_init();m_text(2,2,"LIGHT-GUN INPUT SNAPSHOT");m_wait();
    m_text(2,5,"PORT   RAW  TRIGGER  LIGHT");m_wait();
    m_put(3,8,'1');port_hex(9,8,port_result[0]);port_number(15,8,port_result[1]);port_number(24,8,port_result[2]);m_wait();
    m_put(3,10,'2');port_hex(9,10,port_result[3]);port_number(15,10,port_result[4]);port_number(24,10,port_result[5]);m_wait();
    m_text(2,13,"DEFAULT = PORT 2");m_wait();
    m_text(2,15,"TRIGGER");port_number(15,15,port_result[6]);m_wait();
    m_text(2,17,"LIGHT");port_number(15,17,port_result[7]);m_wait();
    m_text(2,21,"LIGHT 1 IS NOT A HIT TEST");m_wait();
    while(1){m_wait();}
}
