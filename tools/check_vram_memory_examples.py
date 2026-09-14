"""Verify the immediate GB VRAM intrinsics through bytes and actual tile geometry."""
from pathlib import Path
import argparse,json,hashlib,subprocess
from check_entity_callbacks import check_pixels
from check_api_tile_examples import read_png
from api_build_cleanup import cleanup_build_outputs
from api_vram_colors import matches_color
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUTPUT=SITE/'verification/api-vram-memory'
parser=argparse.ArgumentParser()
parser.add_argument('--keep-build-metadata',action='store_true')
args=parser.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def geometry_errors(image,mode):
 width,height,channels,rows=read_png(image);background=rows[-1][:3]
 patterns={0:[0]*8,1:[255]*8,2:[240]*8,3:[128,192,224,240,248,252,254,255]}
 tiles={(2+x,y):x+1 for y in range(2,7) for x in range(3)}
 tiles.update({(x,y):1 for y in range(7,11) for x in range(2,5)})
 tiles.update({(2,11):1,(2,12):1,(4,12):1})
 errors=0;colors=0
 for y in range(16,104):
  for x in range(56):
   expected=bool(patterns[tiles.get((x//8,y//8),0)][y%8] & (1<<(7-x%8)))
   ink=rows[y][x*channels:x*channels+3]!=background
   errors+=expected!=ink
   if expected:
    color='black'
    if mode=='cgb':
     tile_y=y//8;tile_x=x//8
     palette=(tile_y-2)%3+1 if tile_y<=10 else (1 if tile_y==11 else (2 if tile_x==2 else 3))
     color={1:'red',2:'blue',3:'green'}[palette]
    colors+=not matches_color(rows[y][x*channels:x*channels+3],color)
 return errors,colors
records=[]
for mode in ['dmg','cgb']:
 folder=OUTPUT/mode;folder.mkdir(parents=True,exist_ok=True)
 source=SITE/'samples/api-examples/gb/vram_memory_shapes.c'
 compiler=REPOS/'kitaqgb/kitaqgb.exe';emulator=REPOS/'kokura/kokura-cli.exe'
 rom=folder/'example.gb';image=folder/'screen.png';report=folder/'runtime.json'
 for path in [rom,image,report]:path.unlink(missing_ok=True)
 command=[str(compiler),str(source),'-I',str(REPOS/'kitaqgb/lib'),'-I',str(SITE/'samples'),'-o',str(rom),'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--no-cache','--no-disasm']
 process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
 (folder/'build.txt').write_bytes(process.stdout+process.stderr)
 row={'platform':'gb','mode':mode,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'compiler_sha256':sha(compiler),'build_command':command,'build_exit':process.returncode,'passed':False,
 'support_sha256':{name:sha(SITE/name) for name in ['samples/gb_tile_example.h','samples/gb_common.h','samples/font_gb.h','samples/vram_example_colors.h']}}
 if process.returncode==0:
  command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','180','--png',str(image),'--dump-report',str(report)]
  process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
  (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
  row.update(runtime_exit=process.returncode,run_command=command,rom_sha256=sha(rom),emulator_sha256=sha(emulator))
  if process.returncode==0 and image.exists():
   state=json.loads(report.read_text(encoding='utf-8'));frames=state['meta']['frames_executed']
   state={k:state[k] for k in ['meta','cpu','video','stop_reason','unsupported_opcodes'] if k in state}
   report.write_text(json.dumps(state,indent=2),encoding='utf-8')
   labels=[(1,0,'VRAM MEMORY SHAPES'),(1,15,'FAILED CHECKS'),(16,15,'000')]
   labels += [(7,y,label) for y,label in enumerate(['MEMCPY','COPY','HBLANK','DMA','COPY UNSAFE','MEMSET','FILL','FILL TILEMAP','FILL UNSAFE','ZERO COUNT','LCD ON'],2)]
   label_errors=check_pixels(image,labels,'gb');shape_errors,color_errors=geometry_errors(image,mode)
   row.update(image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),expected_labels=labels,label_pixel_mismatches=label_errors,geometry_pixel_mismatches=shape_errors,geometry_color_mismatches=color_errors,frames=frames,passed=label_errors==0 and shape_errors==0 and color_errors==0 and frames==180)
 if row['passed'] and not args.keep_build_metadata:cleanup_build_outputs(folder)
 records.append(row);print(mode,'PASS' if row['passed'] else 'FAIL',flush=True)
(OUTPUT/'results.json').write_text(json.dumps({'records':records,'scope':'Immediate copies/fills, runtime and constant counts, retained fill values across length evaluation, zero-count sentinels and LCD-on safe writes. Real hardware not tested.'},indent=2),encoding='utf-8')
if not all(r['passed'] for r in records):raise SystemExit(1)
