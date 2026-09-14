"""Verify bank-separated asset descriptors, copied bytes and visible tile uploads."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from check_api_tile_examples import read_png
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs
from api_vram_colors import matches_color

SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUTPUT=SITE/'verification/api-asset'
parser=argparse.ArgumentParser()
parser.add_argument('--platform',choices=['gb','fc'])
parser.add_argument('--gb-compiler',type=Path)
parser.add_argument('--fc-compiler',type=Path)
parser.add_argument('--output',type=Path)
args=parser.parse_args()
if args.output:OUTPUT=args.output.resolve()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def geometry_errors(image,platform,mode):
    width,height,channels,rows=read_png(image)
    background=rows[-1][:3]
    masks=[[128,192,224,240,248,252,254,255],[255,129,129,129,129,129,129,255],[240]*8]
    shapes=colors=0
    for top,count,color in [(32,9,'red'),(64,2,'blue'),(96,2,'green')]:
        for y in range(top,top+8):
            for x in range(16,16+count*8):
                tile=(x-16)//8;ink=bool(masks[tile%3][y-top] & (1<<(7-x%8)))
                pixel=rows[y][x*channels:x*channels+3]
                actual=pixel!=background
                shapes+=ink!=actual
                if ink:colors+=not matches_color(pixel,'black' if platform=='gb' and mode=='dmg' else color)
    return shapes,colors

records=[]
for platform,mode in [('gb','dmg'),('gb','cgb'),('fc','surom512')]:
    if args.platform and args.platform!=platform:continue
    folder=OUTPUT/(platform+'-'+mode);folder.mkdir(parents=True,exist_ok=True)
    source=SITE/('samples/api-examples/'+platform+'/asset_banks.c')
    compiler=REPOS/('kitaq'+platform)/('kitaq'+platform+'.exe')
    compiler=(getattr(args,platform+'_compiler') or compiler).resolve()
    emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
    rom=folder/('example.gb' if platform=='gb' else 'example.nes');image=folder/'screen.png';report=folder/'runtime.json'
    for path in [rom,image,report]:path.unlink(missing_ok=True)
    command=[str(compiler),str(source),'-I',str(REPOS/('kitaq'+platform)/'lib'),'-I',str(SITE/'samples'),'-o',str(rom),'--no-cache','--no-disasm']
    if platform=='gb':command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=64k']
    else:command+=['--mapper=mmc1','--board=surom512']
    process=subprocess.run(command,capture_output=True,timeout=120,cwd=folder)
    (folder/'build.txt').write_bytes(process.stdout+process.stderr)
    supports=['samples/asset_example_checks.h','samples/asset_example_data_'+platform+'.h','samples/font_gb.h']
    supports += ['samples/gb_tile_example.h','samples/gb_common.h','samples/vram_example_colors.h'] if platform=='gb' else ['samples/fc_common.h']
    row={'platform':platform,'mode':mode,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'compiler_sha256':sha(compiler),'build_command':command,'build_exit':process.returncode,'passed':False,'support_sha256':{name:sha(SITE/name) for name in supports},'library_sha256':{name:sha(REPOS/('kitaq'+platform)/'lib'/name) for name in (['asset.h','asset.c'] if platform=='gb' else ['asset.h','asset.c','bank.h','bank.c'])}}
    if process.returncode==0:
        command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','300','--png',str(image),'--dump-report',str(report)] if platform=='gb' else [str(emulator),'run',str(rom),'--frames','300','--png',str(image),'--json',str(report)]
        process=subprocess.run(command,capture_output=True,timeout=120,cwd=folder)
        (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
        row.update(runtime_exit=process.returncode,run_command=command,rom_sha256=sha(rom),emulator_sha256=sha(emulator))
        if process.returncode==0 and image.exists():
            state=json.loads(report.read_text(encoding='utf-8'))
            frames=state.get('frames',state.get('meta',{}).get('frames_executed'))
            if platform=='gb':
                state={key:state[key] for key in ['meta','cpu','video','stop_reason','unsupported_opcodes'] if key in state}
                report.write_text(json.dumps(state,indent=2),encoding='utf-8')
            row.update(frames=frames,runtime_sha256=sha(report))
            labels=[(1,0,'ASSET BANKS'),(1,3,'TILE ASSET 144B'),(1,15,'FAILED CHECKS'),(1,17,'FIRST FAILURE')]
            labels += [(6,8,'FARMEMCPY' if platform=='gb' else 'FAR_MEMCPY'),(6,12,'FAR_MEMCPY' if platform=='gb' else 'LOAD RAW'),(16 if platform=='gb' else 20,15,'000'),(16 if platform=='gb' else 20,17,'00')]
            errors=check_pixels(image,labels,platform);shapes,colors=geometry_errors(image,platform,mode)
            image_name=image.relative_to(SITE).as_posix() if image.is_relative_to(SITE) else str(image)
            row.update(image=image_name,image_sha256=sha(image),expected_labels=labels,label_pixel_mismatches=errors,geometry_pixel_mismatches=shapes,geometry_color_mismatches=colors,passed=frames==300 and errors==0 and shapes==0 and colors==0)
    if row['passed']:cleanup_build_outputs(folder)
    records.append(row);print(platform,mode,'PASS' if row['passed'] else 'FAIL',flush=True)
(OUTPUT/'results.json').write_text(json.dumps({'records':records,'scope':'Separate table/payload banks, lookup/error/truncation/empty cases, bank restoration and actual tile patterns. Emulator execution only.'},indent=2),encoding='utf-8')
if not all(row['passed'] for row in records):raise SystemExit(1)
