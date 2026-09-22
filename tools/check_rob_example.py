"""Check the optical-timing sample state, labels and all waveform diagram pixels."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from check_batch200 import dependencies
from check_entity_callbacks import check_pixels
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
ap=argparse.ArgumentParser();ap.add_argument('--compiler',type=Path,default=REPOS/'kitaqfc/kitaqfc.exe');opt=ap.parse_args()
compiler=opt.compiler.resolve();emulator=REPOS/'kurosaki/kurosaki.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=SITE/'verification/api-rob/example';out.mkdir(parents=True,exist_ok=True)
source=SITE/'samples/api-examples/fc/rob_timing.c';rom=out/'example.nes';image=out/'screen.png';snapshot=out/'snapshot.json'
cmd=[str(compiler),str(source),'-I',str(REPOS/'kitaqfc/lib'),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper=nrom','--nes-chr='+str(SITE/'samples/api-examples/fc/vram_shapes.chr'),'--no-cache','--no-disasm']
p=subprocess.run(cmd,capture_output=True,timeout=90,cwd=out)
if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
p=subprocess.run([str(emulator),'run',str(rom),'--frames','160','--snapshot',str(snapshot),'--png',str(image)],capture_output=True,timeout=120,cwd=out);assert p.returncode==0
state=json.loads(snapshot.read_text());actual=state['bus']['ram'][0x700:0x705];expected=[1,5,48,0,165]
labels=[(1,0,'OPTICAL MASK TIMING'),(1,2,'FLASH WAITS 1'),(1,3,'PULSE 3 ON / 2 OFF = 5'),(1,4,'A5 BYTE WAITS 48'),(1,6,'ONE BLOCK = ONE WAIT'),(1,7,'WHITE ON / BLANK OFF'),(1,22,'FINAL MASK 0'),(1,24,'TIMING CHECKS OK')]
for bit in range(8):labels.append((2+(bit%4)*6,10 if bit<4 else 17,'1' if 0xA5&(0x80>>bit) else '0'))
label_errors=check_pixels(image,labels,'fc')
w,h,ch,rows=read_png(image);errors=0;pixels=0
for group in range(8):
 on=4 if 0xA5&(0x80>>group) else 2;x0=(2+(group%4)*6)*8;y0=(12 if group<4 else 19)*8
 for y in range(y0,y0+8):
  for x in range(x0,x0+48):
   rgb=rows[y][x*ch:x*ch+3];ink=x-x0<on*8
   errors+=not matches_color(rgb,'white' if ink else 'black');pixels+=1
inputs=dependencies(source,REPOS/'kitaqfc/lib');inputs['samples/api-examples/fc/vram_shapes.chr']=sha(SITE/'samples/api-examples/fc/vram_shapes.chr')
row=dict(platform='fc',mode='ntsc',source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),input_sha256=inputs,compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),actual=actual,expected=expected,label_pixel_mismatches=label_errors,pixel_mismatches=errors,diagram_pixels=pixels,passed=actual==expected and not errors and not label_errors)
(out/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),record=row),indent=2),encoding='utf-8')
print('Optical sample','PASS' if row['passed'] else 'FAIL',actual,'labels',label_errors,'diagram',errors)
if row['passed']:snapshot.unlink();cleanup_build_outputs(out)
raise SystemExit(0 if row['passed'] else 1)
