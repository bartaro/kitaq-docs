// Load bank-qualified descriptors and original shape payloads, with visible results.
#pragma bank 0
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "asset.c"
#include "asset_example_data_gb.h"
#include "asset_example_checks.h"
void __bankswitch(u8 bank);
void __far_memcpy(void* dst,u8 bank,const void* src,u16 len);

void main() {
    tile_example_begin();
    __bankswitch(1); // Keep both cartridge mapping and compiler bank shadow consistent.
    expect(__bankof(asset_bank_marker)==1 && __bankof(asset_shapes)==2 && __bankof(asset_descriptors)==3,31);
    asset_checks();
    // example:asset_load_tiles:start
    __bankswitch(payload_bank); // GB tile upload expects the payload bank already visible.
    loaded=asset_load_tiles(0,0x8010); // Nine tiles = 144 bytes, LCD off.
    expect(loaded==1,24);
    __bankswitch(1);
    // example:asset_load_tiles:end
    expect(asset_load_tiles(2,0x8010)==0 && asset_load_tiles(4,0x8010)==0,25);
    for(i=0;i<144;i++) expect(*((u8*)(0x8010+i))==expected_shape_byte(i),26);
    for(i=0;i<9;i++) __settile_unsafe((u8)(2+i),4,(u8)(1+i));
    vram_example_color(2,4,9,1,1); // Red triangle/outline/half repeated three times.
    // example:__farmemcpy:start
    __farmemcpy(buffer,payload_bank,payload_pointer,32);
    expect(*asset_bank_marker==0xA1,27); // Source bank 2 was selected only for the copy.
    for(i=0;i<32;i++) expect(buffer[(__safe_index u8)i]==expected_shape_byte(i),28);
    // example:__farmemcpy:end
    __vram_copy(0x80A0,buffer,32);
    __settile_unsafe(2,8,10); __settile_unsafe(3,8,11);
    vram_example_color(2,8,2,1,2); // Blue triangle and outline.
    // example:__far_memcpy:start
    __far_memcpy(buffer,2,asset_shapes,32); // Same backend as __farmemcpy.
    expect(*asset_bank_marker==0xA1,29);
    for(i=0;i<32;i++) expect(buffer[(__safe_index u8)i]==expected_shape_byte(i),32);
    buffer[32]=0x55;
    __far_memcpy(buffer+32,2,asset_shapes,0); // Zero count writes no bytes and restores the bank.
    expect(buffer[32]==0x55 && *asset_bank_marker==0xA1,30);
    // example:__far_memcpy:end
    __vram_copy(0x80C0,buffer,32);
    __settile_unsafe(2,12,12); __settile_unsafe(3,12,13);
    vram_example_color(2,12,2,1,3); // Green triangle and outline.
    M_LCDC=0x91;
    m_text(1,0,"ASSET BANKS");
    m_text(1,3,"TILE ASSET 144B");
    m_text(6,8,"FARMEMCPY"); m_text(6,12,"FAR_MEMCPY");
    m_text(1,15,"FAILED CHECKS");
    m_put(16,15,(u8)('0'+failures/100));m_put(17,15,(u8)('0'+(failures/10)%10));m_put(18,15,(u8)('0'+failures%10));
    m_text(1,17,"FIRST FAILURE");m_put(16,17,(u8)('0'+first_failure/10));m_put(17,17,(u8)('0'+first_failure%10));
    while(1) { m_wait(); }
}
