"""Generate original integer sine/reciprocal tables from mathematical formulas."""
from pathlib import Path
import math
ROOT=Path(__file__).resolve().parents[3]
def rows(values):return '\n'.join('    '+','.join(map(str,values[n:n+16]))+',' for n in range(0,len(values),16))
text='// Copyright (c) 2026 DAISUKE OBA. SPDX-License-Identifier: MIT\n'
text+='// Generated from round(64*sin(2*pi*i/32)) and round(64*width/z).\n'
text+='// Depths below 32 are rejected. Saturating 256 to 255 at the largest\n// viewport/nearest depth bounds the projection error without a ninth bit.\n'
text+='__prg_rom const s8 w3dfc_sin[32]={\n'+rows([round(64*math.sin(2*math.pi*i/32)) for i in range(32)])+'\n};\n'
for n,width in enumerate([64,96,128]):
    text+=('#if' if n==0 else '#elif')+' WIRE3D_FC_WIDTH == '+str(width)+'\n'
    text+='__prg_rom const u8 w3dfc_recip[256]={\n'+rows([0 if z<32 else min(255,round(64*width/z)) for z in range(256)])+'\n};\n'
    height={64:48,96:64,128:96}[width]
    offsets=[(y//8)*width+y%8 for y in range(height)]
    for name,values in [('row_lo',[v&255 for v in offsets]),('row_hi',[0x68+(v>>8) for v in offsets]),('tile_row',[(y//8)*(width//8) for y in range(height)])]:
        text+='__prg_rom const u8 w3dfc_'+name+'['+str(height)+']={\n'+rows(values)+'\n};\n'
text+='#endif\n'
(ROOT/'publish/github_20260912/kitaqfc/lib/wire3d_tables.h').write_bytes(text.encode('utf-8'))
