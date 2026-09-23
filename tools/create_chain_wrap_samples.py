"""Create a small wrapped-distance lesson for each target's font helpers."""
from pathlib import Path
SITE=Path(__file__).resolve().parents[1]
BODY='''// Shortest signed distance on a field whose edges join.
// Positive moves toward increasing coordinates; no objects are moved here.
#include "PLATFORM_common.h"
#include "chain.c"
__location(RESULT) s16 distances[5];

// Print the computed sign and two decimal digits, including a leading zero.
void show_distance(u8 row, s16 distance) {
    u8 magnitude;
    m_put(15,row,distance<0 ? '-' : '+');
    magnitude=(u8)(distance<0 ? 0-distance : distance);
    m_put(16,row,'0'+magnitude/10);
    m_put(17,row,'0'+magnitude%10);
    m_wait();
}
void main() {
    // The arguments are target, current, size. Coordinates are normalized.
    // example:chain_wrap_delta:start
    distances[0]=chain_wrap_delta(1,159,160);   // +2: cross the right edge.
    distances[1]=chain_wrap_delta(159,1,160);   // -2: cross the left edge.
    distances[2]=chain_wrap_delta(80,0,160);    // +80: keep the direct sign.
    distances[3]=chain_wrap_delta(0,80,160);    // -80: same-length routes.
    distances[4]=chain_wrap_delta(0,0,1);       // 0: the only valid position.
    // example:chain_wrap_delta:end
    m_init();
    m_text(0,0,"WRAPPED DISTANCE"); m_wait();
    m_text(0,2,"FIELD: 160 PIXELS"); m_wait();
    m_text(0,4,"159 -> 1"); show_distance(4,distances[0]);
    m_text(0,6,"1 -> 159"); show_distance(6,distances[1]);
    m_text(0,8,"TIE 0 -> 80"); show_distance(8,distances[2]);
    m_text(0,10,"TIE 80 -> 0"); show_distance(10,distances[3]);
    m_text(0,12,"FIELD: 1 PIXEL"); m_wait();
    m_text(0,14,"0 -> 0"); show_distance(14,distances[4]);
    m_text(0,16,"SIGNED PIXEL DELTA"); m_wait();
    while(1) { m_wait(); }
}
'''
for platform,address in [('gb','0xC600'),('fc','0x0600')]:
    text=BODY.replace('PLATFORM',platform).replace('RESULT',address)
    if platform=='gb':text=text.replace('"gb_common.h"','"gb_tile_example.h"').replace('    m_init();','    tile_example_begin(); M_LCDC=0x91;')
    (SITE/f'samples/api-examples/{platform}/chain_wrap.c').write_text(text,encoding='ascii')
