"""Create visible queue examples with identical geometry and explicit platform units."""
from pathlib import Path
SITE=Path(__file__).resolve().parents[2]
# Three original geometric tiles: solid, left half, and a stepped right triangle.
rows=[[255]*8,[240]*8,[128,192,224,240,248,252,254,255]]
gb_patterns=[value for tile in rows for value in tile for _ in range(2)]
fc_patterns=[value for tile in rows for plane in range(2) for value in tile]
font=bytearray((SITE/'samples/font.chr').read_bytes());font[16:64]=bytes(fc_patterns)
(SITE/'samples/api-examples/fc/vram_shapes.chr').write_bytes(font)
body=r'''
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
    DEMO_BEGIN
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
    FC_COMMIT
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
    FC_READY_TEST
    // example:vram_flush_now:start
    // Rendering is stopped here. On FC, commit readiness before direct execution.
    FC_COMMIT
    vram_flush_now();
    after_flush=vram_get_queue_used();
    if (after_flush!=0) failures++;
    // example:vram_flush_now:end
    DEMO_DISPLAY
    check_result=vram_queue_tile(18,10,1);
    // example:vram_flush:start
    vram_flush(); // One small write through the VBlank/NMI path.
    RESTORE_SCROLL
    if (vram_get_queue_used()!=0) failures++;
    // example:vram_flush:end
    if (vram_get_overflowed()!=0) failures++;
    m_text(1,0,"VRAM QUEUE SHAPES"); m_wait();
    show(11,"CAPACITY",capacity); show(12,"USED",used); show(13,"FREE",available);
    show(14,"AFTER FLUSH",after_flush); show(16,"FAILED CHECKS",failures);
    show(15,"OVERFLOW SEEN",overflow_seen);
    while (1) m_wait();
}
'''
for platform in ['gb','fc']:
    prefix='// Learn deferred VRAM writes, retained source pointers and queue capacity units.\n'
    if platform=='gb':
        prefix+='#include "gb_tile_example.h"\n#include "vram_example_colors.h"\nconst u8 shape_patterns[48]={'+','.join(map(str,gb_patterns))+'};\n#define MAP_BASE 0x9800\n#define EXPECTED_CAPACITY 32\n#define EXPECTED_USED 7\n#define EXPECTED_LATCHED_RETURN 1\n#define EXPECTED_SINGLE_SIZE 1\n'
        replacements={'DEMO_BEGIN':'tile_example_begin(); M_LCDC=0;\n    __vram_copy(0x8010,shape_patterns,48);\n    vram_example_color(2,2,3,1,1);\n    vram_example_color(2,4,4,3,2);\n    vram_example_color(10,4,3,2,3);\n    vram_example_color(2,8,3,1,1);\n    vram_example_color(6,8,2,1,2);\n    vram_example_color(10,8,5,1,3);\n    vram_example_color(18,10,1,1,1);','DEMO_DISPLAY':'M_LCDC=0x91;','FC_READY_TEST':'','FC_COMMIT':'','RESTORE_SCROLL':''}
    else:
        prefix+='#include "fc_common.h"\n#define MAP_BASE 0x2000\n#define EXPECTED_CAPACITY 128\n#define EXPECTED_USED 52\n#define EXPECTED_LATCHED_RETURN 0\n#define EXPECTED_SINGLE_SIZE 4\n'
        replacements={'DEMO_BEGIN':'m_init(); m_wait();\n    __ppu_ctrl_set(0); __ppu_mask_set(0);','DEMO_DISPLAY':'__scroll_set(0,0); __ppu_ctrl_set(0x80); __ppu_mask_set(0x0A);',
          'FC_READY_TEST':'// An uncommitted FC queue must stay queued even when exec is called.\n    vram_flush_now();\n    if (vram_get_queue_used()!=used) failures++;',
          'FC_COMMIT':'__vramq_commit();','RESTORE_SCROLL':'__scroll_set(0,0);'}
    text=body
    for key,value in replacements.items():text=text.replace(key,value)
    text='\n'.join(line.rstrip() for line in (prefix+text).splitlines())+'\n'
    (SITE/'samples/api-examples'/platform/'vram_queue_shapes.c').write_text(text,encoding='utf-8')
print('Two visual queue examples and an original geometric CHR extension written.')
