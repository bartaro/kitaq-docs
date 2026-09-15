"""Check actual macro, C runtime and rotating-pool OAM library examples."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from check_api_tile_examples import read_png
from check_entity_callbacks import check_pixels
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
p=argparse.ArgumentParser();p.add_argument('--emulator',type=Path,default=REPOS/'kurosaki/kurosaki.exe');args=p.parse_args()
emulator=args.emulator.resolve(strict=True);compiler=REPOS/'kitaqfc/kitaqfc.exe';out=SITE/'verification/api-oam-library';out.mkdir(parents=True,exist_ok=True)
patterns=json.loads((SITE/'samples/sprite_example_shapes.json').read_text(encoding='utf-8'))['patterns']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for mode,filename,page in [('aliases','oam_aliases.c',2),('c-runtime','oam_c_helpers.c',4),('fair-pool','oam_fair.c',2)]:
 folder=out/mode;folder.mkdir(exist_ok=True);source=SITE/'samples/api-examples/fc'/filename;rom=folder/'example.nes';image=folder/'screen.png';runtime=folder/'runtime.json';snapshot=folder/'snapshot.json'
 command=[str(compiler),str(source),'-I',str(REPOS/'kitaqfc/lib'),'-I',str(SITE/'samples'),'--nes-chr='+str(SITE/'samples/sprite_example.chr'),'--no-cache','--no-disasm','-o',str(rom)]
 r=subprocess.run(command,cwd=folder,capture_output=True,timeout=90);(folder/'build.txt').write_bytes(r.stdout+r.stderr)
 supports=['samples/fc_common.h','samples/sprite_example.chr','samples/sprite_example_shapes.json']+(['samples/fc_oam_alias_example.h'] if mode=='aliases' else [])
 libraries=['intrinsics.h']+(['nes_game.h'] if mode=='aliases' else ['runtime.c','runtime.h','metasprite.c'] if mode=='c-runtime' else ['oam_fair.h','oam_fair_impl.h'])
 row=dict(platform='fc',mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),support_sha256={p:sha(SITE/p) for p in supports},library_sha256={p:sha(REPOS/'kitaqfc/lib'/p) for p in libraries},compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),build_command=command,build_exit=r.returncode,passed=False)
 if r.returncode==0:
  command=[str(emulator),'run',str(rom),'--frames','240','--png',str(image),'--snapshot',str(snapshot),'--json',str(runtime)]
  r=subprocess.run(command,cwd=folder,capture_output=True,timeout=90);(folder/'runtime.txt').write_bytes(r.stdout+r.stderr);row.update(run_exit=r.returncode,run_command=command,rom_sha256=sha(rom))
  if r.returncode==0:
   state=json.loads(snapshot.read_text(encoding='utf-8'));frames=json.loads(runtime.read_text(encoding='utf-8'))['frames']
   labels=[(1,0,'FC OAM EXAMPLE'),(24,0,'NEXT'),(29,0,'07'),(1,2,'SET'),(1,4,'MOVE'),(1,6,'TILE'),(1,8,'ATTR'),(1,10,'HIDE'),(1,12,'META'),(1,14,'CLEAR'),(1,16,'TRANSFER')]
   if mode=='c-runtime':labels=[(1,0,'C OAM HELPERS'),(24,0,'NEXT'),(29,0,'08'),(1,4,'PAIR'),(1,8,'HIDE RANGE'),(1,12,'PAGE 04')]
   if mode=='fair-pool':labels=[(1,0,'FAIR OAM'),(1,4,'KEEP FIRST'),(1,8,'CENTERS'),(1,12,'PHASE 13'),(1,14,'DRAWN 03'),(1,16,'BYTES 16')]
   text_errors=check_pixels(image,labels,'fc');w,h,c,rows=read_png(image);assert (w,h)==(256,240)
   expected={(x,y):0 for y in range(8,144) for x in range(128,192)}
   def draw(x,y,tile,fx=False,fy=False):
    for dy in range(8):
     for dx in range(8):
      value=int(patterns[tile][7-dy if fy else dy][7-dx if fx else dx])
      if value:expected[x+dx,y+dy]=value
   if mode=='aliases':
    draw(144,16,0);draw(144,32,0);draw(144,48,1);draw(144,64,0,True,True)
    draw(136,96,0);draw(144,96,0,True);draw(144,128,0)
   elif mode=='c-runtime':
    draw(144,32,0);draw(152,32,0,True);draw(144,96,1)
   else:
    draw(144,32,1);draw(144,64,0);draw(160,64,0);draw(176,64,0)
   errors=[]
   for (x,y),value in expected.items():
    rgb=list(rows[y][x*c:x*c+3]);color=['black','red','green','blue'][value]
    if not matches_color(rgb,color):errors.append({'x':x,'y':y,'expected':color,'actual':rgb})
   ram=state['bus']['ram'];oam=state['bus']['ppu']['oam'];source_bytes=ram[page*256:(page+1)*256]
   row.update(frames=frames,image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),runtime_sha256=sha(runtime),expected_labels=labels,label_pixel_mismatches=text_errors,sprite_pixels_checked=len(expected),sprite_pixel_mismatches=len(errors),first_mismatches=errors[:20],oam=oam,source_page=page,source_bytes=source_bytes,oam_matches_source=oam==source_bytes,shadow_marker_tile=ram[0x221] if mode=='c-runtime' else None,hardware_marker_tile=oam[33] if mode=='c-runtime' else None,passed=frames==240 and text_errors==0 and not errors and oam==source_bytes and (mode!='c-runtime' or (ram[0x221]==128 and oam[33]==129)))
  if row['passed']:cleanup_build_outputs(folder)
 records.append(row);(out/'results.json').write_text(json.dumps({'records':records,'scope':'Aliases and C helpers use independently compiled programs; rotating-pool sprites appear at their specified center positions. Actual colored pixels, preserved source pages and OAM bytes are checked. Physical hardware is untested.'},indent=2),encoding='utf-8')
 print(mode,'PASS' if row['passed'] else 'FAIL',row.get('label_pixel_mismatches'),row.get('sprite_pixel_mismatches'),flush=True)
raise SystemExit(0 if all(r['passed'] for r in records) else 1)
