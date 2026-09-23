// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// Demonstrate low-bit output selection and a single unframed RX sample.
#include "fc_ports_scene.h"
__prg_rom u8 tx_values[6]={0,1,2,3,254,255};
void main(void){
    u8 i;
    __irq_disable();__ppu_ctrl_set(0);port_phase=1;
    for(i=0;i<6;i++)__serial_tx_bit(tx_values[i]);
    __serial_tx_bit(1); // Leave OUT0 high; no byte framing or baud clock is added.
    port_result[0]=__serial_rx_bit();port_phase=2;port_result[31]=165;
    m_init();m_text(2,2,"SERIAL BIT PRIMITIVES");m_wait();
    m_text(2,5,"VALUE       EXPECTED OUT0");m_wait();
    for(i=0;i<6;i++){port_number(3,7+i*2,tx_values[i]);m_put(23,7+i*2,'0'+(tx_values[i]&1));m_wait();}
    m_text(2,20,"RX SAMPLE");port_number(23,20,port_result[0]);m_wait();
    m_text(2,23,"NO BYTE FRAMING OR CLOCK");m_wait();
    while(1){m_wait();}
}
