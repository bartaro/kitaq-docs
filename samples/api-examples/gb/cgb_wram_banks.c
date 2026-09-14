// Read/write the same CPU address in separate CGB WRAM banks, then restore bank 1.
// Build with --cgb=cgb_only --stack-bank=fixed. Keep live state outside WRAMX.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
u8 __svbk_get();
u8 __svbk_set(u8 bank);
void __cgb_safe_set_svbk(u8 value);
__location(0xFF70) u8 W_SELECTOR;
__location(0xC600) u8 failures;
__location(0xC601) u8 requested_bank;
__location(0xC602) u8 previous_bank;
__location(0xC603) u8 bank2_value;
__location(0xC604) u8 bank3_value;
const u8 square[16]={255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255};
const u8 outline[16]={255,255,129,129,129,129,129,129,129,129,129,129,129,129,255,255};

// Return a dynamic bank argument through a function, exercising argument lowering.
u8 next_bank() { return (u8)(requested_bank+1); }

void main() {
    tile_example_begin();
    // example:__cgb_safe_set_svbk:start
    __cgb_safe_set_svbk(0); // Raw selector 0 maps effective bank 1; this API returns void.
    if ((W_SELECTOR&7)!=0) failures++;
    // example:__cgb_safe_set_svbk:end
    // example:__svbk_get:start
    if (__svbk_get()!=1) failures++; // Normalize raw selector zero to effective bank 1.
    // example:__svbk_get:end
    requested_bank=2;
    // example:__svbk_set:start
    previous_bank=__svbk_set(requested_bank);
    if(previous_bank!=1 || __svbk_get()!=2) failures++;
    *((u8*)0xD100)=1; // This byte belongs to bank 2.
    previous_bank=__svbk_set(next_bank()); // Dynamic argument evaluates to 3.
    if(previous_bank!=2 || __svbk_get()!=3) failures++;
    *((u8*)0xD100)=2; // Same CPU address, different physical RAM.
    // example:__svbk_set:end
    previous_bank=__svbk_set(2);
    if(previous_bank!=3) failures++;
    bank2_value=*((u8*)0xD100);
    previous_bank=__svbk_set(requested_bank+1);
    if(previous_bank!=2) failures++;
    bank3_value=*((u8*)0xD100);
    if(bank2_value!=1 || bank3_value!=2) failures++;
    __cgb_safe_set_svbk(8); // Hardware uses bits 0..2: raw zero, effective bank 1.
    if(__svbk_get()!=1 || (W_SELECTOR&7)!=0) failures++;
    __svbk_set(1);
    __vram_copy(0x8010,square,16); __vram_copy(0x8020,outline,16);
    __settile_unsafe(2,3,bank2_value); __settile_unsafe(2,6,bank3_value);
    vram_example_color(2,3,1,1,1); // Bank-2 value selects a red filled square.
    vram_example_color(2,6,1,1,2); // Bank-3 value selects a blue outline.
    M_LCDC=0x91;
    m_text(1,0,"CGB WRAM BANKS");
    m_text(5,3,"BANK 2 = 1"); m_text(5,6,"BANK 3 = 2");
    m_text(1,10,"RESTORED BANK 1");
    m_text(1,15,"FAILED CHECKS");
    m_put(16,15,(u8)('0'+failures/100));
    m_put(17,15,(u8)('0'+(failures/10)%10));
    m_put(18,15,(u8)('0'+failures%10));
    while(1) { m_wait(); }
}
