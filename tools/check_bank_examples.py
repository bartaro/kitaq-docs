"""Build banked API teaching programs and verify their displayed hexadecimal results."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from check_entity_callbacks import check_pixels
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--gb-compiler',type=Path,default=REPOS/'kitaqgb/kitaqgb.exe')
parser.add_argument('--fc-compiler',type=Path,default=REPOS/'kitaqfc/kitaqfc.exe')
parser.add_argument('--output',type=Path,default=SITE/'verification/api-bank')
args=parser.parse_args();output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
records=[]
for platform,mode in [('gb','dmg'),('gb','cgb'),('fc','mmc3')]:
    folder=output/(platform+'-'+mode);folder.mkdir(exist_ok=True)
    compiler=(args.gb_compiler if platform=='gb' else args.fc_compiler).resolve(strict=True)
    emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
    source=SITE/'samples/api-examples'/platform/'banked_data_calls.c'
    library=REPOS/('kitaq'+platform)/'lib'
    rom=folder/('example.gb' if platform=='gb' else 'example.nes');image=folder/'screen.png';runtime=folder/'runtime.json'
    for path in [rom,image,runtime]:path.unlink(missing_ok=True)
    command=[str(compiler),str(source),'-I',str(library),'-I',str(SITE/'samples'),'-o',str(rom),'--no-cache','--no-disasm']
    command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=64k'] if platform=='gb' else ['--mapper=mmc3','--nes-chr='+str(SITE/'samples/font.chr')]
    process=subprocess.run(command,cwd=folder,capture_output=True,timeout=90)
    (folder/'build.txt').write_bytes(process.stdout+process.stderr)
    supports=['samples/bank_example_checks.h']+(['samples/gb_tile_color_example.h','samples/gb_tile_example.h','samples/gb_common.h','samples/font_gb.h'] if platform=='gb' else ['samples/fc_common.h','samples/font.chr'])
    record=dict(platform=platform,mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),
                compiler_sha256=sha(compiler),build_command=command,build_exit=process.returncode,passed=False,
                support_sha256={p:sha(SITE/p) for p in supports},library_sha256={p:sha(library/p) for p in ['bank.h','bank.c']})
    if process.returncode==0:
        command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','240','--png',str(image),'--dump-report',str(runtime)] if platform=='gb' else [str(emulator),'run',str(rom),'--frames','240','--png',str(image),'--json',str(runtime)]
        process=subprocess.run(command,cwd=folder,capture_output=True,timeout=90)
        (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
        record.update(run_command=command,run_exit=process.returncode,rom_sha256=sha(rom),emulator_sha256=sha(emulator))
        if process.returncode==0:
            state=json.loads(runtime.read_text(encoding='utf-8'));frames=state.get('frames',state.get('meta',{}).get('frames_executed'))
            if platform=='gb':
                state={k:state[k] for k in ['meta','cpu','video','stop_reason','unsupported_opcodes'] if k in state}
                runtime.write_text(json.dumps(state,indent=2),encoding='utf-8')
            labels=[(1,0,'BANKED DATA CALLS'),(1,2,'BANK IN'),(15,2,'02'),(1,4,'BYTE HEX'),(15,4,'D3'),
                    (1,6,'WORD HEX'),(13,6,'5C7A'),(1,8,'CALL COUNT'),(15,8,'03' if platform=='gb' else '02'),
                    (1,10,'BANK OUT'),(15,10,'02'),(1,12,'FAILED CHECKS'),(15,12,'00'),(1,14,'FIRST FAILURE'),(15,14,'00')]
            errors=check_pixels(image,labels,platform)
            width,height,channels,rows=read_png(image);background=rows[-1][:3];color_errors=0
            for tx,ty,label in labels:
                for y in range(ty*8,ty*8+8):
                    for x in range(tx*8,(tx+len(label))*8):
                        rgb=rows[y][x*channels:x*channels+3]
                        if rgb!=background:color_errors+=not matches_color(rgb,'black' if mode=='dmg' else 'blue')
            record.update(image=image.relative_to(SITE).as_posix() if image.is_relative_to(SITE) else str(image),image_sha256=sha(image),
                          runtime_sha256=sha(runtime),frames=frames,expected_labels=labels,label_pixel_mismatches=errors,
                          color_pixel_mismatches=color_errors,passed=frames==240 and errors==0 and color_errors==0)
    records.append(record);print(platform,mode,'PASS' if record['passed'] else 'FAIL',flush=True)
    if record['passed']:cleanup_build_outputs(folder)
    (output/'results.json').write_text(json.dumps({'records':records,'scope':'Banked data values, callback counts and restored mapping on KOKURA and KUROSAKI; no physical-hardware claim.'},indent=2),encoding='utf-8')
if not all(r['passed'] for r in records):raise SystemExit(1)
