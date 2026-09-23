// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// MMC3: observe CHR selection, CIRAM aliases and one IRQ per explicit enable.
// Build with mapper_banks.chr; its 1 KiB banks contain distinct marker bytes.
#include "fc_common.h"
#include "nes_game.h"
__location(0x2007) u8 mapper_data;
__location(0x4017) u8 irq_frame_counter;
__location(0x0600) u8 mapper_result[32];
__location(0x0620) u8 irq_count;
__location(0x0621) u8 irq_phase;

// The compiler supplies RTI, but the handler must preserve what it changes.
// These byte operations and zero-argument intrinsics use no shared ABI scratch.
void __nes_irq(void) {
    __asm {
        PHA
        TXA
        PHA
        TYA
        PHA
    }
    irq_count++;
    if (irq_phase == 1) { nes_mapper_irq_ack(); }
    else { __mapper_irq_ack(); }
    __asm {
        PLA
        TAY
        PLA
        TAX
        PLA
    }
}

u8 mapper_read(u16 address) {
    u8 ignored;
    __ppu_addr(address); ignored = mapper_data; return mapper_data;
}
void mapper_write(u16 address, u8 value) {
    __ppu_addr(address); mapper_data = value;
}
void mapper_byte(u8 x, u8 y, u8 value) {
    m_put(x,y,(u8)('0'+value/10)); m_put(x+1,y,(u8)('0'+value%10));
}

void main(void) {
    u8 i;
    __irq_disable(); __ppu_mask_set(0); __ppu_ctrl_set(0); irq_frame_counter=0x40;
    mapper_result[0] = __mapper_id();
    // The two marker bytes are at the ends of adjacent 1 KiB banks.
    __chr_bank_set(2);
    mapper_result[1] = mapper_read(0x03FF);
    mapper_result[2] = mapper_read(0x07FF);
    __chr_bank_set0(4);
    mapper_result[3] = mapper_read(0x03FF);
    mapper_result[4] = mapper_read(0x07FF);
    __chr_bank_set1(6);
    mapper_result[5] = mapper_read(0x0BFF);
    mapper_result[6] = mapper_read(0x0FFF);
    // Restore the font's two 2 KiB windows before displaying the observations.
    __chr_bank_set0(0); __chr_bank_set1(2);
    __mirroring_set(0);
    mapper_write(0x2000,17); mapper_write(0x2400,34);
    for (i=0;i<4;i++) { mapper_result[7+i]=mapper_read(0x2000+(u16)i*1024); }
    __mirroring_set(1);
    for (i=0;i<4;i++) { mapper_result[11+i]=mapper_read(0x2000+(u16)i*1024); }
    __mirroring_set(0);
    m_init();
    // Opposite background/sprite pattern tables provide qualified MMC3 A12 edges.
    __ppu_ctrl_set(0x88); __ppu_mask_set(0x1E);
    __mapper_irq_disable(); irq_count=0; irq_phase=0;
    __mapper_irq_set(37); __mapper_irq_enable(); __irq_enable();
    for (i=0;i<6;i++) { m_wait(); }
    mapper_result[15]=irq_count;
    irq_phase=1;
    nes_mapper_irq_set(15); nes_mapper_irq_enable();
    for (i=0;i<6;i++) { m_wait(); }
    mapper_result[16]=irq_count;
    irq_phase=2;
    __irq_scanline_set(7); __mapper_irq_enable();
    for (i=0;i<6;i++) { m_wait(); }
    mapper_result[17]=irq_count;
    nes_mapper_irq_disable();
    for (i=0;i<6;i++) { m_wait(); }
    mapper_result[18]=irq_count;
    __irq_disable(); __mapper_irq_disable();
    m_text(1,1,"MMC3 / CHR AND IRQ"); m_wait();
    m_text(1,3,"MAPPER"); mapper_byte(24,3,mapper_result[0]); m_wait();
    m_text(1,5,"CHR SET 2"); mapper_byte(20,5,mapper_result[1]); mapper_byte(24,5,mapper_result[2]); m_wait();
    m_text(1,7,"CHR SET0 4"); mapper_byte(20,7,mapper_result[3]); mapper_byte(24,7,mapper_result[4]); m_wait();
    m_text(1,9,"CHR SET1 6"); mapper_byte(20,9,mapper_result[5]); mapper_byte(24,9,mapper_result[6]); m_wait();
    m_text(1,12,"CIRAM: A=17 / B=34"); m_wait();
    for (i=0;i<4;i++) {
        m_put(19+i*2,14,mapper_result[7+i]==17?'A':'B');
        m_put(19+i*2,16,mapper_result[11+i]==17?'A':'B');
    }
    m_text(1,14,"VERTICAL"); m_wait(); m_text(1,16,"HORIZONTAL"); m_wait();
    m_text(1,19,"IRQ COUNTS");
    for (i=0;i<4;i++) { mapper_byte(16+i*3,19,mapper_result[15+i]); }
    m_wait(); m_text(1,22,"ONE IRQ PER ENABLE"); m_wait();
    m_text(1,24,"ACK LEAVES IRQ DISABLED"); m_wait();
    mapper_result[31]=165;
    while (1) { m_wait(); }
}
