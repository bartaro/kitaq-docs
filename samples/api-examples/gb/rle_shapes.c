// Decode three original tiles through RAM, banked RAM and direct VRAM paths.
#pragma bank 0
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "rle.c"
void __bankswitch(u8 bank);
#pragma fixed_bank 0
// Count/value pairs followed by a single zero count: nine encoded bytes, 48 decoded bytes.
__prg_rom u8 local_rle[9]={18,255,12,129,2,255,16,240,0};
#pragma fixed_bank 1
__prg_rom u8 rle_bank_marker[1]={0xA1};
#pragma fixed_bank 2
__prg_rom u8 banked_rle[9]={18,255,12,129,2,255,16,240,0};
#pragma fixed_bank 0
u8 near_buffer[50];
u8 far_buffer[50];
u16 near_count;
u16 far_count;
u16 vram_count;
u8 failures;
u8 i;
u8 expected_byte(u8 offset){
    if(offset<18)return 255;
    if(offset<30)return 129;
    if(offset<32)return 255;
    return 240;
}
void count_label(u8 row,const u8* label,u16 value){
    m_text(1,row,label);m_put(16,row,(u8)('0'+value/100));
    m_put(17,row,(u8)('0'+value/10%10));m_put(18,row,(u8)('0'+value%10));
}
void main(){
    tile_example_begin();failures=0;__bankswitch(1);
    for(i=0;i<50;i++){near_buffer[i]=204;far_buffer[i]=204;}
    // example:rle_decode:start
    near_count=rle_decode(near_buffer+1,local_rle); // 48 bytes in writable RAM.
    __vram_copy(0x8800,near_buffer+1,near_count); // Upload those bytes while the LCD is off.
    // example:rle_decode:end
    // example:rle_decode_far:start
    far_count=rle_decode_far(far_buffer+1,2,banked_rle); // Read encoded pairs from ROM bank 2.
    if(*rle_bank_marker!=0xA1)failures++; // ROM bank 1 must be visible again.
    __vram_copy(0x8830,far_buffer+1,far_count);
    // example:rle_decode_far:end
    // example:__rle_decode_vram:start
    vram_count=__rle_decode_vram(0x8860,2,banked_rle); // Expand directly to 48 bytes of tile data.
    if(*rle_bank_marker!=0xA1)failures++;
    // example:__rle_decode_vram:end
    if(near_count!=48 || far_count!=48 || vram_count!=48)failures++;
    if(near_buffer[0]!=204 || near_buffer[49]!=204 || far_buffer[0]!=204 || far_buffer[49]!=204)failures++;
    for(i=0;i<48;i++){
        if(near_buffer[i+1]!=expected_byte(i) || far_buffer[i+1]!=expected_byte(i) || *((u8*)(0x8860+i))!=expected_byte(i))failures++;
    }
    for(i=0;i<3;i++){
        __settile_unsafe((u8)(2+i*3),4,(u8)(128+i));
        __settile_unsafe((u8)(2+i*3),9,(u8)(131+i));
        __settile_unsafe((u8)(2+i*3),14,(u8)(134+i));
    }
    vram_example_color(2,4,7,1,1); // Red on CGB: near RAM path.
    vram_example_color(2,9,7,1,3); // Green on CGB: far RAM path.
    vram_example_color(2,14,7,1,2); // Blue on CGB: direct VRAM path.
    M_LCDC=0x91;m_text(1,0,"RLE TILE DECODING");
    count_label(2,"RLE TO RAM",near_count);count_label(7,"BANKED RAM",far_count);
    count_label(12,"DIRECT VRAM",vram_count);count_label(17,"FAILED",failures);
    while(1){m_wait();}
}
