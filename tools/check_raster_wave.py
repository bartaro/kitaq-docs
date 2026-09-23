"""Compare every rendered scanline with an independent original tile-map model.

Only standard-library PNG decoding is used. Captures at consecutive frames
must advance exactly one wave phase; a successful build alone is not a pass.
"""
from pathlib import Path
import hashlib, json, math, re, subprocess
from check_api_tile_examples import read_png

SITE = Path(__file__).resolve().parents[1]
ROOT = SITE.parents[1]
REPOS = ROOT / 'publish/github_20260912'
OUT = SITE / 'verification/api-raster-wave'
SOURCE = SITE / 'samples/api-examples/gb/raster_wave.c'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def run(args, log):
    result = subprocess.run(list(map(str, args)), capture_output=True, timeout=180)
    log.write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(str(log))

def reference_rows(title=False):
    text = (SITE / 'samples/font_gb.h').read_text(encoding='utf-8')
    font = [int(v, 0) for v in re.findall(r'0x[0-9a-fA-F]+|\d+', text[text.index('{')+1:text.index('}')])]
    tilemap = [[128 if x % 4 == 0 else 0 for x in range(32)] for y in range(18)]
    labels = [(3,4,'ORBIT GUARD'), (4,8,'TITLE ARRIVAL'), (4,12,'PRESS START')] if title else [(3,4,'SCANLINE WAVE'), (4,8,'BOSS APPROACH'), (4,12,'WARP CORRIDOR')]
    for x, y, label in labels:
        tilemap[y][x:x+len(label)] = list(map(ord, label))
    rows = []
    for y in range(144):
        row = []
        for tile in tilemap[y//8]:
            low, high = (0x38,0x38) if tile == 128 else font[tile*16+(y%8)*2:tile*16+(y%8)*2+2]
            row += [bool((low | high) & (128 >> x)) for x in range(8)]
        rows.append(row)
    return rows

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    compiler = REPOS / 'kitaqgb/kitaqgb.exe'
    emulator = REPOS / 'kokura/kokura-cli.exe'
    library = REPOS / 'kitaqgb/lib'
    rom = OUT / 'raster_wave.gb'
    run([compiler, SOURCE, '-I', library, '-I', SITE/'samples', '-o', rom,
         '--profile=dev', '--rst-disable', '--stack-bank=fixed', '--cgb=cgb',
         '--no-cache', '--no-disasm'], OUT/'build.txt')
    background = reference_rows()
    offsets = [round(24*math.sin(2*math.pi*i/64)) for i in range(64)]
    records = []
    for mode in ['dmg','cgb']:
        for frames in [60,61,68,76,84,92,100,108,116]:
            stem = mode+'-'+str(frames)
            png = OUT/(stem+'.png'); report = OUT/(stem+'.json')
            run([emulator,rom,'--hardware',mode,'--run-frames',frames,'--png',png,
                 '--dump-report',report,'--report-sections','meta,watched_memory',
                 '--watch-window','frames:0xC600:2','--watch-fields','preview'], OUT/(stem+'.txt'))
            state = json.loads(report.read_text(encoding='utf-8'))
            count = state['watched_memory'][0]['preview_bytes'][0]
            assert state['watched_memory'][0]['preview_bytes'][1] == 17
            width,height,channels,rows = read_png(png)
            assert (width,height)==(160,144)
            pixels = [[tuple(row[x*channels:x*channels+3]) for x in range(160)] for row in rows]
            paper = max(set(sum(pixels,[])), key=sum(pixels,[]).count)
            mask = [[rgb != paper for rgb in row] for row in pixels]
            scores = []
            for phase in range(64):
                scores.append(sum(mask[y][x] != background[y][(x+offsets[(y+phase)%64])%256]
                                  for y in range(144) for x in range(160)))
            phase = scores.index(min(scores))
            colored = sum(r!=g or g!=b for row in pixels for r,g,b in row)
            entry = dict(mode=mode, frames=frames, completed=count, phase=phase,
                         pixel_mismatches=scores[phase], colored_pixels=colored,
                         image=png.relative_to(SITE).as_posix(), image_sha256=sha(png),
                         passed=scores[phase]==0 and phase==(count-1)%64 and count>=frames-8 and (mode!='cgb' or colored>0))
            records.append(entry)
            print(mode,frames,entry,flush=True)
    animation = all((records[k+1]['phase']-records[k]['phase'])%64 == 1 and
                    (records[k+2]['phase']-records[k]['phase'])%64 == 8 for k in [0,9])
    title_source = SOURCE.with_name('raster_title_entry.c')
    title_rom = OUT/'raster_title_entry.gb'
    run([compiler, title_source, '-I', library, '-I', SITE/'samples', '-o', title_rom,
         '--profile=dev', '--rst-disable', '--stack-bank=fixed', '--cgb=cgb',
         '--no-cache', '--no-disasm'], OUT/'title-build.txt')
    background = reference_rows(title=True)
    for mode in ['dmg','cgb']:
        for frames in [16,40,60,84,120,176]:
            stem='title-'+mode+'-'+str(frames)
            png=OUT/(stem+'.png'); report=OUT/(stem+'.json')
            run([emulator,title_rom,'--hardware',mode,'--run-frames',frames,'--png',png,
                 '--dump-report',report,'--report-sections','meta,watched_memory',
                 '--watch-window','frames:0xC600:2','--watch-fields','preview'], OUT/(stem+'.txt'))
            state=json.loads(report.read_text(encoding='utf-8'))
            count=state['watched_memory'][0]['preview_bytes'][0]
            assert state['watched_memory'][0]['preview_bytes'][1] == 17
            age=(count-1)%160
            base=(160+2*age)%256 if age<48 else 0
            phase=age if age<48 else age-48
            displacement=[offsets[(y+phase)%64] if age<48 else (((y+phase)%16)//2-4 if age<96 else 0) for y in range(144)]
            width,height,channels,rows=read_png(png)
            pixels=[[tuple(row[x*channels:x*channels+3]) for x in range(160)] for row in rows]
            paper=max(set(sum(pixels,[])),key=sum(pixels,[]).count)
            mismatches=sum((pixels[y][x]!=paper) != background[y][(x+base+displacement[y])%256] for y in range(144) for x in range(160))
            entry=dict(lesson='title',mode=mode,frames=frames,completed=count,age=age,
                       pixel_mismatches=mismatches,image=png.relative_to(SITE).as_posix(),image_sha256=sha(png),
                       passed=mismatches==0 and count>=frames-8)
            records.append(entry);print(entry,flush=True)
    result = dict(records=records, animation_passed=animation,
                  rom_sha256=sha(rom), title_rom_sha256=sha(title_rom),
                  source_sha256=sha(SOURCE), title_source_sha256=sha(title_source), compiler_sha256=sha(compiler), emulator_sha256=sha(emulator),
                  support_sha256={name:sha(SITE/'samples'/name) for name in ['gb_common.h','font_gb.h']},
                  library_sha256={name:sha(library/name) for name in ['raster.c','raster.h','scroll.c','scroll.h']},
                  script_sha256=sha(Path(__file__)), passed=animation and all(r['passed'] for r in records))
    (OUT/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    raise SystemExit(0 if result['passed'] else 1)

if __name__ == '__main__':
    main()
