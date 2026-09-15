"""Execute the IRQ/NMI teaching ROM and compare the observed values and font pixels."""
from pathlib import Path
import hashlib,json,subprocess
from check_entity_callbacks import check_pixels
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs

SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUTPUT=SITE/'verification/api-interrupt-intrinsics'
folder=OUTPUT/'nrom';folder.mkdir(parents=True,exist_ok=True)
source=SITE/'samples/api-examples/fc/interrupt_intrinsics.c'
compiler=REPOS/'kitaqfc/kitaqfc.exe';emulator=REPOS/'kurosaki/kurosaki.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rom=folder/'example.nes';image=folder/'screen.png';runtime=folder/'runtime.json'
for path in [rom,image,runtime]:path.unlink(missing_ok=True)
command=[str(compiler),str(source),'-I',str(REPOS/'kitaqfc/lib'),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper=nrom','--nes-chr='+str(SITE/'samples/font.chr'),'--no-cache','--no-disasm']
process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
(folder/'build.txt').write_bytes(process.stdout+process.stderr)
row={'platform':'fc','mode':'nrom','source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'compiler_sha256':sha(compiler),'header_sha256':sha(REPOS/'kitaqfc/lib/intrinsics.h'),'support_sha256':{name:sha(SITE/name) for name in ['samples/fc_common.h','samples/font.chr']},'build_exit':process.returncode,'passed':False}
if process.returncode==0:
    process=subprocess.run([str(emulator),'run',str(rom),'--frames','360','--png',str(image),'--json',str(runtime)],capture_output=True,timeout=90,cwd=folder)
    (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
    row.update(runtime_exit=process.returncode,rom_sha256=sha(rom),emulator_sha256=sha(emulator))
    if process.returncode==0:
        labels=[(1,1,'IRQ MASK AND NMI COUNTER'),(1,25,'DEFAULT HANDLER ONLY')]
        values=[(4,'IRQ DISABLED I','001'),(6,'IRQ ENABLED I','000'),(8,'SAVED SECTION I','001'),(10,'RESTORED I','000'),(14,'NMI DELTA 3 WAITS','003'),(16,'NMI DELTA 256 WAITS','000'),(18,'NMI OFF DELTA','000'),(22,'FAILED CHECKS','000')]
        for y,text,value in values:labels.extend([(1,y,text),(27,y,value)])
        errors=check_pixels(image,labels,'fc');width,height,channels,rows=read_png(image)
        color_errors=0;colored_pixels=0
        for pixels in rows:
            for x in range(width):
                rgb=pixels[x*channels:x*channels+3]
                if not matches_color(rgb,'black'):
                    colored_pixels+=1;color_errors+=not matches_color(rgb,'blue')
        state=json.loads(runtime.read_text(encoding='utf-8'))
        row.update(image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),labels=labels,label_pixel_mismatches=errors,color_mismatches=color_errors,colored_pixels=colored_pixels,frames=state['frames'],ppu_writes_while_rendering=state['ppu']['data_writes_while_rendering'],passed=errors==0 and color_errors==0 and colored_pixels>0 and state['frames']==360 and state['ppu']['data_writes_while_rendering']==0)
if row['passed']:cleanup_build_outputs(folder)
(OUTPUT/'results.json').write_text(json.dumps({'records':[row],'scope':'Default NMI counter and CPU IRQ-mask state; no IRQ-generating peripheral or physical hardware test.'},indent=2),encoding='utf-8')
print(json.dumps(row))
raise SystemExit(0 if row['passed'] else 1)
