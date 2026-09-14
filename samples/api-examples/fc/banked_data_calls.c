// Read bank-qualified data and call named, no-argument functions, restoring bank 2.
#pragma fixed_bank 0
#define MANUAL_BANK_FC
#include "fc_common.h"
#include "bank.c"
__prg_rom u8 bank_palette[16]={0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22};
u8 callback_count;
u8 callback_byte;
#pragma fixed_bank 1
__prg_rom u8 home1[1]={0xA1};
#pragma fixed_bank 2
__prg_rom u8 home2[1]={0xB2};
#pragma fixed_bank 3
__prg_rom u8 payload[4]={0xD3,0x7A,0x5C,0x96};
void callback() { callback_count++;callback_byte=payload[0]; }
#pragma fixed_bank 0
#include "bank_example_checks.h"
void main() {
    m_init();m_wait();__ppu_off();__palette_bg_load(bank_palette);
    bank_checks();
    __ppu_ctrl_set(0x80);__ppu_mask_set(0x0A);bank_show();
    while(1) { m_wait(); }
}
