"""Check palette boundaries and actual colored/monochrome attribute geometry."""
from pathlib import Path
import hashlib
import json
import subprocess
from check_api_tile_examples import read_png
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs
from api_vram_colors import matches_color

SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists(): REPOS=SITE.parent
OUTPUT=SITE/'verification/api-cgb-palette'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def pixel_errors(image,mode):
    width,height,channels,rows=read_png(image)
    assert (width,height)==(160,144)
    # Start with an empty canvas for the three isolated bands; text is checked separately.
    expected={}
    bg=['red','blue','green','red','blue','green','red']
    obj=['blue','green','red','blue','green','red','blue']
    triangle=[128,192,224,240,248,252,254,255]
    ring=[255,129,129,129,129,129,129,255]
    def tile(x,y,pattern,color,xflip=False,yflip=False):
        for dy in range(8):
            bits=pattern[7-dy if yflip else dy]
            for dx in range(8):
                if bits & (1 << (dx if xflip else 7-dx)):
                    expected[x+dx,y+dy]=color if mode=='cgb' else 'black'
    for i in range(7):
        tile(16+i*16,24,triangle,bg[i])
        tile(16+i*16,64,triangle,obj[i])
    tile(16,88,triangle,'red')
    tile(32,88,ring if mode=='cgb' else triangle,'blue')
    tile(48,88,triangle,'green',xflip=mode=='cgb')
    tile(64,88,triangle,'red',yflip=mode=='cgb')
    tile(80,88,triangle,'blue',xflip=mode=='cgb',yflip=mode=='cgb')
    tile(96,88,[255]*8,'red')
    if mode=='cgb': tile(96,88,triangle,'green')
    tile(112,88,[255]*8,'red')
    shape_errors=color_errors=0
    for top in [24,64,88]:
        for y in range(top,top+8):
            for x in range(160):
                color=expected.get((x,y),'white')
                pixel=rows[y][x*channels:x*channels+3]
                shape_errors+=(color=='white')!=matches_color(pixel,'white')
                color_errors+=not matches_color(pixel,color)
    return shape_errors,color_errors

records=[]
for target,mode in [('cgb','dmg'),('cgb','cgb'),('dmg','dmg'),('cgb_only','cgb')]:
    folder=OUTPUT/(target+'-'+mode); folder.mkdir(parents=True,exist_ok=True)
    source=SITE/'samples/api-examples/gb/cgb_palette_attributes.c'
    compiler=REPOS/'kitaqgb/kitaqgb.exe'; emulator=REPOS/'kokura/kokura-cli.exe'
    rom=folder/'example.gb'; image=folder/'screen.png'; report=folder/'runtime.json'
    for path in [rom,image,report]: path.unlink(missing_ok=True)
    command=[str(compiler),str(source),'-I',str(REPOS/'kitaqgb/lib'),'-I',str(SITE/'samples'),'-o',str(rom),'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb='+target,'--no-cache','--no-disasm']
    process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
    (folder/'build.txt').write_bytes(process.stdout+process.stderr)
    row={'platform':'gb','target':target,'mode':mode,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'compiler_sha256':sha(compiler),'build_command':command,'build_exit':process.returncode,'passed':False,
         'support_sha256':{name:sha(SITE/name) for name in ['samples/gb_tile_example.h','samples/gb_common.h','samples/font_gb.h']},
         'library_sha256':{name:sha(REPOS/'kitaqgb/lib'/name) for name in ['cgb_palette.h','cgb_palette.c','cgb_tile.h']}}
    if process.returncode==0:
        command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','240','--png',str(image),'--dump-report',str(report)]
        process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
        (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
        row.update(runtime_exit=process.returncode,run_command=command,rom_sha256=sha(rom),emulator_sha256=sha(emulator))
        if process.returncode==0 and image.exists():
            state=json.loads(report.read_text(encoding='utf-8'));frames=state['meta']['frames_executed']
            state={key:state[key] for key in ['meta','cpu','video','stop_reason','unsupported_opcodes'] if key in state}
            report.write_text(json.dumps(state,indent=2),encoding='utf-8')
            labels=[(1,0,'CGB PALETTE / ATTR'),(1,2,'BG 1 2 3 4 5 6 7'),(1,6,'OBJ 1 2 3 4 5 6 7'),(1,10,'PAL BANK X Y XY PRI'),(1,13,'CGB MODE'),(16,13,'1' if mode=='cgb' else '0'),(1,15,'FAILED CHECKS'),(16,15,'000')]
            label_errors=check_pixels(image,labels,'gb')
            shape_errors,color_errors=pixel_errors(image,mode)
            row.update(image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),expected_labels=labels,label_pixel_mismatches=label_errors,geometry_pixel_mismatches=shape_errors,geometry_color_mismatches=color_errors,frames=frames,passed=label_errors==0 and shape_errors==0 and color_errors==0 and frames==240)
    if row['passed']: cleanup_build_outputs(folder)
    records.append(row)
    print(target,mode,'PASS' if row['passed'] else 'FAIL',flush=True)
(OUTPUT/'results.json').write_text(json.dumps({'records':records,'scope':'Four compiler-target/hardware combinations. RGB and attribute masks, palette slot wrapping, crossing, end clamping, null/empty sources, BG/OBJ independence and drawn pixel geometry/colors. LCD-off setup only; real hardware and LCD-on contention are not tested.'},indent=2),encoding='utf-8')
if not all(row['passed'] for row in records): raise SystemExit(1)
