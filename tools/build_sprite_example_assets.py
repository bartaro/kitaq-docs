"""Encode original asymmetric sprite patterns in GB and FC tile formats."""
from pathlib import Path
import json
SITE=Path(__file__).resolve().parents[1]
patterns=[['00001000','00001100','22221310','22221331','22221310','00001100','00001000','00000000'],
          ['22222222']*8]
gb=[];fc=[]
for rows in patterns:
    low=[sum((int(v)&1)<<(7-x) for x,v in enumerate(row)) for row in rows]
    high=[sum(((int(v)>>1)&1)<<(7-x) for x,v in enumerate(row)) for row in rows]
    gb.extend(v for pair in zip(low,high) for v in pair);fc.extend(low+high)
header='// Original sample artwork: right arrow and solid square. Values 1/2/3 select red/green/blue.\n'
header+='__prg_rom u8 sprite_example_tiles[32] = {'+','.join('0x%02X'%v for v in gb)+'};\n'
(SITE/'samples/sprite_example_tiles.h').write_text(header,encoding='ascii')
chr_data=bytearray((SITE/'samples/font.chr').read_bytes());chr_data[128*16:130*16]=bytes(fc)
(SITE/'samples/sprite_example.chr').write_bytes(chr_data)
(SITE/'samples/sprite_example_shapes.json').write_text(json.dumps({'tile_ids':[128,129],'patterns':patterns,
    'palette':['transparent','red','green','blue'],'source':'Original example artwork; font from samples/font.chr.'},indent=2),encoding='utf-8')
print('Original arrow and square encoded for GB and FC.')
