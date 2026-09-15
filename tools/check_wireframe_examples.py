"""Build wireframe examples and compare full emulator frames with geometric expectations."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-wireframe';OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def line_points(ax,ay,bx,by):
    """Nearest lattice points along the major axis; exact half ties stay back."""
    dx=abs(bx-ax);dy=abs(by-ay);n=max(dx,dy)
    if not n:return [(ax,ay)]
    sx=1 if bx>=ax else -1;sy=1 if by>=ay else -1
    return [(ax+sx*((i*dx+(n-1)//2)//n),ay+sy*((i*dy+(n-1)//2)//n)) for i in range(n+1)]

def expected_pixels(spec):
    pixels=[[0]*160 for _ in range(144)]
    for primitive in spec['primitives']:
        op=primitive[0];args=primitive[1:]
        if op=='line':
            ax,ay,bx,by,color=args;points=line_points(ax,ay,bx,by)
            if spec.get('connected'):
                # The bridge is on the next minor-axis coordinate and the
                # preceding major-axis coordinate in the DMG rasterizer.
                shallow=abs(bx-ax)>=abs(by-ay)
                points += [(a[0],b[1]) if shallow else (b[0],a[1]) for a,b in zip(points,points[1:]) if a[0]!=b[0] and a[1]!=b[1]]
        elif op=='point':
            x,y,color=args;points=[(x,y)]
        elif op in ['fill','erase']:
            x0,y0,x1,y1=args[:4];color=0 if op=='erase' else args[4]
            points=[(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1)]
        elif op=='erase_triangle':
            ax,ay,bx,by,cx,cy=args;color=0;points=[]
            cross=lambda a,b,p:(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
            for y in range(min(ay,by,cy),max(ay,by,cy)+1):
                for x in range(min(ax,bx,cx),max(ax,bx,cx)+1):
                    sides=[cross(a,b,(x,y)) for a,b in [((ax,ay),(bx,by)),((bx,by),(cx,cy)),((cx,cy),(ax,ay))]]
                    if min(sides)>=0 or max(sides)<=0:points.append((x,y))
        else:raise ValueError('Unknown geometry '+op)
        for x,y in points:
            if not (0<=x<160 and 0<=y<144):raise ValueError('Expected geometry outside screen')
            if op=='line' and spec.get('combine','or')=='or':pixels[y][x]|=color
            else:pixels[y][x]=color
    return pixels

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case');options=parser.parse_args()
    manifest=SITE/'tools/api_descriptions/wireframe_examples.json'
    specs=json.loads(manifest.read_text(encoding='utf-8'));records=[]
    for name,spec in specs.items():
        if options.case and options.case!=name:continue
        source=SITE/spec['source'];lib=REPOS/'kitaqgb/lib';compiler=lib.parent/'kitaqgb.exe';emulator=REPOS/'kokura/kokura-cli.exe'
        folder=OUT/name;folder.mkdir(exist_ok=True);rom=folder/'example.gb'
        library=lib/spec['library'];command=[str(compiler),str(source),str(library),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--profile=dev','--stack-bank=fixed','--rst-disable','--cgb='+spec.get('target','cgb'),'--cart=mbc5','--romsize=256k','--no-cache','--no-disasm']+spec.get('flags',[])
        p=subprocess.run(command,cwd=folder,capture_output=True,timeout=180);(folder/'build.txt').write_bytes(p.stdout+p.stderr)
        if p.returncode:raise RuntimeError('Wireframe sample build failed: '+name)
        inputs=dependencies(source,lib);inputs.update(dependencies(library,lib));want_pixels=expected_pixels(spec)
        for mode in spec['modes']:
            sub=folder/mode;sub.mkdir(exist_ok=True);report=sub/'runtime.json';image=sub/'screen.png'
            command=[str(emulator),str(rom),'--hardware',mode,'--run-frames',str(spec.get('frames',240)),'--png',str(image),'--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview']
            command+=['--watch-window','r0:49424:16'] # C110..C11F: eight words.
            p=subprocess.run(command,cwd=sub,capture_output=True,timeout=180);assert p.returncode==0
            state=json.loads(report.read_text(encoding='utf-8'));watches={w['name']:w['preview_bytes'] for w in state['watched_memory']};raw=watches['r0']
            actual=[raw[i]+256*raw[i+1] for i in range(0,16,2)];expected=[v&65535 for v in spec['expected']]+[0]*(7-len(spec['expected']))+[0xA55A]
            width,height,channels,rows=read_png(image);assert (width,height)==(160,144)
            mismatches=[];colors=spec.get('colors',['black','red','blue','green'])
            for y in range(height):
                for x in range(width):
                    color=colors[want_pixels[y][x]]
                    if not matches_color(rows[y][x*channels:x*channels+3],color):mismatches.append([x,y,color])
            row=dict(platform='gb',group=name,mode=mode,source=spec['source'],source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=inputs,actual=actual,expected=expected,pixel_mismatches=len(mismatches),first_pixel_mismatches=mismatches[:10])
            row['passed']=actual==expected and not mismatches;records.append(row)
            print(name,mode,'PASS' if row['passed'] else 'FAIL','RAM',[(i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b][:5],'pixels',len(mismatches),mismatches[:5],flush=True)
        cleanup_build_outputs(folder)
        (OUT/'partial_results.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    result={'records':records,'script_sha256':sha(Path(__file__)),'manifest_sha256':sha(manifest)}
    (OUT/((options.case+'-results.json') if options.case else 'results.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
    raise SystemExit(0 if records and all(r['passed'] for r in records) else 1)
if __name__=='__main__':main()
