"""Build the C runtime queue sample and check geometry, colors and queue assertions."""
from pathlib import Path
import json,hashlib,subprocess
from check_entity_callbacks import check_pixels
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUTPUT=SITE/'verification/api-runtime-queue'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def geometry_errors(image):
 width,height,channels,rows=read_png(image)
 patterns={0:[0]*8,1:[255]*8,2:[240]*8,3:[128,192,224,240,248,252,254,255]}
 tiles={}
 for i in range(127):tiles[(i%32,2+i//32)]=(i%3+1,'blue')
 for i in range(127):tiles[(i%32,8+i//32)]=(1,'green')
 tiles.update({(2,14):(1,'red'),(28,14):(2,'red')})
 shapes=0;colors=0
 for y in list(range(16,48))+list(range(64,96))+list(range(112,120)):
  for x in range(width):
   tile,color=tiles.get((x//8,y//8),(0,'black'))
   ink=bool(patterns[tile][y%8]&(1<<(7-x%8)))
   rgb=rows[y][x*channels:x*channels+3]
   actual=not matches_color(rgb,'black')
   shapes+=ink!=actual
   if ink:colors+=not matches_color(rgb,color)
 return shapes,colors
folder=OUTPUT/'fc-nrom';folder.mkdir(parents=True,exist_ok=True)
source=SITE/'samples/api-examples/fc/runtime_queue.c'
compiler=REPOS/'kitaqfc/kitaqfc.exe';emulator=REPOS/'kurosaki/kurosaki.exe'
rom=folder/'example.nes';image=folder/'screen.png';report=folder/'runtime.json'
for path in [rom,image,report]:path.unlink(missing_ok=True)
command=[str(compiler),str(source),'-I',str(REPOS/'kitaqfc/lib'),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper=nrom','--nes-chr='+str(SITE/'samples/api-examples/fc/vram_shapes.chr'),'--no-cache','--no-disasm']
process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
(folder/'build.txt').write_bytes(process.stdout+process.stderr)
row={'platform':'fc','mode':'nrom','source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'compiler_sha256':sha(compiler),'library_sha256':{name:sha(REPOS/'kitaqfc/lib'/name) for name in ['intrinsics.h','runtime.h','runtime.c']},'build_command':command,'build_exit':process.returncode,'passed':False,
 'support_sha256':{name:sha(SITE/name) for name in ['samples/fc_common.h','samples/api-examples/fc/vram_shapes.chr']}}
if process.returncode==0:
 command=[str(emulator),'run',str(rom),'--frames','240','--png',str(image),'--json',str(report)]
 process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
 (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
 row.update(runtime_exit=process.returncode,run_command=command,rom_sha256=sha(rom),emulator_sha256=sha(emulator))
 if process.returncode==0 and image.exists():
  state=json.loads(report.read_text(encoding='utf-8'));frames=state['frames']
  labels=[(1,0,'RUNTIME VRAM QUEUE'),(1,6,'BLUE COPIED PAYLOAD'),(1,12,'GREEN FILL'),(1,13,'ZERO / NMI / CANCEL')]
  labels += [(1,y,label) for y,label in enumerate(['CAPACITY','ENCODED BYTES','AFTER FLUSH','REJECTED LENGTH','OVERFLOW SEEN','FAILED CHECKS'],16)]
  labels += [(20,y,value) for y,value in enumerate(['192','145','000','001','001','000'],16)]
  label_errors=check_pixels(image,labels,'fc');shapes,colors=geometry_errors(image)
  row.update(image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),expected_labels=labels,label_pixel_mismatches=label_errors,geometry_pixel_mismatches=shapes,geometry_color_mismatches=colors,geometry_pixels_checked=18432,ppu_writes_while_rendering=state['ppu']['data_writes_while_rendering'],frames=frames,passed=label_errors==0 and shapes==0 and colors==0 and frames==240 and state['ppu']['data_writes_while_rendering']==0)
if row['passed']:
 cleanup_build_outputs(folder)
 (folder/'integration_test/reports/COMMAND_HISTORY.log').unlink(missing_ok=True)
(OUTPUT/'results.json').write_text(json.dumps({'records':[row],'scope':'0/127-byte runtime records, immediate payload copies, exact capacity and rejected lengths, queue/latch clearing, direct and runtime-NMI execution, visible geometry and color. NROM emulator only; real hardware not tested.'},indent=2),encoding='utf-8')
print('fc nrom','PASS' if row['passed'] else 'FAIL')
if not row['passed']:raise SystemExit(1)
