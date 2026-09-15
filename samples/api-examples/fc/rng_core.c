// Observe reproducible FC byte draws, reseeding and the zero-seed fallback.
#include "fc_common.h"
#define RNG_VALUE_COL 25
__prg_rom u8 rng_palette[16]={0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22,0x0F,0x22,0x22,0x22};
void rng_flush(){__vramq_commit();__vramq_exec();}
void rng_label(u8 row,const u8* text){m_text(1,row,text);rng_flush();}
void rng_digit(u8 x,u8 y,u8 value){m_put(x,y,value);}
#include "rng_example_display.h"
u8 first;
u8 second;
u8 third;
u8 repeated;
u8 zero;
u8 failures;
void main(){
    __ppu_off();__ppu_ctrl_set(0);__vramq_clear();__oam_clear();
    __palette_bg_load(rng_palette);__nametable_rect(0,0,32,30,0);failures=0;
    // example:__rng8:start
    __rng_seed(0x1234);
    first=__rng8();second=__rng8();third=__rng8(); // FC sequence: 19, 137, 240.
    // example:__rng8:end
    // example:__rng_seed:start
    __rng_seed(0x1234);
    repeated=__rng8(); // The first byte is 19 again.
    __rng_seed(0);
    zero=__rng8(); // The next draw uses the FC fallback state and returns 255.
    // example:__rng_seed:end
    if(first!=19 || second!=137 || third!=240 || repeated!=19 || zero!=255)failures++;
    rng_label(0,"SEEDED RNG FC");rng_value(2,"FIRST",first);
    rng_value(4,"SECOND",second);rng_value(6,"THIRD",third);
    rng_value(8,"RESEEDED",repeated);rng_value(10,"ZERO SEED",zero);
    rng_value(16,"FAILED",failures);__scroll_set(0,0);__ppu_mask_set(0x0A);while(1){}
}
