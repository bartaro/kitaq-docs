"""Check absolute text placement, decimal fields and frame tiles on DMG/CGB."""
from pathlib import Path
import hashlib, json, re, subprocess
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs

SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists(): REPOS=SITE.parent
OUT=SITE/'verification/api-text-layout'
LIB=REPOS/'kitaqgb/lib'
COMPILER=REPOS/'kitaqgb/kitaqgb.exe'
EMULATOR=REPOS/'kokura/kokura-cli.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FRAME=[[0,0,0,31,16,16,16,16],[0,0,0,240,16,16,16,16],
       [16,16,16,31,0,0,0,0],[16,16,16,240,0,0,0,0],
       [0,0,0,255,0,0,0,0],[16]*8]

def fill(grid,x,y,w,h,tile):
    for row in range(y,y+h):
        for column in range(x,x+w): grid[row*32+column]=tile

def window(grid,x,y,w,h):
    fill(grid,x,y,w,h,0)
    if not w or not h: return
    grid[y*32+x]=1
    if w>1: grid[y*32+x+w-1]=2
    if h>1: grid[(y+h-1)*32+x]=3
    if w>1 and h>1: grid[(y+h-1)*32+x+w-1]=4
    for col in range(x+1,x+w-1):
        grid[y*32+col]=5
        if h>1: grid[(y+h-1)*32+col]=5
    for row in range(y+1,y+h-1):
        grid[row*32+x]=6
        if w>1: grid[row*32+x+w-1]=6

def put(grid,x,y,text):
    grid[y*32+x:y*32+x+len(text)]=list(text.encode('ascii'))

