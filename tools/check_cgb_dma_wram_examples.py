"""Execute DMA/WRAM examples and verify colored geometry and compiler diagnostics."""
from pathlib import Path
import hashlib,json,subprocess
from check_api_tile_examples import read_png
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs
from api_vram_colors import matches_color

SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists(): REPOS=SITE.parent
OUTPUT=SITE/'verification/api-cgb-dma-wram'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def geometry_errors(image,program,mode):
    width,height,channels,rows=read_png(image)
    assert (width,height)==(160,144)
    patterns={'triangle':[128,192,224,240,248,252,254,255], 'outline':[255,129,129,129,129,129,129,255], 'half':[240]*8,'solid':[255]*8}
    expected={}
    def tile(x,y,pattern,color):
        for dy,bits in enumerate(patterns[pattern]):
            for dx in range(8):
                if bits & (1<<(7-dx)): expected[x+dx,y+dy]=color if mode=='cgb' else 'black'
    if program=='cgb_dma_shapes':
        if mode=='cgb':
            tile(16,24,'triangle','red');tile(24,24,'outline','red')
            tile(16,48,'half','blue');tile(24,48,'solid','blue')
        tile(16,72,'half','green');tile(24,72,'solid','green')
        tops=[24,48,72]
    else:
        tile(16,24,'solid','red');tile(16,48,'outline','blue');tops=[24,48]
    shapes=colors=0
    for top in tops:
        for y in range(top,top+8):
            for x in range(40):
                expected_color=expected.get((x,y),'white');pixel=rows[y][x*channels:x*channels+3]
                shapes+=(expected_color=='white')!=matches_color(pixel,'white')
                colors+=not matches_color(pixel,expected_color)
    return shapes,colors

records=[]
for program,target,mode in [('cgb_dma_shapes','cgb','dmg'),('cgb_dma_shapes','cgb','cgb'),('cgb_dma_shapes','cgb_only','cgb'),('cgb_wram_banks','cgb_only','cgb')]:
    folder=OUTPUT/(program+'-'+target+'-'+mode);folder.mkdir(parents=True,exist_ok=True)
    source=SITE/('samples/api-examples/gb/'+program+'.c')
    compiler=REPOS/'kitaqgb/kitaqgb.exe';emulator=REPOS/'kokura/kokura-cli.exe'
    rom=folder/'example.gb';image=folder/'screen.png';report=folder/'runtime.json'
    for path in [rom,image,report]:path.unlink(missing_ok=True)
    command=[str(compiler),str(source),'-I',str(REPOS/'kitaqgb/lib'),'-I',str(SITE/'samples'),'-o',str(rom),'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb='+target,'--no-cache','--no-disasm']
    process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
    (folder/'build.txt').write_bytes(process.stdout+process.stderr)
    row={'platform':'gb','id':program,'target':target,'mode':mode,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'compiler_sha256':sha(compiler),'build_command':command,'build_exit':process.returncode,'passed':False,
         'support_sha256':{name:sha(SITE/name) for name in ['samples/gb_tile_example.h','samples/gb_common.h','samples/font_gb.h','samples/vram_example_colors.h']}}
    if process.returncode==0:
        command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','240','--png',str(image),'--dump-report',str(report)]
        process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
        (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
        row.update(runtime_exit=process.returncode,run_command=command,rom_sha256=sha(rom),emulator_sha256=sha(emulator))
        if process.returncode==0 and image.exists():
            state=json.loads(report.read_text(encoding='utf-8'));frames=state['meta']['frames_executed']
            state={key:state[key] for key in ['meta','cpu','video','stop_reason','unsupported_opcodes'] if key in state}
            report.write_text(json.dumps(state,indent=2),encoding='utf-8')
            labels=[(1,15,'FAILED CHECKS'),(16,15,'000')]
            if program=='cgb_dma_shapes':labels += [(1,0,'CGB DMA SHAPES'),(6,3,'GDMA 32B'),(6,6,'HDMA 32B'),(6,9,'CANCELED'),(1,12,'CGB MODE'),(16,12,'0' if mode=='dmg' else '1')]
            else:labels += [(1,0,'CGB WRAM BANKS'),(5,3,'BANK 2 = 1'),(5,6,'BANK 3 = 2'),(1,10,'RESTORED BANK 1')]
            label_errors=check_pixels(image,labels,'gb');shapes,colors=geometry_errors(image,program,mode)
            row.update(image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),expected_labels=labels,label_pixel_mismatches=label_errors,geometry_pixel_mismatches=shapes,geometry_color_mismatches=colors,frames=frames,passed=label_errors==0 and shapes==0 and colors==0 and frames==240)
    if row['passed']:cleanup_build_outputs(folder)
    records.append(row);print(program,target,mode,'PASS' if row['passed'] else 'FAIL',flush=True)
(OUTPUT/'results.json').write_text(json.dumps({'records':records,'scope':'Real ROM output in KOKURA: GDMA, HBlank completion, cancellation before first block, target/DMG guards, WRAM bank isolation and prior-bank return for dynamic arguments. Hardware timing, partial cancellation, all DMA lengths and double-speed execution are not tested.'},indent=2),encoding='utf-8')
if not all(row['passed'] for row in records):raise SystemExit(1)
