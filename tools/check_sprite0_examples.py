"""Prove repeated hits and visible horizontal splits with complete color images."""
from pathlib import Path
import hashlib,json,subprocess
from check_api_tile_examples import read_png
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=SITE/'verification/api-sprite0/example';OUT.mkdir(parents=True,exist_ok=True)
compiler=REPOS/'kitaqfc/kitaqfc.exe';emulator=REPOS/'kurosaki/kurosaki.exe';lib=REPOS/'kitaqfc/lib'
asset=SITE/'samples/sprite0_scene.chr';font=(SITE/'samples/font.chr').read_bytes();data=bytearray(font)
for tile,lo,hi in [(240,255,0),(241,0,255),(242,255,255)]:data[tile*16:tile*16+16]=bytes([lo]*8+[hi]*8)
asset.write_bytes(data)
colors=[(0,0,0),(100,176,255),(181,49,32),(255,254,255)]

def expected_scene(shift):
 pixels={}
 for y in range(48,208):
  if 96<=y<104:
   for x in range(256):pixels[x,y]=colors[3]
  else:
   dx=shift if y>=104 else 0
   for left,color in [(64-dx,colors[1]),(160-dx,colors[2])]:
    for x in range(left,left+32):pixels[x,y]=color
 for tx,ty,label in [(1,1,'SPRITE ZERO / SCROLL SPLIT'),(1,3,'TOP: BLUE 64 / RED 160')]:
  for n,c in enumerate(label):
   for y in range(8):
    for x in range(8):
     bits=((font[ord(c)*16+y]>>(7-x))&1)|(((font[ord(c)*16+8+y]>>(7-x))&1)<<1)
     if bits:pixels[(tx+n)*8+x,ty*8+y]=colors[bits]
 return pixels

records=[]
for mode in ['wait','split','split_alias']:
 for variant,flags in [('default',[]),('unoptimized',['-O0'])]:
  folder=OUT/(mode+'-'+variant);folder.mkdir(exist_ok=True)
  source=SITE/('samples/api-examples/fc/sprite0_'+mode+'.c');rom=folder/'example.nes';image=folder/'screen.png'
  cmd=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper=nrom','--nes-chr='+str(asset),'--no-cache','--no-disasm']+flags
  p=subprocess.run(cmd,capture_output=True,cwd=folder,timeout=90)
  if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-3000:])
  observed=[];states=[]
  for frames in [120,121]:
   statepath=folder/('state-'+str(frames)+'.json');states.append(statepath)
   cmd=[str(emulator),'run',str(rom),'--frames',str(frames),'--snapshot',str(statepath)]
   if frames==120:cmd+=['--png',str(image)]
   p=subprocess.run(cmd,capture_output=True,cwd=folder,timeout=90);assert p.returncode==0
   state=json.loads(statepath.read_text());ppu=state['bus']['ppu']
   observed.append(dict(frames=frames,completed=state['bus']['ram'][0x600],hit_pixels=ppu['sprite0_hit_candidates']))
  actual=[(observed[1]['completed']-observed[0]['completed'])&255,int(80<observed[0]['completed']<120),observed[1]['hit_pixels']-observed[0]['hit_pixels']]
  expected=[1,1,64]
  width,height,channels,rows=read_png(image);assert (width,height)==(256,240)
  pixels=expected_scene(0 if mode=='wait' else 32)
  bad=[(x,y) for y in range(height) for x in range(width) if tuple(rows[y][x*channels:x*channels+3])!=pixels.get((x,y),colors[0])]
  inputs=dependencies(source,lib);inputs['samples/sprite0_scene.chr']=sha(asset);inputs['samples/font.chr']=sha(SITE/'samples/font.chr')
  row=dict(platform='fc',mode=mode+'-'+variant,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=inputs,actual=actual,expected=expected,observations=observed,pixel_mismatches=len(bad),first_mismatches=bad[:12],passed=actual==expected and not bad)
  records.append(row);print(mode,variant,'PASS' if row['passed'] else 'FAIL',actual,observed,'pixels',len(bad),flush=True)
  if row['passed']:
   for path in states:path.unlink()
   cleanup_build_outputs(folder)
  (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=records),indent=2),encoding='utf-8')
raise SystemExit(0 if all(r['passed'] for r in records) else 1)
