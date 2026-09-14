"""Check rendered sample pixels against the supplied ascii.c glyphs."""
from pathlib import Path
import argparse,json,re
from PIL import Image
S=Path(__file__).resolve().parents[1]
def main():
 # Verification reads the original glyphs without regenerating any source or atlas.
 ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,default=S/'verification/current');args=ap.parse_args();D=args.results.resolve()
 source=(S/'samples/assets/ascii.c').read_text(encoding='utf-8-sig')
 tiles={int(n):bytes(int(v,16) for v in re.findall(r'0x([0-9a-fA-F]{2})',body)) for n,body in re.findall(r'TileLabelTLE(\d+)\[\]\s*=\s*\{([^}]+)\}',source,re.S)}
 assert sorted(tiles)==list(range(92)) and all(len(tile)==16 for tile in tiles.values())
 mapping=json.loads((S/'verification/font_conversion.json').read_text(encoding='utf-8'))['mapped_glyphs']
 masks={r['char']:[bool((tiles[r['source_tile']][y*2] | tiles[r['source_tile']][y*2+1]) & (1<<(7-x))) for y in range(8) for x in range(8)] for r in mapping}
 records=[]
 def check(ident,x,y,text,optional=False):
  p=D/(ident+'.png')
  if optional and not p.exists():return
  if not p.exists():raise FileNotFoundError('Run this sample first: '+str(p))
  im=Image.open(p).convert('RGB');bg=im.getpixel((0,0));errors=[]
  for i,c in enumerate(text):
   actual=[im.getpixel(((x+i)*8+xx,y*8+yy))!=bg for yy in range(8) for xx in range(8)]
   target=masks[c]
   if actual!=target:errors.append({'char_index':i,'expected':c,'different_pixels':sum(a!=b for a,b in zip(actual,target)),'matches':[k for k,v in masks.items() if v==actual]})
  records.append({'id':ident,'tile_x':x,'tile_y':y,'expected_text':text,'status':'passed' if not errors else 'failed','errors':errors})
 manifest=json.loads((S/'samples/manifest.json').read_text(encoding='utf-8'))
 numeric={'hello':'042','arithmetic':'030','control':'042','aggregate':'042','bits_memory':'010','input':'000','fixed':'012','entity':'001','debug':'001','chain':'042','system':'002','scene':'001','camera':'042','rle':'042','board':'042','physics':'042','bank':'042','asset':'042','danmaku':'001','subpixel':'042','cgb_palette':'042','flags':'001','circle':'042','sound':'042','link':'255'}
 for d in manifest:
  name=d['id'][3:]
  if name in numeric:check(d['id'],3,8,numeric[name])
  if name=='vram_queue':check(d['id'],3,8,'4')
 for p in ['gb','fc']:
  # Pressed-input captures are separate interactive tests, not part of the no-input run.
  check(p+'_input_pressed',3,8,'001',optional=True)
  for x,y,t in [(2,5,'ABCDEFGHIJKLMNOP'),(2,6,'QRSTUVWXYZ'),(2,8,'0123456789'),(2,10,'abcdefghijklmnop'),(2,11,'qrstuvwxyz'),(2,13,"!#$%&'()*+,-./"),(2,14,':;<=>?@[]^_`{}~'),(16,13,'"')]:check(p+'_font',x,y,t)
 (D/'visual_checks.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Pixel checks:',len(records),'passed:',sum(r['status']=='passed' for r in records))
 for r in records:
  if r['status']!='passed':print(r)
 if any(r['status']!='passed' for r in records):raise SystemExit(1)
if __name__=='__main__':main()
