// Copyright (c) 2026 DAISUKE OBA. MIT License.
// Original square, diamond and checker tiles illustrate three decoding paths.
#include "zx0.c"
#include "zx0_assets/tiles.h"
#include "zx0_assets/map.h"
#include "zx0_assets/auto.h"
u8 decoded_map[16];
u8 decoded_auto[16];
u8 tile_workspace[48];
u8 failures;
#include "gb_common.h"
__location(0xFF4F) u8 Z_VBK;
__location(0xFF68) u8 Z_BGPI;
__location(0xFF69) u8 Z_BGPD;
__prg_rom u8 colors[]={0,0,255,127,31,0,0,124};
void main(){u16 count;u8 n;
    __wait_vblank();M_LCDC=0;
    Z_VBK=1;__vram_fill(0x9800,0,1024);Z_VBK=0;
    __vram_copy(0x8000,manual_font,2048);__vram_fill(0x9800,0,1024);
    M_BGP=0xE4;Z_BGPI=128;for(n=0;n<8;n++){Z_BGPD=colors[n];}
    failures=0;
    // Decode compressed tile IDs into ordinary CPU RAM before drawing the map.
    // example:zx0_decompress:start
    count=zx0_decompress(decoded_map,16,packed_map,packed_map_SIZE);
    if(count!=16||zx0_error!=ZX0_OK)failures++;
    // example:zx0_decompress:end
    // The host selected RLE for this constant map and recorded it in KQA1.
    // example:asset_decompress:start
    count=asset_decompress(decoded_auto,16,packed_auto,packed_auto_SIZE);
    if(count!=16||zx0_error!=ZX0_OK)failures++;
    // example:asset_decompress:end
    // Upload three original tiles with the display stopped.
    // example:zx0_decompress_vram:start
    count=zx0_decompress_vram(0x8800,packed_tiles,packed_tiles_SIZE);
    if(count!=48||zx0_error!=ZX0_OK)failures++;
    // example:zx0_decompress_vram:end
    m_text(2,0,"ZX0 ASSET DECODE");
    m_text(2,3,"RAM MAP");m_text(2,7,"AUTO RLE MAP");m_text(2,11,"VRAM TILES");
    for(n=0;n<16;n++){m_put(n+2,5,decoded_map[n]);m_put(n+2,9,decoded_auto[n]);m_put(n+2,13,(u8)(128+n%3));}
    m_text(2,16,failures==0?"CHECKS OK":"CHECKS FAILED");
    M_LCDC=0x91;while(1){__wait_vblank();}
}
