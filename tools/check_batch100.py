"""Build and execute the 100-API batch; compare captured RAM with host expectations."""
from pathlib import Path
import json,hashlib,subprocess,argparse
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs
from check_text_layout import FRAME,window,put
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
import re
SITE=Path(__file__).resolve().parents[1];ROOT=SITE.parents[1];REPOS=ROOT/'publish/github_20260912'
OUT=SITE/'verification/api-batch100';AUTHOR=SITE/'tools/api_descriptions'
if not REPOS.exists():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--case');opt=ap.parse_args();records=[]
 for spec in json.loads((AUTHOR/'batch100_examples.json').read_text(encoding='utf-8')):
  platform=spec['platform'];group=spec['group']
  if opt.case and opt.case!=platform+'-'+group:continue
  source=SITE/spec['source'];lib=REPOS/('kitaq'+platform)/'lib';compiler=lib.parent/('kitaq'+platform+'.exe')
  emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
  folder=OUT/(platform+'-'+group);folder.mkdir(parents=True,exist_ok=True)
  rom=folder/('example.gb' if platform=='gb' else 'example.nes');rom.unlink(missing_ok=True)
  command=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--no-cache','--no-disasm']
  if platform=='gb':command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=64k']
  else:
   if group=='services':command.insert(1,str(lib/'runtime.c'))
   command+=['--mapper=nrom','--nes-chr='+str(SITE/'samples/font.chr')]
  built=subprocess.run(command,cwd=folder,capture_output=True,timeout=120);(folder/'build.txt').write_bytes(built.stdout+built.stderr)
  if built.returncode:
   print(platform,group,'BUILD FAIL',flush=True);records.append({'platform':platform,'group':group,'passed':False,'build_exit':built.returncode});continue
  cleanup_build_outputs(folder)
  for mode in (['dmg','cgb'] if platform=='gb' else ['nrom']):
   sub=folder/mode;sub.mkdir(exist_ok=True);statepath=sub/'runtime.json';png=sub/'screen.png'
   for path in [statepath,png]:path.unlink(missing_ok=True)
   if platform=='gb':
    command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','180','--dump-report',str(statepath),'--report-sections','meta,cpu,watched_memory','--watch-fields','preview','--png',str(png)]
    if spec.get('input_sequence'):command+=['--input-seq',spec['input_sequence']]
    for offset in range(0,160,16):command+=['--watch-window',f'result{offset}:{0xC600+offset}:16']
    if group.startswith('menu_'):
     for offset in range(0,1024,16):command+=['--watch-window',f'map{offset}:{0x9800+offset}:16']
   else:command=[str(emulator),'run',str(rom),'--frames','180','--headless','--snapshot',str(statepath),'--png',str(png)]
   result=subprocess.run(command,cwd=sub,capture_output=True,timeout=120);(sub/'runtime.txt').write_bytes(result.stdout+result.stderr)
   row={'platform':platform,'group':group,'mode':mode,'source':spec['source'],'source_sha256':sha(source),'compiler_sha256':sha(compiler),'emulator_sha256':sha(emulator),'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),'passed':False}
   if result.returncode==0 and statepath.exists():
    state=json.loads(statepath.read_text(encoding='utf-8'))
    if platform=='gb':
     watches={w['name']:w for w in state['watched_memory']};raw=[]
     for offset in range(0,160,16):raw+=watches['result'+str(offset)]['preview_bytes']
    else:raw=state['bus']['ram'][0x600:0x6A0]
    actual=[raw[i]+raw[i+1]*256 for i in range(0,160,2)]
    expected=spec['expected']+[0]*(79-len(spec['expected']))+[0xA55A]
    labels=[]
    for y,label,index in spec['labels']:
     labels.append((1,y,label))
     if index is not None:
      value=expected[index]
      if spec.get('signed_display') and value>=32768:
       labels.append((12,y,'-'));value=65536-value
      labels.append((13,y,str(value).zfill(5)))
    errors=check_pixels(png,labels,platform)
    if group=='geometry':
     geometry_colors=0;w,h,channels,pixels=read_png(png)
     for gy in range(11):
      line=''
      for gx in range(15):
       inside_a=1<=gx<9 and 1<=gy<7;inside_b=5<=gx<13 and 4<=gy<10
       line+='O' if inside_a and inside_b else 'A' if inside_a else 'B' if inside_b else ' '
      errors+=check_pixels(png,[(1,2+gy,line)],platform)
      if mode!='dmg':
       background=pixels[-1][:3]
       for gx,tile in enumerate(line):
        if tile==' ':continue
        color={'A':'red','B':'blue','O':'green'}[tile] if platform=='gb' else 'blue'
        for py in range(8):
         for px in range(8):
          rgb=pixels[(2+gy)*8+py][((1+gx)*8+px)*channels:((1+gx)*8+px)*channels+3]
          if rgb!=background:geometry_colors+=not matches_color(rgb,color)
     errors+=geometry_colors
    row.update(actual=actual,expected=expected,expected_labels=labels,pixel_mismatches=errors,image=png.relative_to(SITE).as_posix(),image_sha256=sha(png),passed=actual==expected and errors==0)
    if group.startswith('menu_'):
     grid=[0]*1024
     if group=='menu_yesno':
      window(grid,6,10,8,4);put(grid,8,11,'YES');put(grid,8,12,'NO');grid[12*32+7]=7
     else:
      top=1 if group=='menu_inventory' else 2
      window(grid,1,top,18,5)
      for n,label in enumerate(['SWORD','SHIELD','POTION']):put(grid,3,top+1+n,label)
      grid[(top+2)*32+2]=7
      if group=='menu_inventory':
       for n,qty in enumerate(['07','42','99']):put(grid,15,2+n,qty)
     for x,y,label in labels:put(grid,x,y,label)
     captured=[]
     for offset in range(0,1024,16):captured+=watches['map'+str(offset)]['preview_bytes']
     font_text=(SITE/'samples/font_gb.h').read_text(encoding='utf-8')
     font=[int(n,0) for n in re.findall(r'0x[0-9a-fA-F]+|\d+',font_text[font_text.index('{')+1:font_text.index('}')])]
     masks=[[font[t*16+y*2]|font[t*16+y*2+1] for y in range(8)] for t in range(128)]
     masks[1:9]=FRAME+[[0,16,24,28,24,16,0,0],[0,0,0,0,254,124,56,16]]
     w,h,channels,pixels=read_png(png);background=pixels[-1][:3];geometry=colors=0
     for y in range(h):
      for x in range(w):
       tx,ty=x//8,y//8;ink=bool(masks[grid[ty*32+tx]][y%8]&(1<<(7-x%8)));rgb=pixels[y][x*channels:x*channels+3]
       geometry+=ink!=(rgb!=background)
       if ink:
        color='green' if mode=='cgb' and 1<=tx<19 and 1<=ty<16 else 'black'
        colors+=not matches_color(rgb,color)
     row.update(tilemap_mismatches=sum(a!=b for a,b in zip(grid,captured)),geometry_pixel_mismatches=geometry,color_mismatches=colors)
     row['passed'] &= captured==grid and geometry==colors==0
     if not row['passed']:print('Menu map/pixels/colors',row['tilemap_mismatches'],geometry,colors,flush=True)
    print(platform,group,mode,'PASS' if row['passed'] else 'FAIL','pixels',errors,'RAM',[(i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b][:12],flush=True)
   else:print(platform,group,mode,'RUN FAIL',result.returncode,flush=True)
   records.append(row)
  (OUT/'partial-results.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
 target=OUT/((opt.case+'-results.json') if opt.case else 'results.json')
 target.write_text(json.dumps({'records':records,'checker_sha256':sha(Path(__file__))},indent=2),encoding='utf-8')
 if not all(row['passed'] for row in records):raise SystemExit(1)
if __name__=='__main__':main()
