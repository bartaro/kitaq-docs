"""Check real sprite colors, flips, compositing, hidden slots and scanline limits."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from check_api_tile_examples import read_png
from check_entity_callbacks import check_pixels
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--fc-compiler',type=Path,default=REPOS/'kitaqfc/kitaqfc.exe')
parser.add_argument('--output',type=Path,default=SITE/'verification/api-sprite')
args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
patterns=json.loads((SITE/'samples/sprite_example_shapes.json').read_text(encoding='utf-8'))['patterns']
records=[]
for platform,mode in [('gb','dmg'),('gb','cgb'),('fc','ntsc')]:
    folder=out/(platform+'-'+mode);folder.mkdir(exist_ok=True)
    source=SITE/'samples/api-examples'/platform/'sprite_shapes.c';library=REPOS/('kitaq'+platform)/'lib'
    compiler=(REPOS/'kitaqgb/kitaqgb.exe' if platform=='gb' else args.fc_compiler).resolve(strict=True)
    emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
    rom=folder/('example.gb' if platform=='gb' else 'example.nes');image=folder/'screen.png';runtime=folder/'runtime.json'
    for path in [rom,image,runtime]:path.unlink(missing_ok=True)
    command=[str(compiler),str(source),'-I',str(library),'-I',str(SITE/'samples'),'--no-cache','--no-disasm','-o',str(rom)]
    command+=['--cgb=cgb','--profile=dev','--rst-disable','--stack-bank=fixed'] if platform=='gb' else ['--nes-chr='+str(SITE/'samples/sprite_example.chr')]
    run=subprocess.run(command,cwd=folder,capture_output=True,timeout=90);(folder/'build.txt').write_bytes(run.stdout+run.stderr)
    supports=['samples/sprite_example_checks.h','samples/sprite_example_shapes.json']+(['samples/gb_tile_example.h','samples/gb_common.h','samples/font_gb.h','samples/sprite_example_tiles.h'] if platform=='gb' else ['samples/fc_common.h','samples/sprite_example.chr'])
    row=dict(platform=platform,mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),
        support_sha256={p:sha(SITE/p) for p in supports},library_sha256={p:sha(library/p) for p in ['sprite.c','sprite.h']},
        compiler_sha256=sha(compiler),build_command=command,build_exit=run.returncode,passed=False)
    if run.returncode==0:
        command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','240','--png',str(image),'--dump-report',str(runtime)] if platform=='gb' else [str(emulator),'run',str(rom),'--frames','240','--png',str(image),'--json',str(runtime)]
        run=subprocess.run(command,cwd=folder,capture_output=True,timeout=90);(folder/'runtime.txt').write_bytes(run.stdout+run.stderr)
        row.update(run_exit=run.returncode,run_command=command,rom_sha256=sha(rom),emulator_sha256=sha(emulator))
        if run.returncode==0:
            state=json.loads(runtime.read_text(encoding='utf-8'));frames=state.get('frames',state.get('meta',{}).get('frames_executed'))
            if platform=='gb':
                state={k:state[k] for k in ['meta','cpu','video','unsupported_opcodes','stop_reason'] if k in state}
                runtime.write_text(json.dumps(state,indent=2),encoding='utf-8')
            labels=[(1,0,'SPRITE EXAMPLE'),(17,0,'00'),(1,2,'NORMAL'),(1,4,'FLIP X'),(1,6,'FLIP Y'),
                    (1,8,'META'),(1,10,'OVERLAP'),(1,12,'ANIMATION'),(1,14,'SCAN LIMIT')]
            text_errors=check_pixels(image,labels,platform)
            w,h,c,rows=read_png(image);assert (w,h)==((160,144) if platform=='gb' else (256,240))
            expected={}
            # Restrict the comparison to sprite fields and deliberately empty hidden-slot fields.
            for x0,y0,x1,y1 in [(80,16,112,112),(120,16,128,24),(120,32,128,40),(0,128,112,136)]:
                for y in range(y0,y1):
                    for x in range(x0,x1):expected[x,y]=0
            def draw(tx,ty,tile,flipx=False,flipy=False):
                for dy in range(8):
                    for dx in range(8):
                        value=int(patterns[tile][7-dy if flipy else dy][7-dx if flipx else dx])
                        if value:expected[tx+dx,ty+dy]=value
            draw(88,16,0);draw(88,32,0,True);draw(88,48,0,False,True)
            draw(88,64,0);draw(96,64,0,True)
            draw(92,80,1);draw(88,80,0);draw(88,96,1)
            for i in range(10 if platform=='gb' else 8):draw(8+8*i,128,0)
            errors=[]
            for (x,y),value in expected.items():
                rgb=list(rows[y][x*c:x*c+3])
                if mode=='dmg':
                    # KOKURA maps DMG shades to RGB555 levels 31, 21, 10, 0,
                    # then exports each channel as floor(level * 255 / 31).
                    luminance=[255,172,82,0][value]
                    okay=rgb==[luminance]*3
                elif value==0:okay=matches_color(rgb,'white' if platform=='gb' else 'black')
                else:okay=matches_color(rgb,['','red','green','blue'][value])
                if not okay:errors.append({'x':x,'y':y,'index':value,'actual_rgb':rgb})
            row.update(frames=frames,image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),runtime_sha256=sha(runtime),
                expected_labels=labels,label_pixel_mismatches=text_errors,sprite_pixels_checked=len(expected),
                sprite_pixel_mismatches=len(errors),first_mismatches=errors[:20],passed=frames==240 and text_errors==0 and not errors)
        if row['passed']:cleanup_build_outputs(folder)
    records.append(row);print(platform,mode,'PASS' if row['passed'] else 'FAIL',row.get('label_pixel_mismatches'),row.get('sprite_pixel_mismatches'),flush=True)
    (out/'results.json').write_text(json.dumps({'records':records,'scope':'Actual emulator sprite geometry, color, flips, overlap, hidden slots, animation and per-line selection limits; physical hardware untested.'},indent=2),encoding='utf-8')
raise SystemExit(0 if all(r['passed'] for r in records) else 1)
