"""Measure separately the clear, transform, raster and transfer stages of two cubes."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3]
REPOS=ROOT/'publish/github_20260912'
OUT=ROOT/'publish/library_docs_20260914/fc-effects/wire3d'

def main():
    rows=[]
    for width,height in [(64,48),(96,64),(128,96)]:
        for version in ['baseline','optimized']:
            folder=OUT/f'bench-{width}-{version}';folder.mkdir(exist_ok=True)
            lib=OUT/'baseline-source' if version=='baseline' else REPOS/'kitaqfc/lib'
            original=(lib/'wire3d.c').read_text();body=original
            start=body.index('void Wire3DFC_DrawModel(');end=body.index('\n}',start)
            function=body[start:end]
            function=function.replace('    for(i=0;i<vertex_count;i++)', '    model_phase=1;\n    for(i=0;i<vertex_count;i++)',1)
            function=function.replace('    for(i=0;i<edge_count;i++)', '    model_phase=2;\n    for(i=0;i<edge_count;i++)',1)
            body=body[:start]+function+'\n    model_phase=3;'+body[end:]
            main=(OUT/'bench.c').read_text().replace('#include "wire3d.c"', '')
            source=folder/'case.c';rom=folder/'case.nes';trace=folder/'trace.jsonl'
            source.write_text(f'#define WIRE3D_FC_WIDTH {width}\n#define WIRE3D_FC_HEIGHT {height}\n__location(0x0609) u8 model_phase;\n'+body+'\n'+main)
            cmd=[str(REPOS/'kitaqfc/kitaqfc.exe'),str(source),'-I',str(lib),'-I',str(REPOS/'kitaqfc/lib'),'-o',str(rom),'--mapper=nrom','--nes-chr-ram','--no-cache','--no-disasm']
            build=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120);(folder/'build.txt').write_bytes(build.stdout+build.stderr)
            if build.returncode:raise RuntimeError(str(folder)+' build failed')
            run=subprocess.run([str(REPOS/'kurosaki/kurosaki.exe'),'trace',str(rom),'--frames','180','--mem-write','--out',str(trace)],capture_output=True,timeout=120)
            if run.returncode:raise RuntimeError(str(folder)+' run failed')
            events=[]
            for entry in trace.open():
                r=json.loads(entry)
                if r['addr'] in [0x608,0x609]:events.append(dict(marker=r['addr'],value=r['value'],cycle=r['cpu_cycle']))
            phases=[r for r in events if r['marker']==0x608];models=[r for r in events if r['marker']==0x609]
            assert [r['value'] for r in phases]==[1,2,3,4,1,2,3,4,5]
            assert [r['value'] for r in models]==[1,2,3,1,2,3]
            stages=[]
            for n in range(2):
                a=phases[n*4:n*4+4];b=models[n*3:n*3+3]
                stages.append(dict(angle=n,clear=a[1]['cycle']-a[0]['cycle'],transform=b[1]['cycle']-b[0]['cycle'],raster=b[2]['cycle']-b[1]['cycle'],transfer=a[3]['cycle']-a[2]['cycle'],total=a[3]['cycle']-a[0]['cycle']))
            row=dict(width=width,height=height,version=version,stages=stages,markers=events,library_sha256=hashlib.sha256(original.encode()).hexdigest(),rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest())
            rows.append(row);print(width,version,stages,flush=True)
            (OUT/'benchmarks.json').write_text(json.dumps(rows,indent=2))
            # The bounded measurement is retained above; remove the raw temporary trace.
            assert trace.resolve().is_relative_to(OUT.resolve());trace.unlink()

if __name__=='__main__':main()
