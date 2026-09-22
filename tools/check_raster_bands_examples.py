"""Compare band/HUD/window examples against a complete independent tile-map model."""
from pathlib import Path
import hashlib,json,re,subprocess
from check_api_tile_examples import read_png
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs
from api_vram_colors import matches_color
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912';OUT=SITE/'verification/api-raster-bands';OUT.mkdir(parents=True,exist_ok=True)
compiler=REPOS/'kitaqgb/kitaqgb.exe';emulator=REPOS/'kokura/kokura-cli.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec_path=SITE/'tools/api_descriptions/raster_bands_examples.json';specs=json.loads(spec_path.read_text());records=[]
font_text=(SITE/'samples/font_gb.h').read_text();font=[int(v,0) for v in re.findall(r'0x[0-9A-Fa-f]+|\d+',font_text[font_text.index('{')+1:font_text.index('}')])]
def expected_pixel(spec,x,y):
 if spec['group']=='color':return 'blue' if y<66 else 'red' if y<114 else 'green'
 sx=sy=0
 for ly,bx,by in spec['bands']:
  if y>=ly:sx,sy=bx,by
 if spec['window'] and x>=24 and y>=48:return 'blue' if 32<=x<48 and 56<=y<72 else 'white'
 x=(x+sx)%256;y=(y+sy)%256
 if 32<=x<56 and any(top<=y<top+16 for top in [16,80,112]):return 'red'
 if spec['title_y']*8<=y<(spec['title_y']+1)*8 and 8<=x<8+len(spec['title'])*8:
  ch=ord(spec['title'][(x-8)//8]);line=y%8;mask=font[ch*16+line*2]|font[ch*16+line*2+1]
  if mask&(128>>(x%8)):return 'black'
 return 'white'
for spec in specs:
 folder=OUT/spec['group'];folder.mkdir(exist_ok=True);source=SITE/spec['source'];rom=folder/'example.gb'
 cmd=[compiler,source,'-I',compiler.parent/'lib','-I',SITE/'samples','-o',rom,'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=64k','--no-cache','--no-disasm']
 p=subprocess.run(list(map(str,cmd)),capture_output=True,cwd=folder,timeout=120);assert p.returncode==0,(p.stdout+p.stderr)[-2000:]
 for mode in spec['modes']:
  image=folder/(mode+'.png');report=folder/(mode+'.json');cmd=[emulator,rom,'--hardware',mode,'--run-frames','180','--png',image,'--dump-report',report,'--report-sections','meta,watched_memory','--watch-fields','preview','--watch-window','result:50688:4']
  p=subprocess.run(list(map(str,cmd)),capture_output=True,cwd=folder,timeout=120);assert p.returncode==0,p.stderr[-1000:]
  result=json.loads(report.read_text())['watched_memory'][0]['preview_bytes'];w,h,c,pixels=read_png(image);assert (w,h)==(160,144)
  mismatches=[]
  for y in range(h):
   for x in range(w):
    color=expected_pixel(spec,x,y)
    if mode=='dmg' and color!='white':color='black'
    actual=pixels[y][x*c:x*c+3]
    if not matches_color(actual,color):mismatches.append([x,y,color,list(actual)])
  row=dict(platform='gb',group=spec['group'],mode=mode,source=spec['source'],source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=dependencies(source,compiler.parent/'lib'),actual=result,expected=spec['expected'],pixel_mismatches=len(mismatches),first_pixel_mismatches=mismatches[:12],passed=result==spec['expected'] and not mismatches)
  records.append(row);print(spec['group'],mode,'PASS' if row['passed'] else 'FAIL',result,'pixels',len(mismatches),mismatches[:2],flush=True)
  if row['passed']:report.unlink()
  (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),spec_sha256=sha(spec_path),records=records),indent=2),encoding='utf-8')
 if all(r['passed'] for r in records if r['group']==spec['group']):cleanup_build_outputs(folder)
raise SystemExit(0 if all(r['passed'] for r in records) else 1)
