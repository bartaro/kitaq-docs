"""Use the author-supplied ascii.c, preserving every 2bpp glyph bit."""
from pathlib import Path
import re,hashlib,json,shutil
from PIL import Image,ImageDraw
S=Path(__file__).resolve().parents[1]
ROOT=S.parent
def load():
 src=ROOT/'kitaqgb/examples/assets/ascii.c'
 packaged=S/'samples/assets/ascii.c'
 packaged.parent.mkdir(exist_ok=True,parents=True)
 if src.exists():shutil.copyfile(src,packaged)
 raw=packaged.read_bytes();text=raw.decode('utf-8-sig')
 tiles={int(n):bytes(int(v,16) for v in re.findall(r'0x([0-9a-fA-F]+)',body)) for n,body in re.findall(r'TileLabelTLE(\d+)\[\]\s*=\s*\{([^}]+)\}',text,re.S)}
 assert len(tiles)==92 and all(len(t)==16 for t in tiles.values())
 atlas=Image.new('RGB',(12*64,8*88),'#ffffff');draw=ImageDraw.Draw(atlas)
 for n,t in tiles.items():
  x=(n%12)*64;y=(n//12)*88
  draw.text((x+3,y+2),str(n),fill='black')
  for yy in range(8):
   for xx in range(8):
    value=((t[2*yy]>>(7-xx))&1)|(((t[2*yy+1]>>(7-xx))&1)<<1)
    draw.rectangle((x+8+xx*6,y+21+yy*6,x+13+xx*6,y+26+yy*6),fill=(255-value*85,)*3)
 atlas.save(S/'verification/font_source_atlas.png')
 return tiles,hashlib.sha256(raw).hexdigest()
def convert():
 tiles,sha=load()
 chars={c:i for i,c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz')}
 punctuation='!"#$%&\'()*+,-./:;<=>?@[]^_`{}~'
 # Tail punctuation mapping is verified against the generated source atlas.
 chars.update({c:62+i for i,c in enumerate(punctuation)})
 gb=bytearray(128*16);fc=bytearray(8192)
 mapping=[]
 for c,n in chars.items():
  t=tiles[n];off=ord(c)*16;gb[off:off+16]=t
  fc[off:off+16]=t[0::2]+t[1::2]
  assert fc[off:off+8]==gb[off:off+16:2] and fc[off+8:off+16]==gb[off+1:off+16:2]
  mapping.append({'char':c,'ascii':ord(c),'source_tile':n})
 report={'source':'samples/assets/ascii.c','source_sha256':sha,'source_tiles':92,'gb_bytes':len(gb),'nes_chr_bytes':len(fc),'conversion':'GB interleaved planes to NES plane-0 followed by plane-1; unchanged pixel indices','mapped_glyphs':mapping,'gb_sha256':hashlib.sha256(gb).hexdigest(),'nes_sha256':hashlib.sha256(fc).hexdigest()}
 (S/'verification/font_conversion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 return gb,fc
if __name__=='__main__':load()
