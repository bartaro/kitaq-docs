// Demonstrate __farmemcpy: copy banked tile bytes and restore the selected bank.
// Build with --mapper=mmc1 --board=surom512 for CHR RAM and common-bank asset-upload code.
// Omitting --nes-chr on a generic board instead creates a blank CHR ROM.
#define MANUAL_ASSET_FC
#pragma bank 0
#include "fc_common.h"
#include "font_gb.h"
#include "bank.c"
#include "asset.c"
#include "asset_example_data_fc.h"
#include "asset_example_checks.h"
__prg_rom u8 asset_palette[16]={0x0F,0x30,0x10,0x30,0x0F,0x26,0x26,0x26,0x0F,0x22,0x22,0x22,0x0F,0x2A,0x2A,0x2A};
u8 tile_index;
u8 line;
u16 font_offset;

// Write one byte with the documented immediate PPU fill intrinsic.
void write_ppu_byte(u16 address,u8 value) { __vram_fill(address,value,1); }

// Convert the original GB-interleaved font to FC's separate planes in a 16-byte buffer.
void load_font_chr_ram() {
    font_offset=0;
    for(tile_index=0;tile_index<128;tile_index++) {
        for(line=0;line<8;line++) {
            buffer[(__safe_index u8)line]=manual_font[(__safe_index u16)(font_offset+(u16)line*2)];
            buffer[(__safe_index u8)(line+8)]=manual_font[(__safe_index u16)(font_offset+(u16)line*2+1)];
        }
        __vram_write(font_offset,buffer,16);
        font_offset=(u16)(font_offset+16);
    }
}

void main() {
    m_init();m_wait();__ppu_ctrl_set(0);__ppu_mask_set(0);
    load_font_chr_ram();__palette_bg_load(asset_palette);
    bank_switch(1); // Initialize the library shadow and the compiler's mapper state together.
    asset_checks();
    // example:asset_load_tiles:start
    loaded=asset_load_tiles(0,0x0010); // 144 bytes: library uploads chunks of 128 and 16 bytes.
    expect(loaded==1 && bank_get_current()==1 && *asset_bank_marker==0xA1,24);
    // LCD and NMI are off; CHR RAM is writable. The library selects payload bank 2 and restores bank 1.
    // example:asset_load_tiles:end
    expect(asset_load_tiles(2,0x0010)==0 && asset_load_tiles(4,0x0010)==0,25);
    for(i=0;i<9;i++) write_ppu_byte((u16)(0x2082+i),(u8)(1+i));
    write_ppu_byte(0x23C8,4);write_ppu_byte(0x23C9,5);write_ppu_byte(0x23CA,5); // Red row at tile y=4.
    // example:__farmemcpy:start
    __farmemcpy(buffer,payload_bank,(u16)payload_pointer,32);
    expect(*asset_bank_marker==0xA1 && bank_get_current()==1,27);
    for(i=0;i<32;i++) expect(buffer[(__safe_index u8)i]==expected_shape_byte(i),28);
    buffer[32]=0x55;
    __farmemcpy(buffer+32,2,(u16)asset_shapes,0);
    expect(buffer[32]==0x55 && *asset_bank_marker==0xA1,30);
    // example:__farmemcpy:end
    __vram_write(0x00A0,buffer,32);
    write_ppu_byte(0x2102,10);write_ppu_byte(0x2103,11);write_ppu_byte(0x23D0,8); // Blue pair at tile y=8.
    expect(asset_load_raw(1,buffer,32)==1,31);
    __vram_write(0x00C0,buffer,32);
    write_ppu_byte(0x2182,12);write_ppu_byte(0x2183,13);write_ppu_byte(0x23D8,12); // Green pair at tile y=12.
    __scroll_set(0,0);__ppu_ctrl_set(0x80);__ppu_mask_set(0x0A);
    m_text(1,0,"ASSET BANKS");m_wait();
    m_text(1,3,"TILE ASSET 144B");m_wait();
    m_text(6,8,"FARMEMCPY");m_wait();m_text(6,12,"LOAD RAW");m_wait();
    m_text(1,15,"FAILED CHECKS");
    m_put(20,15,(u8)('0'+failures/100));m_put(21,15,(u8)('0'+(failures/10)%10));m_put(22,15,(u8)('0'+failures%10));m_wait();
    m_text(1,17,"FIRST FAILURE");m_put(20,17,(u8)('0'+first_failure/10));m_put(21,17,(u8)('0'+first_failure%10));m_wait();
    while(1) { m_wait(); }
}
