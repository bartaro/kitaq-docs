// Learn the copied-payload C queue, seven-bit lengths and automatic NMI flushing.
#define MANUAL_FC_RUNTIME
#include "fc_common.h"
#include "runtime.c"
__prg_rom u8 runtime_palette[16]={0x0F,0x30,0x10,0x30,0x0F,0x16,0x16,0x16,0x0F,0x12,0x12,0x12,0x0F,0x1A,0x1A,0x1A};
// Each attribute quadrant covers a 2x2 tile area. Copy is blue, fill is green,
// and the three sentinel positions share red; the text rows use white.
__prg_rom u8 runtime_attributes[64]={160,160,160,160,160,160,160,160,10,10,10,10,10,10,10,10,255,255,255,255,255,255,255,255,80,80,80,80,80,80,80,80,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
u8 source_bytes[127];u8 failures;u8 peak;u8 encoded;u8 after_flush;
u8 rejected;u8 overflow_seen;u8 fill_value;u8 marker;
// Static text uses bounded batches with both rendering and NMI disabled.
void label(u8 x,u8 y,const u8* text) {
    m_text(x,y,text);nes_vram_queue_nmi_flush();__scroll_set(0,0);
}
void show(u8 row,const u8* label,u8 value) {
    m_text(1,row,label);
    m_put(20,row,(u8)('0'+value/100));
    m_put(21,row,(u8)('0'+(value/10)%10));
    m_put(22,row,(u8)('0'+value%10));nes_vram_queue_nmi_flush();__scroll_set(0,0);
}
void main() {
    u8 i;
    m_init();m_wait();__ppu_ctrl_set(0);__ppu_mask_set(0);
    __palette_bg_load(runtime_palette);__vram_write(0x23C0,runtime_attributes,64);
    failures=0;for(i=0;i<127;i++)source_bytes[i]=(u8)(i%3+1);
    nes_vram_queue_clear();
    if(nes_vram_queue_try_write(0x2040,source_bytes,127)!=1)failures++;
    if(nes_vram_queue_try_write(0x2100,source_bytes,59)!=1)failures++;
    peak=nes_vram_queue_used;
    if(peak!=192)failures++;
    if(nes_vram_queue_try_write(0x21DF,source_bytes,0)!=0)failures++;
    overflow_seen=nes_vram_queue_overflow;
    if(overflow_seen!=1 || nes_vram_queue_used!=192)failures++;
    // example:nes_vram_queue_clear:start
    nes_vram_queue_clear(); // Discard all records AND clear the overflow latch.
    if(nes_vram_queue_used!=0 || nes_vram_queue_overflow!=0)failures++;
    // example:nes_vram_queue_clear:end
    rejected=(u8)(1-nes_vram_queue_try_write(0x2040,source_bytes,128));
    if(rejected!=1 || nes_vram_queue_used!=0 || nes_vram_queue_overflow!=1)failures++;
    nes_vram_queue_clear();
    // Queue and cancel a red tile at the right edge; this cell must stay black.
    if(nes_vram_queue_try_fill(0x21DF,1,1)!=1)failures++;
    nes_vram_queue_clear();
    marker=1;
    if(nes_vram_queue_try_write(0x21C2,&marker,1)!=1)failures++;
    if(nes_vram_queue_try_write(0x21C2,source_bytes,0)!=1)failures++;
    if(nes_vram_queue_try_fill(0x21C2,0,0)!=1)failures++;
    // example:nes_vram_queue_try_write:start
    if(nes_vram_queue_try_write(0x2040,source_bytes,127)!=1)failures++;
    source_bytes[0]=3; // The queued first tile stays 1: payload was copied immediately.
    // example:nes_vram_queue_try_write:end
    fill_value=1;
    // example:nes_vram_queue_try_fill:start
    if(nes_vram_queue_try_fill(0x2100,fill_value,127)!=1)failures++;
    fill_value=3; // The queued fill remains the solid tile 1.
    // example:nes_vram_queue_try_fill:end
    encoded=nes_vram_queue_used;
    if(encoded!=145)failures++;
    // example:nes_vram_queue_nmi_flush:start
    // Rendering and NMI are disabled; PPUCTRL selects increment 1.
    nes_vram_queue_nmi_flush(); // No commit flag: consume all queued records now.
    after_flush=nes_vram_queue_used;
    if(after_flush!=0)failures++;
    // example:nes_vram_queue_nmi_flush:end
    // A small pending record is consumed automatically by runtime.c's __nes_nmi.
    marker=2;
    if(nes_vram_queue_try_write(0x21DC,&marker,1)!=1)failures++;
    __scroll_set(0,0);__ppu_ctrl_set(0x80);__ppu_mask_set(0x0A);
    nes_wait_nmi();__scroll_set(0,0);
    if(nes_vram_queue_used!=0)failures++;
    // Stop NMI while producing each static text batch, and stop rendering because
    // many small C records exceed VBlank. Explicit flushes cannot race a producer.
    __ppu_ctrl_set(0);__ppu_mask_set(0);
    label(1,0,"RUNTIME VRAM QUEUE");
    label(1,6,"BLUE COPIED PAYLOAD");label(1,12,"GREEN FILL");
    label(1,13,"ZERO / NMI / CANCEL");
    show(16,"CAPACITY",peak);show(17,"ENCODED BYTES",encoded);
    show(18,"AFTER FLUSH",after_flush);show(19,"REJECTED LENGTH",rejected);
    show(20,"OVERFLOW SEEN",overflow_seen);show(21,"FAILED CHECKS",failures);
    __scroll_set(0,0);__ppu_ctrl_set(0x80);__ppu_mask_set(0x0A);
    while(1)m_wait();
}
