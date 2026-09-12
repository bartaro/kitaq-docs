"""Check rendered sample pixels against the supplied ascii.c glyphs."""
from pathlib import Path
import json,re
from PIL import Image
from font_asset import load
S=Path(__file__).resolve().parents[1];D=S/'verification'
def main():
 tiles,_=load();mapping=json.loads((D/'font_conversion.json').read_text(encoding='utf-8'))['mapped_glyphs']
 masks={r['char']:[bool((tiles[r['source_tile']][y*2] | tiles[r['source_tile']][y*2+1]) & (1<<(7-x))) for y in range(8) for x in range(8)] for r in mapping}
 records=[]
 def check(ident,x,y,text):
  p=D/(ident+'.png')
  if not p.exists():return
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
  check(p+'_input_pressed',3,8,'001')
  for x,y,t in [(2,5,'ABCDEFGHIJKLMNOP'),(2,6,'QRSTUVWXYZ'),(2,8,'0123456789'),(2,10,'abcdefghijklmnop'),(2,11,'qrstuvwxyz'),(2,13,"!#$%&'()*+,-./"),(2,14,':;<=>?@[]^_`{}~'),(16,13,'"')]:check(p+'_font',x,y,t)
 (D/'visual_checks.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Pixel checks:',len(records),'passed:',sum(r['status']=='passed' for r in records))
 for r in records:
  if r['status']!='passed':print(r)
if __name__=='__main__':main()
