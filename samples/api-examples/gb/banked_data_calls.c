// Read bank-qualified data and invoke no-argument callbacks, restoring bank 2.
#pragma fixed_bank 0
#include "gb_tile_color_example.h"
#include "bank.c"
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
    tile_color_example_begin();
    bank_checks();
    M_LCDC=0x91;bank_show();
    while(1) { m_wait(); }
}
