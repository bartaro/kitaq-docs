"""Measure completed raster work between two write stops, excluding video setup."""
from pathlib import Path
import hashlib,json,random,subprocess
from check_api_tile_examples import read_png
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'publish/library_docs_20260914/wire-speed'
REPOS=ROOT/'publish/github_20260912'

def main():
    records=[];rng=random.Random(6510)
    endpoints=[tuple(rng.randrange(n) for n in (128,96,128,96)) for _ in range(32)]
    for profile,height,color in [('dmg',96,3),('dmg',120,3),('cgb',96,1),('cgb',96,2),('cgb',96,3)]:
        api='Wire3DDMG' if profile=='dmg' else 'Wire3DCGB'
        reference_pixels=None
        for version in ['baseline','optimized']:
            folder=OUT/f'lines-{profile}{height}-{color}-{version}';folder.mkdir(exist_ok=True)
            library=(OUT if version=='baseline' else REPOS/'kitaqgb/lib')/f'wire3d_{profile}.c'
            source=folder/'case.c';rom=folder/'case.gb'
            text=f'#pragma bank 0\n#define WIRE3D_DMG_HEIGHT {height}\n#include "wire3d_{profile}.h"\n__location(0xC110) u8 start;\n__location(0xC111) u8 done;\n__location(0xC112) u8 visible;\nvoid main(){{{api}_Init();{api}_BeginFrame();'
            if profile=='cgb':text+=f'{api}_SetLineColor({color});'
            text+='start=1;'
            for x,y,bx,by in endpoints:text+=f'{api}_DrawLine2D({x},{y},{bx},{by});'
            text+=f'done=1;{api}_EndFrame();__wait_vblank();__wait_vblank();visible=1;while(1){{}}}}';source.write_text(text)
            cmd=[str(REPOS/'kitaqgb/kitaqgb.exe'),str(source),str(library),'-I',str(REPOS/'kitaqgb/lib'),'-o',str(rom),'--profile=dev','--stack-bank=fixed','--rst-disable','--cgb=cgb','--cart=mbc5','--romsize=256k','--no-cache','--no-disasm']
            build=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=180);(folder/'build.txt').write_bytes(build.stdout+build.stderr)
            if build.returncode:raise RuntimeError(str(folder)+' build failed')
            times=[]
            for name,addr in [('start','0xC110'),('done','0xC111')]:
                report=folder/(name+'.json')
                cmd=[str(REPOS/'kokura/kokura-cli.exe'),str(rom),'--hardware',profile,'--run-frames','240','--watchpoint',addr,'--watch-window','marks:49424:2','--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview']
                run=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=180);(folder/(name+'.txt')).write_bytes(run.stdout+run.stderr)
                if run.returncode:raise RuntimeError(str(folder)+' run failed')
                data=json.loads(report.read_text());marks=data['watched_memory'][0]['preview_bytes']
                assert marks[0]==1 and (name=='start' or marks[1]==1)
                times.append(data['meta']['observation_cycle'])
            image=folder/'screen.png';report=folder/'visible.json'
            cmd=[str(REPOS/'kokura/kokura-cli.exe'),str(rom),'--hardware',profile,'--run-frames','240','--watchpoint','0xC112','--watch-window','marks:49424:3','--png',str(image),'--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview']
            run=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=180);(folder/'visible.txt').write_bytes(run.stdout+run.stderr)
            assert run.returncode==0 and json.loads(report.read_text())['watched_memory'][0]['preview_bytes']==[1,1,1]
            pixels=read_png(image)
            if reference_pixels is None:reference_pixels=pixels
            same=pixels==reference_pixels
            row=dict(profile=profile,height=height,color=color,version=version,cycles=times[1]-times[0],lines=len(endpoints),pixels_equal_to_baseline=same,image_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),library_sha256=hashlib.sha256(library.read_bytes()).hexdigest())
            records.append(row);print(profile,height,color,version,row['cycles'],flush=True)
            (OUT/'line-speed-results.json').write_text(json.dumps(records,indent=2))
            assert same, 'optimized raster pixels differ from baseline'

if __name__=='__main__':main()
