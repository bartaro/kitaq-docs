"""Verify scanline selection, color and visible rotation in the teaching ROM."""
from pathlib import Path
import hashlib, json, subprocess
from check_api_tile_examples import read_png
from check_entity_callbacks import check_pixels
from api_vram_colors import matches_color
from api_build_cleanup import cleanup_build_outputs

SITE = Path(__file__).resolve().parents[1]
REPOS = SITE.parents[1] / 'publish/github_20260912'
LIB = REPOS / 'kitaqgb/lib'
COMPILER = REPOS / 'kitaqgb/kitaqgb.exe'
EMU = REPOS / 'kokura/kokura-cli.exe'
SOURCE = SITE / 'samples/api-examples/gb/sprite_order_demo.c'
OUT = SITE / 'verification/api-sprite-order/example'
OUT.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def check_scene(image, mode, phase):
    labels = [(1,0,'SPRITE ORDER'),(1,6,'HIGH'),(6,6,'NORMAL'),
              (5,10,'0123456789AB'),(1,12,'PHASE'),(7,12,f'{phase:02}'),
              (1,15,'2 HIGH + 8 NORMAL')]
    label_errors = check_pixels(image, labels, 'gb')
    w,h,c,rows = read_png(image)
    assert (w,h) == (160,144)
    # Build the expected ten selected objects without calling the C algorithm.
    # Two priority-zero diamonds occupy two slots. Stable cyclic submission
    # order chooses eight priority-one squares from the twelve candidates.
    cyclic = list(range(phase,14)) + list(range(phase))
    selected = [n for n in cyclic if n < 12][:8]
    expected = {(x,y):0 for y in range(64,72) for x in range(160)}
    diamond = [0,0x18,0x3C,0x7E,0x7E,0x3C,0x18,0]
    square = [0,0x7E,0x7E,0x7E,0x7E,0x7E,0x7E,0]
    for x0,pattern,value in [(8,diamond,1),(20,diamond,1)]+[(40+8*n,square,3) for n in selected]:
        for dy,bits in enumerate(pattern):
            for dx in range(8):
                if bits & (0x80 >> dx): expected[x0+dx,64+dy] = value
    errors=[]
    for (x,y),value in expected.items():
        rgb=list(rows[y][x*c:x*c+3])
        okay=(rgb==[[255]*3,[172]*3,[82]*3,[0]*3][value]) if mode=='dmg' else matches_color(rgb,['white','red','green','blue'][value])
        if not okay: errors.append(dict(x=x,y=y,index=value,actual_rgb=rgb))
    return dict(expected_labels=labels,label_pixel_mismatches=label_errors,
                selected_squares=selected,sprite_pixels_checked=len(expected),
                sprite_pixel_mismatches=len(errors),first_mismatches=errors[:20])

records=[]
matrix=[('phase'+str(p),p,[],[120]) for p in (0,4,8)]
matrix += [('O0-phase4',4,['-O0'],[120]),('animated',None,[],[120,240])]
def save():
    (OUT/'results.json').write_text(json.dumps(dict(
        script_sha256=sha(Path(__file__)),records=records,
        passed=len(records)==12 and all(r['passed'] for r in records),
        scope='KOKURA DMG/CGB scanline selection, geometry, colors and foreground phase progression. Physical hardware untested.'
    ),indent=2),encoding='utf-8')
save()
for variant,phase,flags,frames_list in matrix:
    folder=OUT/variant;folder.mkdir(exist_ok=True)
    wrapper=folder/'example.c'
    wrapper.write_text(('' if phase is None else '#define SPRITE_ORDER_DEMO_PHASE '+str(phase)+'\n')+'#include "sprite_order_demo.c"\n',encoding='ascii')
    rom=folder/'example.gb'
    command=[str(COMPILER),str(wrapper),'-I',str(LIB),'-I',str(SITE/'samples'),'-I',str(SOURCE.parent),'-o',str(rom),
             '--no-cache','--no-disasm','--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb',*flags]
    run=subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
    (folder/'build.log').write_bytes(run.stdout+run.stderr)
    assert run.returncode==0,(run.stdout+run.stderr).decode(errors='replace')[-6000:]
    for mode in ['dmg','cgb']:
        for frames in frames_list:
            image=folder/(mode+'-'+str(frames)+'.png');report=folder/'runtime.json'
            command=[str(EMU),str(rom),'--hardware',mode,'--run-frames',str(frames),'--png',str(image),
                     '--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview',
                     '--watch-window','state:0xC700:4']
            run=subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
            assert run.returncode==0,run.stderr
            data=json.loads(report.read_text(encoding='utf-8'))
            status=data['watched_memory'][0]['preview_bytes'];observed=status[0]
            assert status[1:]==[14,14,165] and observed<14,status
            if phase is not None:assert observed==phase,status
            result=check_scene(image,mode,observed)
            row=dict(variant=variant,mode=mode,frames=frames,state=status,
                     source=SOURCE.relative_to(SITE).as_posix(),source_sha256=sha(SOURCE),
                     wrapper=wrapper.relative_to(SITE).as_posix(),wrapper_sha256=sha(wrapper),
                     support_sha256={p:sha(SITE/p) for p in ['samples/gb_tile_example.h','samples/gb_common.h','samples/font_gb.h']},
                     library_sha256={p:sha(LIB/p) for p in ['sprite_order.c','sprite_order.h','sprite.c','sprite.h']},
                     compiler_sha256=sha(COMPILER),emulator_sha256=sha(EMU),
                     rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),
                     image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),**result)
            row['passed']=data['meta']['frames_executed']==frames and result['label_pixel_mismatches']==0 and result['sprite_pixel_mismatches']==0
            records.append(row);save()
            print(variant,mode,frames,status,'PASS' if row['passed'] else 'FAIL',result['label_pixel_mismatches'],result['sprite_pixel_mismatches'],flush=True)
            assert row['passed'],result['first_mismatches']
            report.unlink()
    cleanup_build_outputs(folder)
for mode in ['dmg','cgb']:
    moving=[r for r in records if r['variant']=='animated' and r['mode']==mode]
    assert moving[0]['state'][0]!=moving[1]['state'][0]
    assert moving[0]['selected_squares']!=moving[1]['selected_squares']
save()
