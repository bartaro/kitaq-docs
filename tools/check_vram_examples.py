"""Build queue examples and verify both visible geometry and the reported queue units."""
from pathlib import Path
import json,hashlib,subprocess
from check_entity_callbacks import check_pixels
from check_api_tile_examples import read_png
from api_build_cleanup import cleanup_build_outputs
from api_vram_colors import matches_color
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUTPUT=SITE/'verification/api-vram'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def geometry_errors(image,platform,mode):
    width,height,channels,rows=read_png(image)
    background=rows[-1][:3]
    patterns={0:[0]*8,1:[255]*8,2:[240]*8,3:[128,192,224,240,248,252,254,255]}
    tiles={(2,2):1,(4,2):1,(18,10):1}
    tiles.update({(x,y):1 for y in range(4,7) for x in range(2,6)})
    tiles.update({(10+x,4+y):value for y,line in enumerate([[1,2,3],[3,0,2]]) for x,value in enumerate(line)})
    tiles.update({(2+x,8):value for x,value in enumerate([1,2,3])})
    tiles.update({(6+x,8):value for x,value in enumerate([2,3])})
    tiles.update({(10+x,8):1 for x in range(5)})
    errors=0;colors=0
    for y in range(16,88):
        for x in range(width):
            tile=tiles.get((x//8,y//8),0)
            expected=bool(patterns[tile][y%8] & (1<<(7-x%8)))
            ink=rows[y][x*channels:x*channels+3]!=background
            errors+=expected!=ink
            if expected:
                color='black' if platform=='gb' else 'white'
                if mode=='cgb':
                    tx,ty=x//8,y//8
                    if ty==2 or ty==10:color='red'
                    elif ty==8:color='red' if tx<5 else ('blue' if tx<8 else 'green')
                    else:color='blue' if tx<6 else 'green'
                colors+=not matches_color(rows[y][x*channels:x*channels+3],color)
    return errors,colors

records=[]
for platform,mode in [('gb','dmg'),('gb','cgb'),('fc','nrom')]:
    folder=OUTPUT/(platform+'-'+mode);folder.mkdir(parents=True,exist_ok=True)
    source=SITE/'samples/api-examples'/platform/'vram_queue_shapes.c'
    compiler=REPOS/('kitaq'+platform)/('kitaq'+platform+'.exe')
    library=REPOS/('kitaq'+platform)/'lib/vram.c'
    emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
    rom=folder/('example.gb' if platform=='gb' else 'example.nes');image=folder/'screen.png';report=folder/'runtime.json'
    for path in [rom,image,report]:path.unlink(missing_ok=True)
    command=[str(compiler),str(library),str(source),'-I',str(library.parent),'-I',str(SITE/'samples'),'-o',str(rom),'--no-cache','--no-disasm']
    command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb'] if platform=='gb' else ['--mapper=nrom','--nes-chr='+str(SITE/'samples/api-examples/fc/vram_shapes.chr')]
    process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
    (folder/'build.txt').write_bytes(process.stdout+process.stderr)
    row={'platform':platform,'mode':mode,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'library_sha256':sha(library),'compiler_sha256':sha(compiler),'build_command':command,'build_exit':process.returncode,'passed':False}
    support = ['samples/gb_tile_example.h','samples/gb_common.h','samples/font_gb.h','samples/vram_example_colors.h'] if platform=='gb' else ['samples/fc_common.h','samples/api-examples/fc/vram_shapes.chr']
    row['support_sha256']={file:sha(SITE/file) for file in support}
    row['library_header_sha256']=sha(library.with_suffix('.h'))
    if process.returncode==0:
        command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','180','--png',str(image),'--dump-report',str(report)] if platform=='gb' else [str(emulator),'run',str(rom),'--frames','180','--png',str(image),'--json',str(report)]
        process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
        (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
        row.update(runtime_exit=process.returncode,run_command=command,rom_sha256=sha(rom),emulator_sha256=sha(emulator))
        if process.returncode==0 and image.exists():
            state=json.loads(report.read_text(encoding='utf-8'))
            frames=state.get('frames',state.get('meta',{}).get('frames_executed'))
            if platform=='gb':
                state={k:state[k] for k in ['meta','cpu','video','stop_reason','unsupported_opcodes'] if k in state}
                report.write_text(json.dumps(state,indent=2),encoding='utf-8')
            cap,used,free=('032','007','025') if platform=='gb' else ('128','052','076')
            labels=[(1,0,'VRAM QUEUE SHAPES'),(1,11,'CAPACITY'),(16,11,cap),(1,12,'USED'),(16,12,used),(1,13,'FREE'),(16,13,free),(1,14,'AFTER FLUSH'),(16,14,'000'),(1,16,'FAILED CHECKS'),(16,16,'000')]
            labels += [(1,15,'OVERFLOW SEEN'),(16,15,'001')]
            counts=check_pixels(image,labels,platform);shapes,colors=geometry_errors(image,platform,mode)
            row.update(image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),expected_labels=labels,label_pixel_mismatches=counts,geometry_pixel_mismatches=shapes,geometry_color_mismatches=colors,frames=frames,passed=counts==0 and shapes==0 and colors==0 and frames==180)
    if row['passed']:cleanup_build_outputs(folder)
    records.append(row);print(platform,mode,'PASS' if row['passed'] else 'FAIL',flush=True)
(OUTPUT/'results.json').write_text(json.dumps({'records':records,'scope':'Visible tile geometry, retained-source update, discarded write, queue capacity units and immediate/VBlank flush paths. Real hardware is not tested.'},indent=2),encoding='utf-8')
if not all(r['passed'] for r in records):raise SystemExit(1)
