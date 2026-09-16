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
OUT=SITE/'verification/api-batch300';AUTHOR=SITE/'tools/api_descriptions'
if not REPOS.exists():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def dependencies(source,lib):
    """Fingerprint direct and transitive quoted includes, including drawing support."""
    pending=[source];seen={}
    while pending:
        path=pending.pop().resolve()
        if path in seen:continue
        seen[path]=sha(path)
        for name in re.findall(r'^\s*#include\s+"([^"]+)"',path.read_text(encoding='utf-8'),re.M):
            found=next((p for p in [path.parent/name,lib/name,SITE/'samples'/name] if p.is_file()),None)
            if found is None:raise ValueError('Missing included source: '+name)
            pending.append(found)
    return {str(p.relative_to(SITE) if p.is_relative_to(SITE) else p.relative_to(REPOS)).replace('\\','/'):h for p,h in seen.items()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--case');opt=ap.parse_args();records=[]
 for spec in json.loads((AUTHOR/'batch300_examples.json').read_text(encoding='utf-8')):
  platform=spec['platform'];group=spec['group']
  if opt.case and opt.case!=platform+'-'+group:continue
  source=SITE/spec['source'];lib=REPOS/('kitaq'+platform)/'lib';compiler=lib.parent/('kitaq'+platform+'.exe')
  emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
  folder=OUT/(platform+'-'+group);folder.mkdir(parents=True,exist_ok=True)
  rom=folder/('example.gb' if platform=='gb' else 'example.nes');rom.unlink(missing_ok=True)
  command=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--no-cache','--no-disasm']
  if platform=='gb':command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=64k','--ramsize='+spec.get('ramsize','none')]
  else:
   if spec.get('runtime'):command.insert(1,str(lib/'runtime.c'))
   command+=['--mapper=nrom','--nes-chr='+str(SITE/spec.get('chr','samples/font.chr'))]
   if spec.get('mirroring'):command+=['--mirroring='+spec['mirroring']]
  built=subprocess.run(command,cwd=folder,capture_output=True,timeout=120);(folder/'build.txt').write_bytes(built.stdout+built.stderr)
  if built.returncode:
   print(platform,group,'BUILD FAIL',flush=True);records.append({'platform':platform,'group':group,'passed':False,'build_exit':built.returncode});continue
  cleanup_build_outputs(folder)
  for mode in spec.get('modes',(['dmg','cgb'] if platform=='gb' else ['nrom'])):
   sub=folder/mode;sub.mkdir(exist_ok=True);statepath=sub/'runtime.json';png=sub/'screen.png'
   for path in [statepath,png]:path.unlink(missing_ok=True)
   if platform=='gb':
    command=[str(emulator),str(rom),'--hardware',mode,'--run-frames',str(spec.get('frames',300)),'--dump-report',str(statepath),'--report-sections','meta,cpu,watched_memory','--watch-fields','preview','--png',str(png)]
    if spec.get('input_sequence'):command+=['--input-seq',spec['input_sequence']]
    for offset in range(0,160,16):command+=['--watch-window',f'result{offset}:{spec.get("result_address",0xC600)+offset}:16']
    if group.startswith('menu_'):
     for offset in range(0,1024,16):command+=['--watch-window',f'map{offset}:{0x9800+offset}:16']
   else:command=[str(emulator),'run',str(rom),'--frames',str(spec.get('frames',300)),'--headless','--snapshot',str(statepath),'--png',str(png)]
   result=subprocess.run(command,cwd=sub,capture_output=True,timeout=120);(sub/'runtime.txt').write_bytes(result.stdout+result.stderr)
   row={'platform':platform,'group':group,'mode':mode,'source':spec['source'],'source_sha256':sha(source),'compiler_sha256':sha(compiler),'emulator_sha256':sha(emulator),'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),'passed':False}
   inputs=dependencies(source,lib)
   if spec.get('runtime'):inputs.update(dependencies(lib/'runtime.c',lib))
   if platform=='fc':inputs[spec.get('chr','samples/font.chr')]=sha(SITE/spec.get('chr','samples/font.chr'))
   row['input_sha256']=inputs
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
    if spec.get('grid_check'):
     # Independent breadth-first model: costs and a decreasing-distance route,
     # followed by a whole-screen glyph/color comparison including blank cells.
     from collections import deque
     walls={(2,1),(2,2),(2,3)};dist={(0,2):0};pending=deque([(0,2)])
     while pending:
      xx,yy=pending.popleft()
      for nx,ny in [(xx,yy-1),(xx+1,yy),(xx,yy+1),(xx-1,yy)]:
       if 0<=nx<6 and 0<=ny<5 and (nx,ny) not in walls and (nx,ny) not in dist:
        dist[nx,ny]=dist[xx,yy]+1;pending.append((nx,ny))
     grid=[0]*1024;attrs=[0]*1024
     for xx,yy,label in labels:put(grid,xx,yy,label)
     for xx,yy in walls:
      for shift in [1,11]:grid[(yy+3)*32+xx+shift]=126;attrs[(yy+3)*32+xx+shift]=1
     for (xx,yy),cost in dist.items():
      if cost<=3:grid[(yy+3)*32+xx+1]=48+cost;attrs[(yy+3)*32+xx+1]=2
     xx,yy=5,2
     while (xx,yy)!=(0,2):
      grid[(yy+3)*32+xx+11]=42;attrs[(yy+3)*32+xx+11]=3
      xx,yy=next((nx,ny) for nx,ny in [(xx,yy-1),(xx+1,yy),(xx,yy+1),(xx-1,yy)] if dist.get((nx,ny))==dist[xx,yy]-1)
     grid[5*32+11]=83;grid[5*32+16]=71
     ft=(SITE/'samples/font_gb.h').read_text(encoding='utf-8');font=[int(n,0) for n in re.findall(r'0x[0-9a-fA-F]+|\d+',ft[ft.index('{')+1:ft.index('}')])]
     masks=[[font[t*16+y*2]|font[t*16+y*2+1] for y in range(8)] for t in range(128)];masks[126]=[255]*8
     w,h,ch,pixels=read_png(png);geometry=colors=0
     for py in range(h):
      for px in range(w):
       cell=(py//8)*32+px//8;ink=bool(masks[grid[cell]][py%8]&(128>>(px%8)));rgb=pixels[py][px*ch:px*ch+3]
       color=['black','red','blue','green'][attrs[cell]] if mode=='cgb' else 'black'
       geometry+=ink!=(not matches_color(rgb,'white'));colors+=not matches_color(rgb,color if ink else 'white')
     errors+=geometry+colors;row.update(geometry_pixel_mismatches=geometry,color_mismatches=colors,pixels_checked=w*h)
    if spec.get('visual'):
     labels=spec.get('visual_labels',[]);errors=check_pixels(png,labels,platform)
     w,h,channels,pixels=read_png(png);geometry=colors=0
     for y in range(h):
      for x in range(w):
       if any(ly*8<=y<(ly+1)*8 and lx*8<=x<(lx+len(text))*8 for lx,ly,text in labels):continue
       color=next((c for rx,ry,rw,rh,c in reversed(spec['rectangles']) if rx<=x<rx+rw and ry<=y<ry+rh),None)
       bg='white' if platform=='gb' else 'black'
       expected_color=('black' if mode=='dmg' else color) if color else bg
       rgb=pixels[y][x*channels:x*channels+3]
       geometry+=bool(color)!=(not matches_color(rgb,bg))
       colors+=not matches_color(rgb,expected_color)
     errors+=geometry+colors
     row.update(geometry_pixel_mismatches=geometry,color_mismatches=colors,pixels_checked=w*h)
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
