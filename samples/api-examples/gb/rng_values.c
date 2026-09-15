// Reproduce a seeded sequence and compare byte/word library entry points.
#include "gb_tile_color_example.h"
#include "rpg.h"
#define RNG_VALUE_COL 14
void rng_label(u8 row,const u8* text){m_text(1,row,text);}
void rng_digit(u8 x,u8 y,u8 value){m_put(x,y,value);}
void rng_flush(){}
#include "rng_example_display.h"
u8 first;
u8 second;
u8 repeated;
u8 wrapped;
u8 nextbyte;
u16 word;
u16 nextword;
u8 failures;
void main(){
    tile_color_example_begin();failures=0;
    // example:__rng8:start
    __rng_seed(0x1234);
    first=__rng8();  // 2: the first draw from this seed on GB.
    second=__rng8(); // 34: a second draw advances the same shared state.
    // example:__rng8:end
    // example:__rng_seed:start
    __rng_seed(0x1234);
    repeated=__rng8(); // Reseeding reproduces the first byte, 2.
    // example:__rng_seed:end
    // example:rng8:start
    // example:rng_seed:start
    rng_seed(0x1234); // Reset the same generator used by the intrinsics.
    wrapped=rng8(); // One byte draw: 2 after the preceding seed.
    // example:rng_seed:end
    // example:rng8:end
    // example:rng_next8:start
    rng_seed(0x1234);
    nextbyte=rng_next8(); // One draw, just like rng8(): 2.
    // example:rng_next8:end
    // example:rng16:start
    rng_seed(0x1234);
    word=rng16(); // First draw 2 is high, second draw 34 is low: 0x0222 = 546.
    // example:rng16:end
    // example:rng_next16:start
    rng_seed(0x1234);
    nextword=rng_next16(); // The same two-draw word: 546.
    // example:rng_next16:end
    if(first!=2 || second!=34 || repeated!=2 || wrapped!=2 || nextbyte!=2 || word!=546 || nextword!=546)failures++;
    M_LCDC=0x91;rng_label(0,"SEEDED RNG GB");
    rng_value(2,"FIRST",first);rng_value(4,"SECOND",second);
    rng_value(6,"RESEEDED",repeated);rng_value(8,"RNG8",wrapped);
    rng_value(10,"NEXT8",nextbyte);rng_value(12,"RNG16",word);
    rng_value(14,"NEXT16",nextword);rng_value(16,"FAILED",failures);
    while(1){m_wait();}
}
