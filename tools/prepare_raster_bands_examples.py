"""Create distinct, original band/HUD/window/color teaching scenes."""
from pathlib import Path
import json
SITE=Path(__file__).resolve().parents[1];OUT=SITE/'samples/api-examples/gb'
specs=[
 ('bands','BANDS 0 8 16',[(0,0,0),(64,8,0),(104,16,0)], [('Raster_Push','Raster_Push(0,0,0);Raster_Push(64,8,0);'),('Raster_PushEx','Raster_PushEx(104,16,0,7,0,KQ_RASTER_BG|KQ_RASTER_WIN_HIDE);')]),
 ('hud_top','FIXED TOP HUD',[(0,0,0),(32,8,8)],[('Raster_BuildHudTop','Raster_BuildHudTop(32,8,8);')]),
 ('hud_bottom','FIXED BOTTOM HUD',[(0,8,8),(96,0,0)],[('Raster_BuildHudBottom','Raster_BuildHudBottom(96,8,8);')]),
 ('parallax2','PARALLAX 0 16',[(0,0,0),(64,16,0)],[('Raster_BuildParallax2','Raster_BuildParallax2(64,0,16,0);')]),
 ('parallax3','PARALLAX 0 8 16',[(0,0,0),(64,8,0),(104,16,0)],[('Raster_BuildParallax3','Raster_BuildParallax3(64,104,0,8,16,0);')]),
 ('window_raw','RAW WX 31 WY 48',[(0,0,0)],[('Raster_PushWindowRaw','Raster_PushWindowRaw(0,31,48,KQ_RASTER_WIN_SHOW);')]),
 ('window_screen','SCREEN X24 Y48',[(0,0,0)],[('Raster_PushWindowScreen','Raster_PushWindowScreen(0,24,48,KQ_RASTER_WIN_SHOW);')]),
 ('bg_window','BG 8 WINDOW 24',[(0,8,0)],[('Raster_PushBgWindowScreen','Raster_PushBgWindowScreen(0,8,0,24,48,KQ_RASTER_WIN_SHOW);')]),
 ('color','',[],[('Raster_PushBgColor0','Raster_PushBgColor0(0,0x7C00);Raster_PushBgColor0(64,0x001F);Raster_PushBgColor0(112,0x03E0);')]),
]
records=[]
def marked(api,call):return f'// example:{api}:start\n{call}\n// example:{api}:end\n'
for group,title,bands,calls in specs:
 is_window='window' in group
 source='''// Copyright (c) 2026 DAISUKE OBA. MIT License.
// Compare fixed and scrolling original rectangles, or window/color bands.
#include "gb_tile_example.h"
#include "vram_example_colors.h"
#include "scroll.c"
#include "raster.c"
__location(0xC600) u8 result[4];
void main(){u8 x;u8 y;tile_example_begin();M_LCDC=0;
    Scroll_Init();Scroll_WindowHide();__vram_fill(0x87E0,255,16);
'''
 if group!='color':
  source+='for(y=2;y<4;y++)for(x=4;x<7;x++)m_put(x,y,126);for(y=10;y<12;y++)for(x=4;x<7;x++)m_put(x,y,126);for(y=14;y<16;y++)for(x=4;x<7;x++)m_put(x,y,126);vram_example_color(4,2,3,2,1);vram_example_color(4,10,3,2,1);vram_example_color(4,14,3,2,1);\n'
  source+=f'm_text(1,{17 if group=="hud_bottom" else 0},"{title}");\n'
 if is_window:
  source+='''// Window tile coordinates are independent of the background map.
for(y=1;y<3;y++){__vram_fill((u16)(0x9C00+(u16)y*32+1),126,2);}
if(__cgb_is_cgb()){__cgb_safe_set_vbk(1);for(y=1;y<3;y++){__vram_memset_unsafe((u16)(0x9C00+(u16)y*32+1),2,2);}__cgb_safe_set_vbk(0);}
'''
 if group=='bands':
  source+=marked('Raster_Disable','Raster_Disable();')+marked('Raster_Init','Raster_Init();')+marked('Raster_Clear','Raster_Clear();')
 else:source+='Raster_Init();\n'
 for api,call in calls:source+=marked(api,call)
 if group=='bands':source+=marked('Raster_GetCount','result[0]=Raster_GetCount();')+marked('Raster_GetLastError','result[1]=Raster_GetLastError();')
 else:source+='result[0]=Raster_GetCount();result[1]=Raster_GetLastError();\n'
 source+='M_LCDC='+('0xD1' if is_window else '0x91')+';\n'
 source+=marked('Raster_Commit','result[2]=Raster_Commit();') if group=='bands' else 'result[2]=Raster_Commit();\n'
 source+='result[3]=165;while(1){}\n}\n'
 path=OUT/('raster_bands_'+group+'.c');path.write_text(source,encoding='utf-8')
 records.append(dict(group=group,source=path.relative_to(SITE).as_posix(),title=title,title_y=17 if group=='hud_bottom' else 0,bands=bands,window=is_window,modes=['cgb'] if group=='color' else ['dmg','cgb'],expected=[3 if group=='color' else len(bands),0,0,165],apis=[a for a,_ in calls]+(['Raster_Init','Raster_Clear','Raster_Disable','Raster_GetCount','Raster_GetLastError','Raster_Commit'] if group=='bands' else [])))
(SITE/'tools/api_descriptions/raster_bands_examples.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Nine original raster-band teaching scenes authored.')
