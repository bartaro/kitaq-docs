"""Author original shapes and build assets consumed by both ZX0 teaching ROMs."""
from pathlib import Path
import subprocess
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
patterns=[[255]*8,[24,60,126,255,255,126,60,24],[170,85]*4]
for platform in ['gb','fc']:
 folder=SITE/'samples/api-examples'/platform/'zx0_assets';folder.mkdir(parents=True,exist_ok=True)
 host=REPOS/('kitaq'+platform)/('kitaq'+platform+'-zx0.exe')
 tiles=[]
 for index,mask in enumerate(patterns):
  low=mask if index in [0,2] else [0]*8;high=mask if index in [1,2] else [0]*8
  tiles+=sum(([lo,hi] for lo,hi in zip(low,high)),[]) if platform=='gb' else low+high
 for name,raw,fmt in [('tiles',bytes(tiles),'zx0'),('map',bytes(128+i%3 for i in range(16)),'zx0'),('auto',bytes([128])*16,'auto')]:
  (folder/(name+'.bin')).write_bytes(raw)
  p=subprocess.run([str(host),str(folder/(name+'.bin')),str(folder/(name+'.h')),'--format='+fmt,'--header=packed_'+name],capture_output=True,timeout=60)
  assert p.returncode==0,p.stderr
 common='''// Copyright (c) 2026 DAISUKE OBA. MIT License.
// Original square, diamond and checker tiles illustrate three decoding paths.
#include "zx0.c"
#include "zx0_assets/tiles.h"
#include "zx0_assets/map.h"
#include "zx0_assets/auto.h"
u8 decoded_map[16];
u8 decoded_auto[16];
u8 tile_workspace[48];
u8 failures;
'''
 if platform=='gb':
  setup='''#include "gb_common.h"
__location(0xFF4F) u8 Z_VBK;
__location(0xFF68) u8 Z_BGPI;
__location(0xFF69) u8 Z_BGPD;
__prg_rom u8 colors[]={0,0,255,127,31,0,0,124};
void main(){u16 count;u8 n;
    __wait_vblank();M_LCDC=0;
    Z_VBK=1;__vram_fill(0x9800,0,1024);Z_VBK=0;
    __vram_copy(0x8000,manual_font,2048);__vram_fill(0x9800,0,1024);
    M_BGP=0xE4;Z_BGPI=128;for(n=0;n<8;n++){Z_BGPD=colors[n];}
'''
  vram='count=zx0_decompress_vram(0x8800,packed_tiles,packed_tiles_SIZE);'
  draw='''    m_text(2,0,"ZX0 ASSET DECODE");
    m_text(2,3,"RAM MAP");m_text(2,7,"AUTO RLE MAP");m_text(2,11,"VRAM TILES");
    for(n=0;n<16;n++){m_put(n+2,5,decoded_map[n]);m_put(n+2,9,decoded_auto[n]);m_put(n+2,13,(u8)(128+n%3));}
    m_text(2,16,failures==0?"CHECKS OK":"CHECKS FAILED");
    M_LCDC=0x91;while(1){__wait_vblank();}
}
'''
 else:
  setup='''#include "physics_font_fc.h"
__location(0x2007) u8 Z_DATA;
__prg_rom u8 colors[]={15,48,22,18,15,48,22,18,15,48,22,18,15,48,22,18};
// Write text directly while rendering is disabled; each character is a font tile.
void text(u8 x,u8 y,const u8* message){__ppu_addr(0x2000+(u16)y*32+x);while(*message){Z_DATA=*message++;}}
void main(){u16 count;u16 position;u8 n;
    __ppu_mask_set(0);__ppu_ctrl_set(0);
    for(position=0;position<2048;position+=128){__vram_write(position,physics_font_fc+position,128);}
    __palette_bg_load(colors);__ppu_addr(0x2000);for(position=0;position<1024;position++){Z_DATA=0;}
'''
  vram='count=zx0_decompress_vram(0x0800,tile_workspace,48,packed_tiles,packed_tiles_SIZE);'
  draw='''    text(2,0,"ZX0 ASSET DECODE");
    text(2,3,"RAM MAP");text(2,7,"AUTO RLE MAP");text(2,11,"VRAM TILES");
    __vram_write(0x20A2,decoded_map,16);__vram_write(0x2122,decoded_auto,16);
    __ppu_addr(0x21A2);for(n=0;n<16;n++){Z_DATA=(u8)(128+n%3);}
    text(2,16,failures==0?"CHECKS OK":"CHECKS FAILED");
    __scroll_set(0,0);__ppu_ctrl_set(0);__ppu_mask_set(0x0A);while(1){}
}
'''
 body='''    failures=0;
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
    '''+vram+'''
    if(count!=48||zx0_error!=ZX0_OK)failures++;
    // example:zx0_decompress_vram:end
'''
 (folder.parent/'zx0_decode.c').write_text(common+setup+body+draw,encoding='utf-8')
print('Original GB/FC compressed assets and three-API teaching programs written.')
