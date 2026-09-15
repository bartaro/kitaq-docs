"""Verify the FC physics header's game-side subpixel example in KUROSAKI."""
from pathlib import Path
import hashlib,json,subprocess
from check_batch200 import dependencies
from check_entity_callbacks import check_pixels
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-physics/fc-subpixel';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=SITE/'samples/api-examples/fc/physics_subpixel.c';rom=OUT/'example.nes';image=OUT/'screen.png';snapshot=OUT/'runtime.json'
compiler=REPOS/'kitaqfc/kitaqfc.exe';emulator=REPOS/'kurosaki/kurosaki.exe';lib=compiler.parent/'lib';chrfile=SITE/'samples/api-examples/fc/vram_shapes.chr'
run=subprocess.run([str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper=nrom','--nes-chr='+str(chrfile),'--no-cache','--no-disasm'],cwd=OUT,capture_output=True,timeout=120)
(OUT/'build.txt').write_bytes(run.stdout+run.stderr);assert run.returncode==0
run=subprocess.run([str(emulator),'run',str(rom),'--frames','120','--headless','--snapshot',str(snapshot),'--png',str(image)],cwd=OUT,capture_output=True,timeout=120);assert run.returncode==0
state=json.loads(snapshot.read_text(encoding='utf-8'));raw=state['bus']['ram'][0x600:0x6A0];actual=[raw[i]+raw[i+1]*256 for i in range(0,160,2)]
expected=[32,0,28,0,28]+[0]*74+[0xA55A];labels=[(1,0,'HALF-PIXEL STEPS'),(1,6,'BEFORE X=24'),(1,12,'16 TICKS X=32')]
label_errors=check_pixels(image,labels,'fc');w,h,c,rows=read_png(image);pixel_errors=0
for y in range(h):
 for x in range(w):
  if any(ly*8<=y<(ly+1)*8 and lx*8<=x<(lx+len(text))*8 for lx,ly,text in labels):continue
  ink=24<=x<40 and 64<=y<80 or 32<=x<48 and 112<=y<128
  pixel_errors+=not matches_color(rows[y][x*c:x*c+3],'red' if ink else 'black')
inputs=dependencies(source,lib);inputs[chrfile.relative_to(SITE).as_posix()]=sha(chrfile)
result=dict(platform='fc',source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=inputs,actual=actual,expected=expected,pixel_mismatches=pixel_errors,label_pixel_mismatches=label_errors,passed=actual==expected and pixel_errors==label_errors==0,script_sha256=sha(Path(__file__)))
(OUT.parent/'fc_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8');cleanup_build_outputs(OUT)
print('FC subpixel','PASS' if result['passed'] else 'FAIL',actual[:5],pixel_errors,label_errors)
raise SystemExit(0 if result['passed'] else 1)
