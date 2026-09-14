// Learn deferred VRAM writes, retained source pointers and queue capacity units.
#include "gb_tile_example.h"
const u8 shape_patterns[48]={255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,128,128,192,192,224,224,240,240,248,248,252,252,254,254,255,255};
#define MAP_BASE 0x9800
#define EXPECTED_CAPACITY 32
#define EXPECTED_USED 7
#define EXPECTED_LATCHED_RETURN 1
#define EXPECTED_SINGLE_SIZE 1

#include "vram.h"
u8 block[6];
u8 strip[3];
u8 failures;
u8 capacity;
u8 used;
u8 available;
u8 after_flush;
u8 check_result;
u8 i;
u8 overflow_seen;
void show(u8 row,const u8* label,u8 value) {
    m_text(1,row,label);
    m_put(16,row,(u8)('0'+value/100));
    m_put(17,row,(u8)('0'+(value/10)%10));
    m_put(18,row,(u8)('0'+value%10));
    m_wait();
}
void main() {
    tile_example_begin(); M_LCDC=0;
    __vram_copy(0x8010,shape_patterns,48);
    failures=0;
    block[0]=0; block[1]=2; block[2]=3;
    block[3]=3; block[4]=0; block[5]=2;
    strip[0]=1; strip[1]=2; strip[2]=3;
    // example:vram_init:start
    vram_init();
    if (vram_get_queue_used()!=0 || vram_get_overflowed()!=0) failures++;
    // example:vram_init:end
    // Fill the whole queue with writes of a blank tile, then reject one extra write.
    i=0;
    while (i<32) {
        check_result=vram_queue_tile(0,17,0);
        if (check_result!=1) failures++;
        i++;
    }
    check_result=vram_queue_tile(0,17,0);
    if (check_result!=0 || vram_get_queue_free()!=0) failures++;
    // example:vram_get_overflowed:start
    overflow_seen=vram_get_overflowed();
    if (overflow_seen!=1) failures++;
    // Reading the latch again does not clear it.
    if (vram_get_overflowed()!=1) failures++;
    // example:vram_get_overflowed:end

    vram_flush_now();
    if (vram_get_queue_used()!=0 || vram_get_overflowed()!=1) failures++;
    check_result=vram_queue_tile(0,17,0);
    // GB reports this append; FC reports whether the overflow latch is clear.
    if (check_result!=EXPECTED_LATCHED_RETURN) failures++;
    if (vram_get_queue_used()!=EXPECTED_SINGLE_SIZE) failures++;
    vram_clear_queue();
    // Discard a tile at (18,3); the verification image must leave that cell blank.
    check_result=vram_queue_bg_tile(18,3,1);
    // example:vram_clear_queue:start
    vram_clear_queue();
    if (vram_get_queue_used()!=0 || vram_get_overflowed()!=0) failures++;
    // example:vram_clear_queue:end
    // example:vram_queue_bg_tile:start
    check_result=vram_queue_bg_tile(2,2,1); // A solid 8x8 tile at pixel (16,16).
    if (check_result!=1) failures++;
    // example:vram_queue_bg_tile:end
    // example:vram_queue_tile:start
    check_result=vram_queue_tile(4,2,1); // The short alias draws at pixel (32,16).
    if (check_result!=1) failures++;
    // example:vram_queue_tile:end
    // example:vram_queue_bg_rect:start
    check_result=vram_queue_bg_rect(2,4,4,3,1); // A filled 32x24 rectangle at (16,32).
    if (check_result!=1) failures++;
    // example:vram_queue_bg_rect:end
    // example:vram_queue_bg_block:start
    check_result=vram_queue_bg_block(MAP_BASE,10,4,3,2,block);
    block[0]=1; // The queued pointer sees this change when the queue executes.
    if (check_result!=1) failures++;
    // example:vram_queue_bg_block:end
    // example:vram_queue_memcpy:start
    check_result=vram_queue_memcpy(MAP_BASE+8*32+2,strip,3);
    if (check_result!=1) failures++; // Copy three map bytes, not three tile patterns.
    // example:vram_queue_memcpy:end
    // example:vram_queue_tiles:start
    check_result=vram_queue_tiles(MAP_BASE+8*32+6,strip+1,2);
    if (check_result!=1) failures++; // This alias also measures length in bytes.
    // example:vram_queue_tiles:end
    // example:vram_queue_memset:start
    check_result=vram_queue_memset(MAP_BASE+8*32+10,1,5);
    if (check_result!=1) failures++; // Five solid tiles form a 40x8 horizontal bar.
    // example:vram_queue_memset:end
    // example:vram_get_queue_capacity:start
    capacity=vram_get_queue_capacity();
    // example:vram_get_queue_capacity:end
    // example:vram_get_queue_used:start
    used=vram_get_queue_used();
    // example:vram_get_queue_used:end
    // example:vram_get_queue_free:start
    available=vram_get_queue_free();
    if (used+available!=capacity) failures++;
    // example:vram_get_queue_free:end
    if (capacity!=EXPECTED_CAPACITY || used!=EXPECTED_USED) failures++;

    // example:vram_flush_now:start
    // Rendering is stopped here. On FC, commit readiness before direct execution.

    vram_flush_now();
    after_flush=vram_get_queue_used();
    if (after_flush!=0) failures++;
    // example:vram_flush_now:end
    M_LCDC=0x91;
    check_result=vram_queue_tile(18,10,1);
    // example:vram_flush:start
    vram_flush(); // One small write through the VBlank/NMI path.

    if (vram_get_queue_used()!=0) failures++;
    // example:vram_flush:end
    if (vram_get_overflowed()!=0) failures++;
    m_text(1,0,"VRAM QUEUE SHAPES"); m_wait();
    show(11,"CAPACITY",capacity); show(12,"USED",used); show(13,"FREE",available);
    show(14,"AFTER FLUSH",after_flush); show(16,"FAILED CHECKS",failures);
    show(15,"OVERFLOW SEEN",overflow_seen);
    while (1) m_wait();
}