def run(source,folder,mode,expected,address,screenshot=False):
    folder.mkdir(parents=True,exist_ok=True)
    rom=folder/'example.gb';runtime=folder/'runtime.json';picture=folder/'screen.png'
    for p in [rom,runtime,picture]: p.unlink(missing_ok=True)
    command=[str(COMPILER),str(source),'-I',str(LIB),'-I',str(SITE/'samples'),
             '-o',str(rom),'--profile=dev','--rst-disable','--stack-bank=fixed',
             '--cgb=cgb','--cart=mbc5','--romsize=64k','--no-cache','--no-disasm']
    process=subprocess.run(command,cwd=folder,capture_output=True,timeout=90)
    (folder/'build.txt').write_bytes(process.stdout+process.stderr)
    row={'mode':mode,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),
         'build_exit':process.returncode,'passed':False}
    if process.returncode:
        return row
    command=[str(EMULATOR),str(rom),'--hardware',mode,'--run-frames','600','--dump-report',str(runtime)]
    for offset in range(0,len(expected),16):
        command+=['--watch-window',f'bytes{offset}:{address+offset}:{min(16,len(expected)-offset)}']
    if screenshot:command+=['--png',str(picture)]
    else:command+=['--watch-window','done:49536:1']
    process=subprocess.run(command,cwd=folder,capture_output=True,timeout=90)
    (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
    row.update(runtime_exit=process.returncode,rom_sha256=sha(rom))
    if process.returncode: return row
    state=json.loads(runtime.read_text(encoding='utf-8'))
    watches={w['name']:w for w in state['watched_memory']};actual=[]
    for offset in range(0,len(expected),16):
        watch=watches['bytes'+str(offset)]
        assert watch['addr']==address+offset and not watch.get('preview_truncated',False)
        actual+=watch['preview_bytes']
    done=screenshot or watches['done']['preview_bytes']==[165]
    frames=state['meta']['frames_executed']
    row.update(actual=actual,expected=expected,done=done,frames=frames,passed=actual==expected and done and frames==600)
    if screenshot:
        width,height,channels,rows=read_png(picture);assert (width,height)==(160,144)
        font_source=(SITE/'samples/font_gb.h').read_text(encoding='utf-8')
        font=[int(n,0) for n in re.findall(r'0x[0-9a-fA-F]+|\d+',font_source[font_source.index('{')+1:font_source.index('}')])]
        masks=[[font[t*16+y*2]|font[t*16+y*2+1] for y in range(8)] for t in range(128)]
        masks[1:7]=FRAME
        background=rows[-1][:3];pixels=colors=ink_count=0
        for y in range(height):
            for x in range(width):
                tx,ty=x//8,y//8;tile=expected[ty*32+tx]
                ink=bool(masks[tile][y%8]&(1<<(7-x%8)))
                rgb=rows[y][x*channels:x*channels+3]
                pixels+=ink!=(rgb!=background)
                if ink:
                    color='black'
                    if mode=='cgb':
                        if 1<=tx<19 and 2<=ty<7:color='red'
                        elif 11<=tx<16 and 8<=ty<11:color='blue'
                        elif 11<=tx<17 and ty==12:color='green'
                    colors+=not matches_color(rgb,color);ink_count+=1
        row.update(platform='gb',image=picture.relative_to(SITE).as_posix(),image_sha256=sha(picture),
                   pixel_mismatches=pixels,color_mismatches=colors,ink_pixels=ink_count)
        row['passed'] &= pixels==colors==0 and ink_count>0
    if row['passed']:cleanup_build_outputs(folder)
    return row

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    sample=SITE/'samples/api-examples/gb/text_layout.c';grid=[0]*1024
    put(grid,1,0,'TEXT PLACEMENT');window(grid,1,2,18,5);put(grid,2,3,'HELLO!')
    put(grid,2,5,'KEEP ERASE KEEP');fill(grid,7,5,5,1,0)
    for y,label,value in [(8,'U8','255'),(10,'U16','65535'),(12,'S16','-32768'),(14,'OVERWRITE','72345'),(16,'CLEAN','7')]:
        put(grid,1,y,label);put(grid,11,y,value)
    records=[];cases=[]
    for mode in ['dmg','cgb']:
        row=run(sample,OUT/('gb-'+mode),mode,grid,0x9800,True);records.append(row)
        print('sample',mode,'PASS' if row['passed'] else 'FAIL',flush=True)
    values16=sorted(set(list(range(21))+[n+d for n in [100,256,1000,10000,32768,65534] for d in [-1,0,1]]))
    signed=sorted(set(list(range(-20,21))+[-32768,-32767,-10000,-1000,-100,-99,99,100,1000,10000,32766,32767]))
    for name,values in [('text_print_u8',list(range(256))),('text_print_u16',values16),('text_print_s16',signed)]:
        expected=[]
        for value in values:expected+=list(str(value).encode('ascii'))+[46]*(8-len(str(value)))
        src='''#pragma bank 0
#include "text.c"
__location(0xFF40) u8 lcd;
__location(0xC180) u8 done;
__location(0xC200) u8 observed[%d];
const u16 values[%d]={%s};
void main(){u16 i;u8 j;__wait_vblank();lcd=0;done=0;
for(i=0;i<%d;i++){
__vram_fill(0x9821,46,8);
%s(1,1,(%s)values[i]);
for(j=0;j<8;j++){observed[i*8+j]=*((u8*)(0x9821+j));}
}
done=165;while(1){}
}
'''%(len(expected),len(values),','.join(str(v&65535) for v in values),len(values),name,'s16' if name.endswith('s16') else ('u8' if name.endswith('u8') else 'u16'))
        for mode in ['dmg','cgb']:
            folder=OUT/'state'/(name+'-'+mode);folder.mkdir(parents=True,exist_ok=True)
            source=folder/'case.c';source.write_text(src,encoding='utf-8')
            row=run(source,folder,mode,expected,0xC200);row.update(name=name,values=values);cases.append(row)
            print(name,mode,'PASS' if row['passed'] else 'FAIL',flush=True)
    grid=[46]*1024
    layouts=[(1,1,6,4),(20,1,1,1),(22,1,2,2),(25,1,0,3),(25,5,3,0),(20,8,1,4),(23,8,4,1),(30,30,2,2)]
    for dims in layouts:window(grid,*dims)
    put(grid,10,1,'A\nB');window(grid,2,10,6,4);put(grid,3,11,'Q');put(grid,10,10,'OUT');fill(grid,12,12,2,2,0)
    calls='\n'.join('text_window(%s);'%','.join(map(str,d)) for d in layouts)
    src='''#pragma bank 0
#include "text.c"
__location(0xFF40) u8 lcd;
__location(0xC180) u8 done;
const u8 raw[4]={65,10,66,0};
void main(){__wait_vblank();lcd=0;done=0;__vram_fill(0x9800,46,1024);
'''+calls+'''
text_print_xy(10,1,raw);text_window(2,10,6,4);
text_print_xy(10,10,"OUT");text_clear_rect(12,12,2,2);text_print("Q");
done=165;while(1){}
}
'''
    for mode in ['dmg','cgb']:
        folder=OUT/'state'/('layout-'+mode);folder.mkdir(parents=True,exist_ok=True)
        source=folder/'case.c';source.write_text(src,encoding='utf-8')
        row=run(source,folder,mode,grid,0x9800);row.update(name='layout',layouts=layouts);cases.append(row)
        print('layout',mode,'PASS' if row['passed'] else 'FAIL',flush=True)
    report={'records':records,'cases':cases,'compiler_sha256':sha(COMPILER),'emulator_sha256':sha(EMULATOR),
            'script_sha256':sha(Path(__file__)),
            'source_sha256':{p.relative_to(REPOS).as_posix():sha(p) for p in [LIB/'rpg.h',LIB/'text.c']},
            'support_sha256':{('samples/'+n):sha(SITE/'samples'/n) for n in ['gb_common.h','gb_tile_example.h','font_gb.h','vram_example_colors.h']}}
    (OUT/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    raise SystemExit(0 if all(r['passed'] for r in records+cases) else 1)

if __name__=='__main__':main()
