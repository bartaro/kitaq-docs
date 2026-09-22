"""Check bullet movement, rotating OAM selection, reserved slots and colored pixels."""
from pathlib import Path
import hashlib,json,math,subprocess
from check_api_tile_examples import read_png
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
OUT=SITE/'verification/api-fc-danmaku';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    records=[];source=SITE/'samples/api-examples/fc/danmaku_patterns.c'
    centers=[(64,64),(48,80),(32,64),(48,48)]
    for i in range(16):
        angle=2*math.pi*i/16
        centers.append((160+int(round(math.cos(angle)*64)/2),104+int(round(math.sin(angle)*64)/2)))
    expected=[0,1,0,20,0,0,8,centers[13][0]-4,centers[13][1]-5,20,20,0xA55A]
    pixels={};bitmap=[24,60,126,255,255,126,60,24]
    for x,y,color in [(112,192,(72,205,222))]+[(x,y,(188,190,0)) for x,y in centers]:
        for dy,row in enumerate(bitmap):
            for dx in range(8):
                if row&(128>>dx):pixels[x-4+dx,y-4+dy]=color
    expected_oam=[187,1,1,108]
    for x,y in centers:expected_oam += [y-5,1,0,x-4]
    for mode,flags in [('default',[]),('O0',['-O0']),('no-inline',['--no-small-inline']),('fastcall',['--fastcall-v2'])]:
        folder=OUT/mode;folder.mkdir(parents=True,exist_ok=True);rom=folder/'example.nes';image=folder/'screen.png';state=folder/'state.json'
        cmd=[str(REPOS/'kitaqfc/kitaqfc.exe'),str(source),'-I',str(REPOS/'kitaqfc/lib'),'-o',str(rom),'--mapper=nrom','--nes-chr-ram','--no-cache','--no-disasm']+flags
        p=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120);(folder/'build.txt').write_bytes(p.stdout+p.stderr);assert p.returncode==0,str(folder)
        p=subprocess.run([str(REPOS/'kurosaki/kurosaki.exe'),'run',str(rom),'--frames','180','--headless','--snapshot',str(state),'--png',str(image)],capture_output=True,timeout=120);(folder/'run.txt').write_bytes(p.stdout+p.stderr);assert p.returncode==0
        data=json.loads(state.read_text());ram=data['bus']['ram'];ppu=data['bus']['ppu'];oam=ppu['oam']
        actual=[ram[0x600+i*2]+256*ram[0x601+i*2] for i in range(12)]
        w,h,c,rows=read_png(image);assert (w,h)==(256,240)
        bad=[(x,y) for y in range(240) for x in range(256) if tuple(rows[y][x*c:x*c+3])!=pixels.get((x,y),(0,0,0))]
        oam_ok=oam[:84]==expected_oam and all(oam[i*4]==240 for i in range(21,64)) and oam==ram[512:768]
        inputs={('kitaqfc/lib/'+n):sha(REPOS/'kitaqfc/lib'/n) for n in ['danmaku.c','danmaku.h','core.h','intrinsics.h']}
        inputs[source.relative_to(SITE).as_posix()]=sha(source)
        inputs['tools/check_api_tile_examples.py']=sha(SITE/'tools/check_api_tile_examples.py')
        row=dict(platform='fc',mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(REPOS/'kitaqfc/kitaqfc.exe'),emulator_sha256=sha(REPOS/'kurosaki/kurosaki.exe'),input_sha256=inputs,actual=actual,expected=expected,pixel_mismatches=len(bad),first_mismatches=bad[:10],oam_matches_expected=oam_ok,oam=oam,unsafe_vram_writes=ppu['data_writes_outside_vblank'],unsafe_address_writes=ppu['addr_writes_while_rendering'])
        row['passed']=actual==expected and not bad and oam_ok and not row['unsafe_vram_writes'] and not row['unsafe_address_writes']
        records.append(row);print(mode,row['passed'],actual,len(bad),oam_ok,flush=True)
        (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=records),indent=2))
        assert state.resolve().is_relative_to(OUT.resolve());state.unlink()
        assert row['passed'],row

if __name__=='__main__':main()
