"""Run the packed-bit teaching ROMs and check every displayed result and ink color."""
from pathlib import Path
import hashlib,json,subprocess
from check_entity_callbacks import check_pixels
from check_api_tile_examples import read_png
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs

SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUTPUT=SITE/'verification/api-bit-intrinsics'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for platform,mode in [('gb','dmg'),('gb','cgb'),('fc','nrom')]:
    folder=OUTPUT/(platform+'-'+mode);folder.mkdir(parents=True,exist_ok=True)
    compiler=REPOS/('kitaq'+platform)/('kitaq'+platform+'.exe')
    emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
    library=REPOS/('kitaq'+platform)/'lib'
    source=SITE/'samples/api-examples'/platform/'bit_intrinsics.c'
    rom=folder/('example.gb' if platform=='gb' else 'example.nes');image=folder/'screen.png';runtime=folder/'runtime.json'
    for path in [rom,image,runtime]:path.unlink(missing_ok=True)
    command=[str(compiler),str(source),'-I',str(library),'-I',str(SITE/'samples'),'-o',str(rom),'--no-cache','--no-disasm']
    command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb'] if platform=='gb' else ['--mapper=nrom','--nes-chr='+str(SITE/'samples/font.chr')]
    process=subprocess.run(command,cwd=folder,capture_output=True,timeout=90)
    (folder/'build.txt').write_bytes(process.stdout+process.stderr)
    supports=['samples/bit_example_checks.h']+(['samples/gb_tile_color_example.h','samples/gb_tile_example.h','samples/gb_common.h','samples/font_gb.h'] if platform=='gb' else ['samples/fc_common.h','samples/font.chr'])
    row=dict(platform=platform,mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),build_exit=process.returncode,passed=False,support_sha256={p:sha(SITE/p) for p in supports},header_sha256=sha(library/('rpg.h' if platform=='gb' else 'intrinsics.h')))
    if process.returncode==0:
        command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','240','--png',str(image),'--dump-report',str(runtime)] if platform=='gb' else [str(emulator),'run',str(rom),'--frames','240','--png',str(image),'--json',str(runtime)]
        process=subprocess.run(command,cwd=folder,capture_output=True,timeout=90)
        (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
        row.update(runtime_exit=process.returncode,rom_sha256=sha(rom))
        if process.returncode==0:
            state=json.loads(runtime.read_text(encoding='utf-8'));frames=state.get('frames',state.get('meta',{}).get('frames_executed'))
            if platform=='gb':
                state={k:state[k] for k in ['meta','cpu','video','stop_reason','unsupported_opcodes'] if k in state}
                runtime.write_text(json.dumps(state,indent=2),encoding='utf-8')
            labels=[(1,0,'PACKED BIT FLAGS')]
            for y,text,value in [(2,'TEST OFF','000'),(4,'TEST ON','001' if platform=='gb' else '128'),(6,'SET BIT1','166'),(8,'CLEAR BIT2','162'),(10,'TOGGLE BIT7','034'),(12,'RESTORE','162'),(14,'NEXT BYTE','130'),(16,'FAILED','000')]:
                labels.extend([(1,y,text),(16 if platform=='gb' else 27,y,value)])
            errors=check_pixels(image,labels,platform)
            width,height,channels,rows=read_png(image);background=rows[-1][:3];color_errors=0;colored_pixels=0
            for pixels in rows:
                for x in range(width):
                    rgb=pixels[x*channels:x*channels+3]
                    if rgb!=background:
                        colored_pixels+=1;color_errors+=not matches_color(rgb,'black' if mode=='dmg' else 'blue')
            unsafe=state.get('ppu',{}).get('data_writes_while_rendering',0)
            row.update(image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),frames=frames,expected_labels=labels,label_pixel_mismatches=errors,color_mismatches=color_errors,colored_pixels=colored_pixels,ppu_writes_while_rendering=unsafe,passed=frames==240 and errors==0 and color_errors==0 and colored_pixels>0 and unsafe==0)
    records.append(row)
    if row['passed']:cleanup_build_outputs(folder)
    (OUTPUT/'results.json').write_text(json.dumps({'records':records,'scope':'RAM contents and guards plus displayed values on emulators; no physical-hardware claim.'},indent=2),encoding='utf-8')
    print(platform,mode,'PASS' if row['passed'] else 'FAIL',flush=True)
raise SystemExit(0 if all(r['passed'] for r in records) else 1)
