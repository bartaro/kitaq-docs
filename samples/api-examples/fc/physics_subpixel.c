// Game-side eighth-pixel integration using the types in physics2d.h.
// physics2d.h provides types/constants; this step routine belongs to the sample.
#include "fc_common.h"
#include "physics2d.h"
__location(0x0600) u16 result[80];
KQ2DPosition position;
KQ2DFraction fraction;
KQ2DSpeed speed;
KQ2DDirection direction;
__prg_rom u8 colors[16]={15,22,22,22,15,22,22,22,15,22,22,22,15,22,22,22};

void game_step() {
    u16 total;
    // Widen before adding speed so an 8-bit intermediate cannot wrap.
    total=(u16)position*KQ2D_SUBPIXEL_ONE+fraction;
    if(direction==KQ2D_DIR_POSITIVE) total=total+speed;
    else if(direction==KQ2D_DIR_NEGATIVE) total=total-speed;
    position=(KQ2DPosition)(total>>KQ2D_SUBPIXEL_BITS);
    fraction=(KQ2DFraction)(total&KQ2D_SUBPIXEL_MASK);
}

void main() {
    u8 i;
    __ppu_off(); __ppu_ctrl_set(0); __vramq_clear(); __oam_clear();
    __nametable_rect(0,0,32,30,0); __palette_bg_load(colors);
    for(i=0;i<80;i++) result[i]=0;
    position=24; fraction=0; speed=4; direction=KQ2D_DIR_POSITIVE;
    __nametable_rect(position/8,8,2,2,1);
    // Sixteen half-pixel ticks produce eight whole pixels.
    for(i=0;i<16;i++) game_step();
    result[0]=position; result[1]=fraction;
    __nametable_rect(position/8,14,2,2,1);
    // Negative direction subtracts magnitude, provided the result stays >= 0.
    direction=KQ2D_DIR_NEGATIVE;
    for(i=0;i<8;i++) game_step();
    result[2]=position; result[3]=fraction;
    direction=KQ2D_DIR_NONE; game_step(); result[4]=position;
    result[79]=0xA55A;
    // Commit one label per frame to stay within the 32-entry intrinsic queue.
    __scroll_set(0,0); __ppu_ctrl_set(0x80); __ppu_mask_set(0x0A);
    m_text(1,0,"HALF-PIXEL STEPS"); m_wait();
    m_text(1,6,"BEFORE X=24"); m_wait();
    m_text(1,12,"16 TICKS X=32"); m_wait();
    while(1) {}
}
