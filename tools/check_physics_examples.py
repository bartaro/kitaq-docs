"""Execute physics samples and compare RAM plus every pixel of two drawing panels."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from check_batch200 import dependencies
from check_entity_callbacks import check_pixels
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-physics';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def expected_panels(shapes):
    panels=[[[0]*64 for _ in range(64)] for _ in range(2)]
    def put(p,x,y,c):
        if 0<=x<64 and 0<=y<64:panels[p][y][x]=c
    for shape in shapes:
        kind,p,x,y,*tail=shape
        if kind=='rect':
            w,h,c,outline=tail
            for dy in range(h):
                for dx in range(w):
                    if not outline or dx in [0,w-1] or dy in [0,h-1]:put(p,x+dx,y+dy,c)
        elif kind=='circle':
            radius,c=tail
            for dy in range(-radius,radius+1):
                for dx in range(-radius,radius+1):
                    if dx*dx+dy*dy<=radius*radius:put(p,x+dx,y+dy,c)
        elif kind=='vector':
            vx,vy,c=tail;n=max(abs(vx),abs(vy))
            for k in range(n+1):put(p,x+int(vx*k/max(n,1)),y+int(vy*k/max(n,1)),c)
        else:raise ValueError(kind)
    return panels

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case');options=parser.parse_args();records=[]
    for spec in json.loads((SITE/'tools/api_descriptions/physics_examples.json').read_text(encoding='utf-8')):
        group=spec['group']
        if options.case and group!=options.case:continue
        folder=OUT/group;folder.mkdir(parents=True,exist_ok=True)
        source=SITE/spec['source'];rom=folder/'example.gb';compiler=REPOS/'kitaqgb/kitaqgb.exe';emulator=REPOS/'kokura/kokura-cli.exe';lib=compiler.parent/'lib'
        cmd=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--no-cache','--no-disasm','--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=128k']
        build=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120);(folder/'build.txt').write_bytes(build.stdout+build.stderr)
        if build.returncode:raise RuntimeError('Build failed: '+group+' '+build.stderr.decode('utf-8',errors='replace')[-1000:])
        inputs=dependencies(source,lib);panels=expected_panels(spec['shapes'])
        for mode in ['dmg','cgb']:
            sub=folder/mode;sub.mkdir(exist_ok=True);report=sub/'runtime.json';image=sub/'screen.png'
            cmd=[str(emulator),str(rom),'--hardware',mode,'--run-frames','240','--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview','--png',str(image)]
            for offset in range(0,160,16):cmd+=['--watch-window',f'r{offset}:{0xC600+offset}:16']
            run=subprocess.run(cmd,cwd=sub,capture_output=True,timeout=120);assert run.returncode==0
            state=json.loads(report.read_text(encoding='utf-8'));watches={w['name']:w['preview_bytes'] for w in state['watched_memory']}
            raw=sum([watches['r'+str(i)] for i in range(0,160,16)],[]);actual=[raw[i]+256*raw[i+1] for i in range(0,160,2)]
            want=spec['expected']+[0]*(79-len(spec['expected']))+[0xA55A]
            labels=check_pixels(image,spec['labels'],'gb');w,h,c,rows=read_png(image);mismatches=[]
            for y in range(h):
                for x in range(w):
                    if any(ly*8<=y<(ly+1)*8 and lx*8<=x<(lx+len(text))*8 for lx,ly,text in spec['labels']):continue
                    color=0
                    for p,origin in enumerate([8,88]):
                        if origin<=x<origin+64 and 48<=y<112:color=panels[p][y-48][x-origin]
                    expected='white' if color==0 else 'black' if mode=='dmg' else ['white','red','blue','green'][color]
                    if not matches_color(rows[y][x*c:x*c+3],expected):mismatches.append([x,y,expected])
            row=dict(platform='gb',group=group,mode=mode,source=spec['source'],source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=inputs,actual=actual,expected=want,frames=state['meta']['frames_executed'],label_pixel_mismatches=labels,pixel_mismatches=len(mismatches),first_pixel_mismatches=mismatches[:12])
            row['passed']=actual==want and labels==0 and not mismatches and row['frames']==240;records.append(row)
            print(group,mode,'PASS' if row['passed'] else 'FAIL','RAM',[(i,a,b) for i,(a,b) in enumerate(zip(actual,want)) if a!=b][:12],'pixels',len(mismatches),'labels',labels,flush=True)
        cleanup_build_outputs(folder)
        (OUT/'partial_results.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    target=OUT/((options.case+'-results.json') if options.case else 'results.json')
    target.write_text(json.dumps({'records':records,'script_sha256':sha(Path(__file__))},indent=2),encoding='utf-8')
    raise SystemExit(0 if records and all(r['passed'] for r in records) else 1)
if __name__=='__main__':main()
