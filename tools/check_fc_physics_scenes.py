"""Check the body/world lessons against independent RAM and color-pixel expectations."""
from pathlib import Path
import hashlib,json,subprocess
from check_api_tile_examples import read_png
from check_entity_callbacks import check_pixels
from api_vram_colors import matches_color
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
OUT=SITE/'verification/api-fc-physics-worlds';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True);rows=[]
    compiler=REPOS/'kitaqfc/kitaqfc.exe';emulator=REPOS/'kurosaki/kurosaki.exe';lib=compiler.parent/'lib'
    for dim in [2,3]:
        source=SITE/f'samples/api-examples/fc/physics_world{dim}d.c'
        folder=OUT/f'{dim}d';folder.mkdir(exist_ok=True);rom=folder/'example.nes';image=folder/'screen.png';state=folder/'state.json'
        build=subprocess.run([str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper=mmc3','--nes-chr='+str(SITE/'samples/api-examples/fc/vram_shapes.chr'),'--no-cache','--no-disasm'],cwd=folder,capture_output=True,timeout=120)
        (folder/'build.txt').write_bytes(build.stdout+build.stderr)
        if build.returncode:raise RuntimeError((build.stdout+build.stderr).decode(errors='replace')[-2200:])
        run=subprocess.run([str(emulator),'run',str(rom),'--frames','240','--headless','--snapshot',str(state),'--png',str(image)],cwd=folder,capture_output=True,timeout=120)
        assert run.returncode==0
        data=json.loads(state.read_text(encoding='utf-8'));raw=data['bus']['ram'][0x600:0x610];actual=[raw[i]+raw[i+1]*256 for i in range(0,16,2)]
        expected=[48,72,0,0,0,0,0,42330] if dim==2 else [48,32,24,65512,24,0,0,42330]
        labels=[(1,1,'2D GRAVITY AND FLOOR' if dim==2 else '3D WALL BOUNCE: XZ VIEW'),(1,5,'BEFORE'),(17,5,'AFTER 4 STEPS' if dim==2 else 'AFTER 1 STEP'),(1,21,'RED BOX / BLUE FLOOR' if dim==2 else 'RED BOX / BLUE WALL'),(1,23,'Y=32 -> 72   VY=0' if dim==2 else 'Z=8 -> 24   VZ=-24')]
        rects=[(40,88,16,16,'red'),(168,128,16,16,'red'),(16,144,64,16,'blue'),(144,144,64,16,'blue')] if dim==2 else [(40,64,16,16,'red'),(168,80,16,16,'red'),(16,96,64,16,'blue'),(144,96,64,16,'blue')]
        label_errors=check_pixels(image,labels,'fc');w,h,c,pixels=read_png(image);errors=0
        for y in range(h):
            for x in range(w):
                if any(lx*8<=x<(lx+len(t))*8 and ly*8<=y<(ly+1)*8 for lx,ly,t in labels):continue
                color='black'
                for rx,ry,rw,rh,ink in rects:
                    if rx<=x<rx+rw and ry<=y<ry+rh:color=ink
                errors+=not matches_color(pixels[y][x*c:x*c+3],color)
        passed=actual==expected and label_errors==errors==0 and data['bus']['ppu']['data_writes_while_rendering']==0
        rows.append(dict(platform='fc',dimension=dim,passed=passed,actual=actual,expected=expected,labels=labels,rectangles=rects,pixel_mismatches=errors,label_pixel_mismatches=label_errors,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=dependencies(source,lib)))
        print(dim,'PASS' if passed else 'FAIL',actual,label_errors,errors,flush=True)
        if passed:state.unlink();cleanup_build_outputs(folder)
        (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=rows,passed=all(r['passed'] for r in rows)),indent=2),encoding='utf-8')
    raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
if __name__=='__main__':main()
