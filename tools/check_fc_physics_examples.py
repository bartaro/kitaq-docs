"""Execute every FC box-physics teaching call and compare RAM and all pixels."""
from pathlib import Path
import hashlib,json,subprocess
from check_physics_examples import expected_panels
from check_api_tile_examples import read_png
from check_entity_callbacks import check_pixels
from api_vram_colors import matches_color
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
OUT=SITE/'verification/api-physics-fc';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True);records=[]
    specs=json.loads((SITE/'tools/api_descriptions/physics_examples.json').read_text(encoding='utf-8'))
    compiler=REPOS/'kitaqfc/kitaqfc.exe';emulator=REPOS/'kurosaki/kurosaki.exe';lib=compiler.parent/'lib'
    for spec in specs:
        group=spec['group']
        if group=='circle':continue
        source=SITE/spec['source'].replace('/gb/','/fc/');folder=OUT/group;folder.mkdir(exist_ok=True)
        rom=folder/'example.nes';image=folder/'screen.png';state=folder/'state.json'
        command=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper=mmc3','--nes-chr-ram','--no-cache','--no-disasm']
        build=subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
        (folder/'build.txt').write_bytes(build.stdout+build.stderr)
        if build.returncode:raise RuntimeError((build.stdout+build.stderr).decode(errors='replace')[-3500:])
        run=subprocess.run([str(emulator),'run',str(rom),'--frames','240','--headless','--snapshot',str(state),'--png',str(image)],cwd=folder,capture_output=True,timeout=120)
        assert run.returncode==0
        data=json.loads(state.read_text(encoding='utf-8'));raw=data['bus']['ram'][0x600:0x6A0]
        actual=[raw[i]+256*raw[i+1] for i in range(0,160,2)]
        want=spec['expected']+[0]*(79-len(spec['expected']))+[0xA55A]
        labels=check_pixels(image,spec['labels'],'fc');panels=expected_panels(spec['shapes'])
        w,h,c,rows=read_png(image);mismatches=[]
        for y in range(h):
            for x in range(w):
                if any(ly*8<=y<(ly+1)*8 and lx*8<=x<(lx+len(t))*8 for lx,ly,t in spec['labels']):continue
                color=0
                for p,origin in enumerate([8,88]):
                    if origin<=x<origin+64 and 48<=y<112:color=panels[p][y-48][x-origin]
                expected=['black','red','blue','green'][color]
                if not matches_color(rows[y][x*c:x*c+3],expected):mismatches.append([x,y,expected])
        row=dict(platform='fc',group=group,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=dependencies(source,lib),actual=actual,expected=want,label_pixel_mismatches=labels,pixel_mismatches=len(mismatches),first_pixel_mismatches=mismatches[:12],unsafe_ppu_writes=data['bus']['ppu']['data_writes_while_rendering'])
        row['passed']=actual==want and labels==0 and not mismatches and row['unsafe_ppu_writes']==0
        records.append(row)
        print(group,'PASS' if row['passed'] else 'FAIL','RAM',[(i,a,b) for i,(a,b) in enumerate(zip(actual,want)) if a!=b][:12],'pixels',len(mismatches),'labels',labels,flush=True)
        if row['passed']:state.unlink();cleanup_build_outputs(folder)
        (OUT/'results.json').write_text(json.dumps(dict(records=records,script_sha256=sha(Path(__file__)),spec_sha256=sha(SITE/'tools/api_descriptions/physics_examples.json')),indent=2),encoding='utf-8')
    raise SystemExit(0 if len(records)==3 and all(r['passed'] for r in records) else 1)
if __name__=='__main__':main()
