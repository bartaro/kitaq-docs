"""Build the direct PPU stream samples and check geometry, colors and queue assertions."""
from pathlib import Path
import json,hashlib,subprocess
from check_entity_callbacks import check_pixels
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUTPUT=SITE/'verification/api-ppu-intrinsics'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def geometry_errors(image,length):
 width,height,channels,rows=read_png(image)
 patterns={0:[0]*8,1:[255]*8,2:[240]*8,3:[128,192,224,240,248,252,254,255]}
 tiles={}
 for i in range(32):tiles[(i,2)]=(i%3+1,'blue');tiles[(i,3)]=(2,'blue')
 for y in range(6,10):
  for x in range(2,10):tiles[(x,y)]=(1,'green')
  for x in range(18,26):tiles[(x,y)]=(3,'red')
 tiles.update({(2,12):(1,'blue'),(3,12):(2,'blue'),(4,12):(3,'blue'),(10,12):(2,'red'),(18,12):(3,'green'),(2,18):(1,'red'),(10,18):(2,'blue'),(18,18):(3,'green')})
 shapes=0;colors=0
 for y in list(range(16,32))+list(range(48,80))+list(range(96,104))+list(range(144,152)):
  for x in range(width):
   tile,color=tiles.get((x//8,y//8),(0,'black'))
   ink=bool(patterns[tile][y%8]&(1<<(7-x%8)))
   rgb=rows[y][x*channels:x*channels+3]
   actual=not matches_color(rgb,'black')
   shapes+=ink!=actual
   if ink:colors+=not matches_color(rgb,color)
 return shapes,colors
records=[]
for mode,length in [('nrom',32)]:
 folder=OUTPUT/mode;folder.mkdir(parents=True,exist_ok=True)
 source=SITE/'samples/api-examples/fc/ppu_intrinsics.c'
 compiler=REPOS/'kitaqfc/kitaqfc.exe';emulator=REPOS/'kurosaki/kurosaki.exe'
 rom=folder/'example.nes';image=folder/'screen.png';report=folder/'runtime.json'
 for path in [rom,image,report]:path.unlink(missing_ok=True)
 command=[str(compiler),str(source),'-I',str(REPOS/'kitaqfc/lib'),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper=nrom','--nes-chr='+str(SITE/'samples/api-examples/fc/vram_shapes.chr'),'--no-cache','--no-disasm']
 process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
 (folder/'build.txt').write_bytes(process.stdout+process.stderr)
 row={'platform':'fc','mode':mode,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'compiler_sha256':sha(compiler),'library_sha256':{name:sha(REPOS/'kitaqfc/lib'/name) for name in ['intrinsics.h']},'build_command':command,'build_exit':process.returncode,'passed':False,
  'support_sha256':{name:sha(SITE/name) for name in ['samples/fc_common.h','samples/api-examples/fc/vram_shapes.chr']}}
 if process.returncode==0:
  command=[str(emulator),'run',str(rom),'--frames','240','--png',str(image),'--json',str(report)]
  process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
  (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
  row.update(runtime_exit=process.returncode,run_command=command,rom_sha256=sha(rom),emulator_sha256=sha(emulator))
  if process.returncode==0 and image.exists():
   state=json.loads(report.read_text(encoding='utf-8'));frames=state['frames']
   labels=[(1,0,'PPU INTRINSICS'),(1,20,'TOP: BLUE COPY AND FILL'),(1,21,'MIDDLE: GREEN / RED'),(1,22,'LOWER: ADDRESS MARKERS'),(1,23,'SPRITES: RED BLUE GREEN'),(1,25,'PPU DRAWING EXAMPLE')]
   label_errors=check_pixels(image,labels,'fc');shapes,colors=geometry_errors(image,length)
   row.update(image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),expected_labels=labels,label_pixel_mismatches=label_errors,geometry_pixel_mismatches=shapes,geometry_color_mismatches=colors,geometry_pixels_checked=16384,ppu_writes_while_rendering=state['ppu']['data_writes_while_rendering'],frames=frames,passed=label_errors==0 and shapes==0 and colors==0 and frames==240 and state['ppu']['data_writes_while_rendering']==0)
 if row['passed']:
  cleanup_build_outputs(folder)
  (folder/'integration_test/reports/COMMAND_HISTORY.log').unlink(missing_ok=True)
 records.append(row)
 print('fc',mode,'PASS' if row['passed'] else 'FAIL',flush=True)
(OUTPUT/'results.json').write_text(json.dumps({'records':records,'scope':'Direct PPU/control/scroll APIs with visible background and sprite palettes, shapes and register/latch state checks. NROM emulator only; real hardware not tested.'},indent=2),encoding='utf-8')
if not all(r['passed'] for r in records):raise SystemExit(1)
