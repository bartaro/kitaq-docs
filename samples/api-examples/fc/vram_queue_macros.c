// Learn the nes_game.h queue macros, record costs, retained sources and commit timing.
#include "nes_game.h"
#include "fc_common.h"
__prg_rom u8 queue_palette[16]={0x0F,0x30,0x10,0x30,0x0F,0x16,0x16,0x16,0x0F,0x12,0x12,0x12,0x0F,0x1A,0x1A,0x1A};
__prg_rom u8 queue_attributes[64]={160,160,160,160,160,160,160,160,170,170,170,170,170,170,170,170,250,250,250,250,250,250,250,250,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,5,5,5,5,5,5,5,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
u8 source_bytes[255];
u8 i;
u8 failures;
u8 capacity;
u8 encoded;
u8 after_exec;
u8 overflow_seen;
u8 fill_value;
void show(u8 row,const u8* label,u8 value) {
    m_text(1,row,label);
    m_put(20,row,(u8)('0'+value/100));
    m_put(21,row,(u8)('0'+(value/10)%10));
    m_put(22,row,(u8)('0'+value%10));
    m_wait();
}
void main() {
    m_init(); m_wait();
    __ppu_ctrl_set(0); __ppu_mask_set(0);
    __palette_bg_load(queue_palette);
    __vram_write(0x23C0,queue_attributes,64);
    failures=0;
    nes_vram_clear_queue(); __vramq_clear_overflow();
    // example:__vramq_capacity:start
    capacity=__vramq_capacity();
    if (capacity!=128) failures++;
    // example:__vramq_capacity:end
    // Thirty-two four-byte put records exactly fill the buffer.
    i=0;
    while (i<32) { nes_vram_put(0x229F,0); i++; }
    if (__vramq_len()!=128 || __vramq_overflow()!=0) failures++;
    nes_vram_put(0x229F,1);
    if (__vramq_len()!=128) failures++;
    // example:__vramq_overflow:start
    overflow_seen=__vramq_overflow();
    if (overflow_seen!=1 || __vramq_overflow()!=1) failures++;
    // example:__vramq_overflow:end
    nes_vram_commit(); __vramq_exec();
    if (__vramq_len()!=0 || __vramq_overflow()!=1) failures++;
    nes_vram_put(0x229F,0);
    // example:nes_vram_clear_queue:start
    nes_vram_clear_queue();
    if (__vramq_len()!=0 || __vramq_overflow()!=1) failures++;
    // Clearing queued work deliberately leaves the overflow latch set.
    // example:nes_vram_clear_queue:end
    nes_vram_put(0x229F,0);
    // example:__vramq_clear_overflow:start
    __vramq_clear_overflow();
    if (__vramq_overflow()!=0 || __vramq_len()!=4) failures++;
    // Resetting the latch deliberately keeps this pending put record.
    // example:__vramq_clear_overflow:end
    // A queue clear also cancels readiness from an earlier commit.
    nes_vram_commit(); nes_vram_clear_queue();
    nes_vram_put(0x229F,1); __vramq_exec();
    if (__vramq_len()!=4) failures++;
    nes_vram_clear_queue();

    i=0;
    while (i<255) { source_bytes[i]=(u8)(i%3+1); i++; }
    // example:nes_vram_put:start
    nes_vram_put(0x2282,1); // Red 8x8 sentinel at pixel (16,160).
    // example:nes_vram_put:end
    // Zero-length records still consume 6 and 5 bytes, but preserve the sentinel.
    nes_vram_copy(0x2282,source_bytes,0);
    nes_vram_fill(0x2282,0,0);
    // example:nes_vram_copy:start
    nes_vram_copy(0x2040,source_bytes,255);
    source_bytes[0]=3; // The executor must see this change through its retained pointer.
    // example:nes_vram_copy:end
    fill_value=1;
    // example:nes_vram_fill:start
    nes_vram_fill(0x2160,fill_value,255); // Seven complete rows and 31 tiles in the eighth.
    fill_value=3; // The queued value stays 1, so the green block remains solid.
    // example:nes_vram_fill:end
    nes_vram_put(0x229E,1); // Red solid tile at pixel (240,160).
    // example:__vramq_len:start
    encoded=__vramq_len();
    if (encoded!=30 || capacity-encoded!=98) failures++;
    // 4+6+5+6+5+4 encoded bytes describe 512 actual byte writes.
    // example:__vramq_len:end
    __vramq_exec(); // Without a commit, the queue must remain untouched.
    if (__vramq_len()!=30) failures++;
    // example:nes_vram_commit:start
    nes_vram_commit(); // NMI is disabled here: this only marks the queue ready.
    if (__vramq_len()!=30) failures++;
    // example:nes_vram_commit:end
    // example:__vramq_exec:start
    // Rendering is stopped and the PPU increment is 1.
    __vramq_exec();
    after_exec=__vramq_len();
    if (after_exec!=0 || __vramq_overflow()!=0) failures++;
    // example:__vramq_exec:end

    // Prove automatic consumption by the default NMI handler with a small write.
    __scroll_set(0,0); __ppu_ctrl_set(0x80); __ppu_mask_set(0x0A);
    nes_vram_put(0x229C,2); // Red left-half tile at pixel (224,160).
    nes_vram_commit(); __nmi_wait(); __scroll_set(0,0);
    if (__vramq_len()!=0) failures++;
    m_text(1,0,"VRAM QUEUE MACROS"); m_wait();
    m_text(1,10,"BLUE COPY / GREEN FILL"); m_wait();
    m_text(1,19,"RED SENTINEL / NMI / PUT"); m_wait();
    show(21,"CAPACITY",capacity);
    show(22,"ENCODED BYTES",encoded);
    show(23,"AFTER EXEC",after_exec);
    show(24,"OVERFLOW SEEN",overflow_seen);
    show(25,"FAILED CHECKS",failures);
    while (1) m_wait();
}
