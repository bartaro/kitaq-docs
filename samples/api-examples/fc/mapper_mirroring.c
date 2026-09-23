// SPDX-License-Identifier: MIT
// Copyright (c) 2026 DAISUKE OBA
// Read all four logical nametables after each board-specific mirroring setting.
// Compile for mmc1, mmc3, mmc5, axrom or fme7; NROM has fixed mirroring.
#include "fc_common.h"
__location(0x2007) u8 mirror_data;
__location(0x5101) u8 mmc5_chr_mode;
__location(0x5120) u8 mmc5_chr_banks[8];
__location(0x8000) u8 fme7_command;
__location(0xA000) u8 fme7_data;
__location(0x0600) u8 mirror_result[32];
u8 mirror_read(u16 address) {
    u8 ignored;
    __ppu_addr(address); ignored=mirror_data; return mirror_data;
}
void main(void) {
    u8 board; u8 i; u8 j; u8 k;
    __irq_disable(); __ppu_mask_set(0); __ppu_ctrl_set(0);
    board=__mapper_id(); mirror_result[0]=board;
    // These boards need eight explicit 1 KiB CHR selections for the font.
    // The three __chr_bank_set names support CNROM/MMC3, so use board registers.
    if (board==5) {
        mmc5_chr_mode=3;
        for (i=0;i<8;i++) { mmc5_chr_banks[i]=i; }
    }
    if (board==69) {
        for (i=0;i<8;i++) { fme7_command=i; fme7_data=i; }
    }
    // Seed two physical CIRAM pages through a mapping each board supports.
    if (board==4) {
        __mirroring_set(0); __ppu_addr(0x2000); mirror_data=17;
        __ppu_addr(0x2400); mirror_data=34;
    } else {
        if (board==5 || board==69) { __mirroring_set(2); }
        else { __mirroring_set(0); }
        __ppu_addr(0x2000); mirror_data=17;
        if (board==5 || board==69) { __mirroring_set(3); }
        else { __mirroring_set(1); }
        __ppu_addr(0x2000); mirror_data=34;
    }
    k=1;
    for (i=0;i<4;i++) {
        __mirroring_set(i);
        for (j=0;j<4;j++) { mirror_result[k]=mirror_read(0x2000+(u16)j*1024); k++; }
    }
    __mirroring_set(0); m_init();
    m_text(1,1,"NAMETABLE MAPPING"); m_wait();
    m_text(1,4,"A=LOW RAM / B=HIGH RAM"); m_wait();
    m_text(1,7,"PPU 2000 2400 2800 2C00"); m_wait();
    k=1;
    for (i=0;i<4;i++) {
        m_text(1,10+i*3,"MODE"); m_put(6,10+i*3,'0'+i);
        for (j=0;j<4;j++) {
            m_put(10+j*4,10+i*3,mirror_result[k]==17?'A':mirror_result[k]==34?'B':'?'); k++;
        }
        m_wait();
    }
    m_text(1,24,"SAME LETTER = SHARED RAM"); m_wait();
    mirror_result[31]=165;
    while (1) { m_wait(); }
}
