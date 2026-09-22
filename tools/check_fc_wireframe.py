"""Check FC wireframe pixels, clearing and PPU timing at all three resolutions."""
from pathlib import Path
import hashlib,json,random,subprocess
from check_api_tile_examples import read_png
ROOT=Path(__file__).resolve().parents[3]
REPOS=ROOT/'publish/github_20260912'
OUT=ROOT/'publish/library_docs_20260914/fc-effects/wire3d/proofs'

def line(a,b):
    x,y=a;bx,by=b;dx=abs(bx-x);dy=abs(by-y)
    sx=1 if x<bx else -1;sy=1 if y<by else -1;error=dx-dy
    while True:
        yield x,y
        if (x,y)==(bx,by):break
        twice=2*error
        if twice>-dy:error-=dy;x+=sx
        if twice<dx:error+=dx;y+=sy

def main():
    OUT.mkdir(parents=True,exist_ok=True);records=[]
    cube=(ROOT/'manual/latest/samples/api-examples/fc/wire3d_cube.c').read_text()
    for w,h in [(64,48),(96,64),(128,96)]:
        rng=random.Random(327+w)
        lines=[(0,0,w-1,h-1),(w-1,0,0,h-1),(0,h//2,w-1,h//2),(w//2,0,w//2,h-1)]
        lines += [tuple(rng.randrange(n) for n in [w,h,w,h]) for _ in range(48)]
        # Clipped lines exercise the word fallback without changing its pixel rule.
        lines += [(-32,h//3,w+30,h//2),(w//2,-24,w//3,h+18),(-10,-10,-1,h)]
        want=set()
        for x,y,bx,by in lines:want.update((a,b) for a,b in line((x,y),(bx,by)) if 0<=a<w and 0<=b<h)
        for case in ['lines','clear','cube']:
            folder=OUT/(str(w)+'-'+case);folder.mkdir(exist_ok=True)
            prefix=f'#define WIRE3D_FC_WIDTH {w}\n#define WIRE3D_FC_HEIGHT {h}\n'
            if case=='cube':
                text=prefix+cube.replace('wire_angle=0;', 'wire_angle=3;').replace('wire_frames++;wire_angle=', 'wire_frames++;while(1){}wire_angle=')
                # Independent signed Q6 transform then reciprocal perspective.
                sin,cos=36,53;verts=[]
                for x,y,z in [(-24,-24,-24),(24,-24,-24),(24,24,-24),(-24,24,-24),(-24,-24,24),(24,-24,24),(24,24,24),(-24,24,24)]:
                    px=int((x*cos+z*sin)/64);pz=int((z*cos-x*sin)/64)+96
                    scale=min(255,round(64*w/pz))
                    verts.append((w//2+(1 if px>=0 else -1)*(abs(px)*scale//128),h//2-(1 if y>=0 else -1)*(abs(y)*scale//128)))
                expected=set()
                for a,b in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:expected.update(line(verts[a],verts[b]))
            else:
                text=prefix+'#include "wire3d.c"\n__location(0x0600) u8 done;\nvoid main(){Wire3DFC_Init();Wire3DFC_BeginFrame();'
                for x,y,bx,by in lines:text+=f'Wire3DFC_DrawLine2D({x},{y},{bx},{by});'
                text+='Wire3DFC_EndFrame();'
                if case=='clear':
                    # Clear both hidden-bank histories, including pixels from two frames ago.
                    text+='Wire3DFC_BeginFrame();Wire3DFC_DrawLine2D(0,0,1,1);Wire3DFC_EndFrame();Wire3DFC_BeginFrame();Wire3DFC_EndFrame();'
                text+='done=1;while(1){}}';expected=want if case=='lines' else set()
            source=folder/'case.c';rom=folder/'case.nes';source.write_text(text,encoding='utf-8')
            cmd=[str(REPOS/'kitaqfc/kitaqfc.exe'),str(source),'-I',str(REPOS/'kitaqfc/lib'),'-o',str(rom),'--mapper=nrom','--nes-chr-ram','--no-cache','--no-disasm']
            build=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120);(folder/'build.txt').write_bytes(build.stdout+build.stderr)
            if build.returncode:raise RuntimeError(str(folder)+' build failed')
            state=folder/'state.json';summary=folder/'run.json';png=folder/'screen.png'
            subprocess.run([str(REPOS/'kurosaki/kurosaki.exe'),'run',str(rom),'--frames','180','--headless','--snapshot',str(state),'--json',str(summary),'--png',str(png)],check=True,timeout=90)
            data=json.loads(state.read_text());ram=data['bus']['ram'];width,height,channels,pixels=read_png(png)
            actual={(x,y) for y in range(height) for x in range(width) if any(pixels[y][x*channels:x*channels+3])}
            ox=(32-w//8)//2*8;oy=(30-h//8)//2*8
            expected={(x+ox,y+oy) for x,y in expected}
            mismatch=actual^expected;ppu=data['bus']['ppu']
            row=dict(width=w,height=h,case=case,complete=ram[0x600]==1,pixel_mismatches=len(mismatch),first_mismatches=sorted(mismatch)[:10],unsafe_vram_writes=ppu['data_writes_outside_vblank'],unsafe_address_writes=ppu['addr_writes_while_rendering'],image=str(png.relative_to(ROOT)),rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest())
            dependencies=[REPOS/'kitaqfc/lib'/n for n in ['wire3d.c','wire3d.h','wire3d_tables.h','core.h','intrinsics.h']]
            dependencies += [REPOS/'kitaqfc/kitaqfc.exe',REPOS/'kurosaki/kurosaki.exe',source,rom,png,Path(__file__)]
            row['input_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies}
            row['passed']=row['complete'] and not mismatch and not row['unsafe_vram_writes'] and not row['unsafe_address_writes']
            records.append(row);print(w,case,row['passed'],row['pixel_mismatches'],row['unsafe_vram_writes'],flush=True)
            (OUT/'results.json').write_text(json.dumps(records,indent=2))
            # Keep the image, ROM and concise evidence; the 1.5 MB raw snapshot is temporary.
            assert state.resolve().is_relative_to(OUT.resolve());state.unlink()
    assert len(records)==9 and all(r['passed'] for r in records)

if __name__=='__main__':main()
