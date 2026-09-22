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
#include "physics_font_fc.h"
__location(0x2007) u8 Z_DATA;
__prg_rom u8 colors[]={15,48,22,18,15,48,22,18,15,48,22,18,15,48,22,18};
// Write text directly while rendering is disabled; each character is a font tile.
void text(u8 x,u8 y,const u8* message){__ppu_addr(0x2000+(u16)y*32+x);while(*message){Z_DATA=*message++;}}
void main(){u16 count;u16 position;u8 n;
    __ppu_mask_set(0);__ppu_ctrl_set(0);
    for(position=0;position<2048;position+=128){__vram_write(position,physics_font_fc+position,128);}
    __palette_bg_load(colors);__ppu_addr(0x2000);for(position=0;position<1024;position++){Z_DATA=0;}
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
    count=zx0_decompress_vram(0x0800,tile_workspace,48,packed_tiles,packed_tiles_SIZE);
    if(count!=48||zx0_error!=ZX0_OK)failures++;
    // example:zx0_decompress_vram:end
    text(2,0,"ZX0 ASSET DECODE");
    text(2,3,"RAM MAP");text(2,7,"AUTO RLE MAP");text(2,11,"VRAM TILES");
    __vram_write(0x20A2,decoded_map,16);__vram_write(0x2122,decoded_auto,16);
    __ppu_addr(0x21A2);for(n=0;n<16;n++){Z_DATA=(u8)(128+n%3);}
    text(2,16,failures==0?"CHECKS OK":"CHECKS FAILED");
    __scroll_set(0,0);__ppu_ctrl_set(0);__ppu_mask_set(0x0A);while(1){}
}
