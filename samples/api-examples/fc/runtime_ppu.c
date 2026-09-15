// Compare copied tile patterns, constant fills, zero-length seeks and safe wait calls.
#define MANUAL_FC_RUNTIME
#include "fc_common.h"
#include "runtime.c"
__prg_rom u8 stream_palette[16]={0x0F,0x30,0x10,0x30,0x0F,0x16,0x16,0x16,0x0F,0x12,0x12,0x12,0x0F,0x1A,0x1A,0x1A};
__prg_rom u8 stream_attributes[64]={160,160,160,160,160,160,160,160,170,170,170,170,170,170,170,170,10,10,10,10,10,10,10,10,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,80,80,80,80,80,80,80,80,0,0,0,0,0,0,0,0};
__location(0x0500) u8 source_bytes[256];
u8 failures;u8 nmi_seen;u8 blank_seen;u8 start_counter;
// Text is copied and flushed with both NMI and rendering off.
void label(u8 x,u8 y,const u8* text) {
    m_text(x,y,text);nes_vram_queue_nmi_flush();__scroll_set(0,0);
}
void show(u8 row,const u8* text,u8 value) {
    m_text(1,row,text);m_put(24,row,(u8)('0'+value));
    nes_vram_queue_nmi_flush();__scroll_set(0,0);
}
void main() {
    u16 i;
    m_init();m_wait();__ppu_ctrl_set(0);__ppu_mask_set(0);
    __palette_bg_load(stream_palette);__vram_write(0x23C0,stream_attributes,64);
    failures=0;for(i=0;i<256;i++)source_bytes[i]=(u8)(i%3+1);
    // example:nes_ppu_stream_write:start
    // Rendering/NMI are off; PPUCTRL increment is 1. Transfer 256 bytes now.
    nes_ppu_stream_write(0x2040,source_bytes,256);
    source_bytes[0]=3; // VRAM already holds tile 1 at the first blue cell.
    // example:nes_ppu_stream_write:end
    // example:nes_ppu_stream_fill:start
    nes_ppu_stream_fill(0x2180,1,256); // Eight complete rows of solid green tiles.
    // example:nes_ppu_stream_fill:end
    // example:nes_ppu_seek:start
    PPUADDR=0x21; // Deliberately leave the shared address latch half-written.
    nes_ppu_seek(0x2342); // This runtime function resets the latch itself.
    PPUDATA=1; // Red 8x8 marker at pixel (16,208).
    // example:nes_ppu_seek:end
    nes_ppu_stream_write(0x235C,source_bytes,0);PPUDATA=2;
    nes_ppu_stream_fill(0x235E,3,0);PPUDATA=3;
    // example:nes_vblank_wait:start
    // With NMI disabled, poll a new PPU VBlank flag. No queued work is flushed.
    nes_vblank_wait();blank_seen=1;
    if((PPUSTATUS&0x80)!=0)failures++; // The wait's status read cleared the flag.
    // example:nes_vblank_wait:end
    // example:nes_wait_nmi:start
    __scroll_set(0,0);start_counter=nes_nmi_counter;
    __ppu_ctrl_set(0x80); // Enable runtime.c's NMI handler before waiting.
    nes_wait_nmi(); // Returns after the runtime completion counter changes.
    nmi_seen=(u8)(nes_nmi_counter!=start_counter);
    if(nmi_seen!=1)failures++;
    // example:nes_wait_nmi:end
    __ppu_ctrl_set(0);__ppu_mask_set(0);
    label(1,0,"RUNTIME PPU STREAM");label(1,10,"BLUE COPY 256 BYTES");
    label(1,20,"GREEN FILL 256 BYTES");
    show(22,"NMI OBSERVED",nmi_seen);show(23,"VBLANK OBSERVED",blank_seen);
    show(24,"FAILED CHECKS",failures);label(1,27,"SEEK / ZERO WRITE / FILL");
    __scroll_set(0,0);__ppu_ctrl_set(0x80);__ppu_mask_set(0x0A);
    while(1)m_wait();
}
