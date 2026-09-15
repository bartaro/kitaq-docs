// Choose a bounded value, an approximate chance and a weighted item.
#include "gb_tile_color_example.h"
#include "rpg.h"
#define RNG_VALUE_COL 14
void rng_label(u8 row,const u8* text){m_text(1,row,text);}
void rng_digit(u8 x,u8 y,u8 value){m_put(x,y,value);}
void rng_flush(){}
#include "rng_example_display.h"
u8 weights[3];
u8 bounded;
u8 alias;
u8 chance;
u8 chosen;
u8 empty;
u8 zero;
u8 afterzero;
u8 failures;
void main(){
    tile_color_example_begin();failures=0;
    // example:rand_range:start
    rng_seed(0x1234);
    bounded=rand_range(10); // An index from 0 through 9; this seed yields 2.
    // example:rand_range:end
    // example:rng_range:start
    rng_seed(0x1234);
    alias=rng_range(10); // The same exclusive upper bound and result, 2.
    // example:rng_range:end
    // example:rng_chance:start
    rng_seed(0x1234);
    chance=rng_chance(50); // Here 2 % 100 < 50, so the result is 1 (true).
    // example:rng_chance:end
    // example:weighted_choice:start
    weights[0]=1;weights[1]=3;weights[2]=6;
    rng_seed(0x1234);
    chosen=weighted_choice(weights,3); // 546 % 10 = 6 selects index 2.
    empty=weighted_choice((const u8*)0,0); // No items: 0 is a fallback, not a chosen item.
    // example:weighted_choice:end
    // A zero bound returns immediately and does not consume a draw.
    rng_seed(0x1234);zero=rand_range(0);afterzero=rng8();
    if(bounded!=2 || alias!=2 || chance!=1 || chosen!=2 || empty!=0 || zero!=0 || afterzero!=2)failures++;
    M_LCDC=0x91;rng_label(0,"RNG CHOICES GB");
    rng_value(2,"RANGE 10",bounded);rng_value(4,"ALIAS 10",alias);
    rng_value(6,"CHANCE 50",chance);rng_value(8,"WEIGHT INDEX",chosen);
    rng_value(10,"EMPTY LIST",empty);rng_value(12,"ZERO BOUND",zero);
    rng_value(14,"NEXT BYTE",afterzero);rng_value(16,"FAILED",failures);
    while(1){m_wait();}
}
