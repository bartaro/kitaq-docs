#pragma once
// Print a five-digit unsigned value so byte and word draws share one display.
void rng_value(u8 row,const u8* text,u16 value){
    rng_label(row,text);
    rng_digit(RNG_VALUE_COL,row,(u8)('0'+value/10000));
    rng_digit(RNG_VALUE_COL+1,row,(u8)('0'+value/1000%10));
    rng_digit(RNG_VALUE_COL+2,row,(u8)('0'+value/100%10));
    rng_digit(RNG_VALUE_COL+3,row,(u8)('0'+value/10%10));
    rng_digit(RNG_VALUE_COL+4,row,(u8)('0'+value%10));
    rng_flush();
}
