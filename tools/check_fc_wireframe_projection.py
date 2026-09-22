"""Execute the complete FC teaching program and check geometry, colors and RAM."""
from pathlib import Path
import hashlib,json,subprocess
from check_api_tile_examples import read_png
from check_fc_wireframe import line
SITE=Path(__file__).resolve().parents[1]
ROOT=SITE.parents[1];REPOS=ROOT/'publish/github_20260912'
OUT=SITE/'verification/api-wireframe-fc/projection'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def expected_scene(w,h):
    # Rounded reciprocal projection, with integer magnitudes truncated to pixels.
    def project(x,y,z):
        scale=min(255,(64*w+z//2)//z)
        return w//2+(1 if x>=0 else -1)*(abs(x)*scale//128),h//2-(1 if y>=0 else -1)*(abs(y)*scale//128)
    sx,sy=project(0,24,96)
    segments=[((0,0),(w-1,0)),((w-1,0),(w-1,h-1)),((w-1,h-1),(0,h-1)),((0,h-1),(0,0)),((sx-3,sy),(sx+3,sy)),((sx,sy-3),(sx,sy+3)),(project(-24,-24,96),project(24,-24,96))]
    points=[]
    for x,y,z in [(-12,-12,-12),(12,-12,-12),(12,12,-12),(-12,12,-12),(-12,-12,12),(12,-12,12),(12,12,12),(-12,12,12)]:
        points.append(project(int((x*53+z*36)/64),y,int((z*53-x*36)/64)+96))
    for a,b in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:segments.append((points[a],points[b]))
    pixels={p for a,b in segments for p in line(a,b)}
    tiles={(x//8,y//8) for x,y in pixels}
    return pixels,[0,24,0,1,sx,sy,len(tiles),0xA55A]

def main():
    records=[];source=SITE/'samples/api-examples/fc/wire3d_projection.c'
    for w,h in [(64,48),(96,64),(128,96)]:
        folder=OUT/str(w);folder.mkdir(parents=True,exist_ok=True)
        wrapper=folder/'build.c';rom=folder/'example.nes';image=folder/'screen.png'
        wrapper.write_text(f'#define WIRE3D_FC_WIDTH {w}\n#define WIRE3D_FC_HEIGHT {h}\n#include "{source.as_posix()}"\n')
        cmd=[str(REPOS/'kitaqfc/kitaqfc.exe'),str(wrapper),'-I',str(REPOS/'kitaqfc/lib'),'-o',str(rom),'--mapper=nrom','--nes-chr-ram','--no-cache','--no-disasm']
        p=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120);(folder/'build.txt').write_bytes(p.stdout+p.stderr)
        assert p.returncode==0,str(folder)
        state=folder/'state.json'
        p=subprocess.run([str(REPOS/'kurosaki/kurosaki.exe'),'run',str(rom),'--frames','180','--headless','--snapshot',str(state),'--png',str(image)],cwd=folder,capture_output=True,timeout=120);(folder/'run.txt').write_bytes(p.stdout+p.stderr)
        assert p.returncode==0
        snapshot=json.loads(state.read_text());ram=snapshot['bus']['ram'];ppu=snapshot['bus']['ppu']
        pixels,expected=expected_scene(w,h);actual=[ram[0x600+i*2]+256*ram[0x601+i*2] for i in range(8)]
        ox=(32-w//8)//2*8;oy=(30-h//8)//2*8;pixels={(x+ox,y+oy) for x,y in pixels}
        width,height,channels,rows=read_png(image);assert (width,height)==(256,240)
        mismatches=[]
        for y in range(240):
            for x in range(256):
                want=(72,205,222) if (x,y) in pixels else (0,0,0)
                if tuple(rows[y][x*channels:x*channels+3])!=want:mismatches.append((x,y))
        inputs={('kitaqfc/lib/'+n):sha(REPOS/'kitaqfc/lib'/n) for n in ['wire3d.c','wire3d.h','wire3d_tables.h','core.h','intrinsics.h']}
        inputs[source.relative_to(SITE).as_posix()]=sha(source)
        for name in ['check_fc_wireframe.py','check_api_tile_examples.py']:
            inputs['tools/'+name]=sha(SITE/'tools'/name)
        row=dict(platform='fc',group='wire3d_projection',mode=f'{w}x{h}',source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(REPOS/'kitaqfc/kitaqfc.exe'),emulator_sha256=sha(REPOS/'kurosaki/kurosaki.exe'),input_sha256=inputs,actual=actual,expected=expected,pixel_mismatches=len(mismatches),first_mismatches=mismatches[:10],unsafe_vram_writes=ppu['data_writes_outside_vblank'],unsafe_address_writes=ppu['addr_writes_while_rendering'])
        row['passed']=actual==expected and not mismatches and not row['unsafe_vram_writes'] and not row['unsafe_address_writes']
        records.append(row);print(w,row['passed'],actual,len(mismatches),flush=True)
        (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=records),indent=2))
        assert state.resolve().is_relative_to(OUT.resolve());state.unlink()
        assert row['passed'],row

if __name__=='__main__':main()
