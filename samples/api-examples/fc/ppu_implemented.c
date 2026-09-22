// Compare copied tile patterns, constant fills, zero-length seeks and safe wait calls.
#include "fc_common.h"
#include "ppu.c"
__prg_rom u8 stream_palette[32]={0x0F,0x30,0x10,0x30,0x0F,0x16,0x16,0x16,0x0F,0x12,0x12,0x12,0x0F,0x1A,0x1A,0x1A,0x0F,0x30,0x10,0x30,0x0F,0x16,0x16,0x16,0x0F,0x12,0x12,0x12,0x0F,0x1A,0x1A,0x1A};
__prg_rom u8 stream_attributes[64]={160,160,160,160,160,160,160,160,170,170,170,170,170,170,170,170,10,10,10,10,10,10,10,10,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,80,80,80,80,80,80,80,80,0,0,0,0,0,0,0,0};
__location(0x0500) u8 source_bytes[256];
__location(0x2007) u8 sample_ppudata;
u8 failures;u8 discarded_read;
// Text is copied and flushed with both NMI and rendering off.
void label(u8 x,u8 y,const u8* text) {
    m_text(x,y,text);__vramq_commit();__vramq_exec();__scroll_set(0,0);
}
void show(u8 row,const u8* text,u8 value) {
    m_text(1,row,text);m_put(24,row,(u8)('0'+value));
    __vramq_commit();__vramq_exec();__scroll_set(0,0);
}
void main() {
    u16 i;
    m_init();m_wait();__ppu_ctrl_set(0);__ppu_mask_set(0);
    __palette_bg_load(stream_palette);__vram_write(0x23C0,stream_attributes,64);
    failures=0;for(i=0;i<256;i++)source_bytes[i]=(u8)(i%3+1);
    // example:__ppu_ctrl_get:start
    __ppu_ctrl_set(4);
    if(__ppu_ctrl_get()!=4)failures=1; // Inspect the software shadow, not PPUSTATUS.
    __ppu_ctrl_set(0);
    // example:__ppu_ctrl_get:end
    // example:__ppu_mask_get:start
    __ppu_mask_set(0xE7);
    if(__ppu_mask_get()!=0xE7)failures=1;
    __ppu_mask_set(0);
    // example:__ppu_mask_get:end
    // example:nes_ppu_screen_off:start
    nes_ppu_screen_off();__ppu_ctrl_set(0); // Disable NMI during this bulk preparation.
    // example:nes_ppu_screen_off:end
    // example:nes_ppu_load_palette:start
    nes_ppu_load_palette(stream_palette); // Sixteen BG bytes followed by sixteen sprite bytes.
    // Palette reads are immediate; both halves use the same original sample palette.
    __ppu_addr(0x3F00);
    for(i=0;i<32;i++)if(sample_ppudata!=stream_palette[(u8)(i&15)])failures=1;
    // example:nes_ppu_load_palette:end
    // example:nes_ppu_clear_nt:start
    nes_ppu_clear_nt(0x2000,0,0); // All 960 tiles and 64 packed attribute bytes.
    // Nametable reads are buffered: discard one read, then inspect all 1024 bytes.
    __ppu_addr(0x2000);discarded_read=sample_ppudata;
    for(i=0;i<1024;i++)if(sample_ppudata!=0)failures=1;
    // example:nes_ppu_clear_nt:end
    // Install the original sample's attribute colors after the clear.
    __vram_write(0x23C0,stream_attributes,64);
    __vram_write(0x2040,source_bytes,255);
    __vram_fill(0x2180,1,255);
    __nametable_put(2,26,1);__nametable_put(28,26,2);__nametable_put(30,26,3);
    __ppu_ctrl_set(0);__ppu_mask_set(0);
    label(1,0,"PPU IMPLEMENTED CALLS");label(1,10,"BLUE COPY 255 BYTES");
    label(1,20,"GREEN FILL 255 BYTES");
    label(1,22,"FOUR LIBRARY CALLS");
    show(24,"FAILED CHECKS",failures);label(1,27,"SQUARE / BAR / TRIANGLE");
    // example:nes_ppu_screen_on:start
    nes_ppu_screen_on(0x80,0x0A);
    // NMI and background rendering are now enabled, with left-edge background visible.
    // example:nes_ppu_screen_on:end
    while(1)m_wait();
}
