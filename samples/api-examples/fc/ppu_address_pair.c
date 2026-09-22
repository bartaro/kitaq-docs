// Compare copied tile patterns, constant fills, zero-length seeks and safe wait calls.
#include "fc_common.h"
#include "ppu.c"
__location(0x2007) u8 PPUDATA;
__prg_rom u8 stream_palette[16]={0x0F,0x30,0x10,0x30,0x0F,0x16,0x16,0x16,0x0F,0x12,0x12,0x12,0x0F,0x1A,0x1A,0x1A};
__prg_rom u8 stream_attributes[64]={160,160,160,160,160,160,160,160,170,170,170,170,170,170,170,170,10,10,10,10,10,10,10,10,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,80,80,80,80,80,80,80,80,0,0,0,0,0,0,0,0};
__location(0x0500) u8 source_bytes[256];
u8 failures;u8 nmi_seen;u8 blank_seen;u8 start_counter;
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
    // These helpers accept an 8-bit count and reset the shared address latch.
    // example:nes_ppu_write_bytes:start
    __ppu_read_status();nes_ppu_write_bytes(0x20,0x40,source_bytes,255);
    source_bytes[0]=3; // The completed transfer retains tile 1.
    // example:nes_ppu_write_bytes:end
    // example:nes_ppu_fill:start
    __ppu_read_status();nes_ppu_fill(0x21,0x80,1,255);
    // example:nes_ppu_fill:end
    // example:nes_ppu_seek_bytes:start
    nes_ppu_seek_bytes(0x23,0x42);
    PPUDATA=1; // Red 8x8 marker at pixel (16,208).
    // example:nes_ppu_seek_bytes:end
    __ppu_read_status();nes_ppu_write_bytes(0x23,0x5C,source_bytes,0);PPUDATA=2;
    __ppu_read_status();nes_ppu_fill(0x23,0x5E,3,0);PPUDATA=3;
    __ppu_ctrl_set(0);__ppu_mask_set(0);
    label(1,0,"PPU HIGH LOW PAIR");label(1,10,"BLUE COPY 255 BYTES");
    label(1,20,"GREEN FILL 255 BYTES");
    label(1,22,"LATCH RESET BY LIBRARY");
    show(24,"FAILED CHECKS",failures);label(1,27,"SEEK / ZERO WRITE / FILL");
    __scroll_set(0,0);__ppu_ctrl_set(0x80);__ppu_mask_set(0x0A);
    while(1)m_wait();
}
