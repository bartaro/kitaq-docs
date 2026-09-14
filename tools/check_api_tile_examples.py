"""Build tile teaching programs and check their actual DMG/CGB result pixels.

Uses Python's standard library only. A successful process exit is insufficient:
the title, FAILED CHECKS label and all three zero digits must match the supplied
font pixel-for-pixel. The ROM itself compares addressed tile/attribute bytes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import zlib
from datetime import datetime, timezone
from api_build_cleanup import cleanup_build_outputs

SITE = Path(__file__).resolve().parents[1]


def read_png(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    position = 8
    compressed = bytearray()
    while position < len(data):
        size = struct.unpack('>I', data[position:position+4])[0]
        kind = data[position+4:position+8]
        payload = data[position+8:position+8+size]
        if kind == b'IHDR':
            width, height, depth, color, _, _, interlace = struct.unpack('>IIBBBBB', payload)
        if kind == b'IDAT': compressed.extend(payload)
        position += 12 + size
    assert depth == 8 and color in (2, 6) and interlace == 0
    channels = 3 if color == 2 else 4
    stride = width * channels
    stream = zlib.decompress(compressed)
    previous = bytearray(stride)
    rows = []
    def paeth(a, b, c):
        prediction = a + b - c
        distances = [abs(prediction-a), abs(prediction-b), abs(prediction-c)]
        return [a,b,c][distances.index(min(distances))]
    for y in range(height):
        offset = y * (stride + 1)
        method = stream[offset]
        row = bytearray(stream[offset+1:offset+1+stride])
        for x in range(stride):
            left = row[x-channels] if x >= channels else 0
            above = previous[x]
            upper_left = previous[x-channels] if x >= channels else 0
            predictor = [0, left, above, (left+above)//2, paeth(left, above, upper_left)][method]
            row[x] = (row[x] + predictor) & 255
        rows.append(row)
        previous = row
    return width, height, channels, rows


def check_result_pixels(path, diagram, hardware):
    width, height, channels, rows = read_png(path)
    assert (width, height) == (160,144)
    source = (SITE/'samples/font_gb.h').read_text(encoding='utf-8')
    array = source[source.index('{')+1:source.index('}')]
    font = [int(value,0) for value in re.findall(r'0x[0-9A-Fa-f]+|\d+',array)]
    assert len(font) == 2048
    mismatches = 0
    for tile_x, tile_y, text in [(2,0,'TILE EXAMPLE'), (2,7,'FAILED CHECKS'), (3,8,'000')]:
        for n, character in enumerate(text):
            for y in range(8):
                low, high = font[ord(character)*16+y*2:ord(character)*16+y*2+2]
                for x in range(8):
                    expected_dark = ((low | high) & (1 << (7-x))) != 0
                    at = (8*(tile_x+n)+x)*channels
                    rgb = rows[8*tile_y+y][at:at+3]
                    actual_dark = sum(rgb) < 384
                    mismatches += actual_dark != expected_dark
    shape_mismatches = 0
    color_mismatches = 0
    pattern = diagram['rows']
    pattern_width = max(map(len,pattern))
    for gy in range(-1,len(pattern)+1):
        for gx in range(-1,pattern_width+1):
            inside = 0 <= gy < len(pattern) and 0 <= gx < len(pattern[gy])
            character = pattern[gy][gx] if inside else ' '
            colors = diagram['cgb_colors']
            palette = (colors[0] if len(colors)==1 else colors[gy*pattern_width+gx]) if inside and hardware=='cgb' else 0
            for y in range(8):
                low, high = font[ord(character)*16+y*2:ord(character)*16+y*2+2]
                for x in range(8):
                    expected_dark = ((low | high) & (1 << (7-x))) != 0
                    at = (8*(diagram['x']+gx)+x)*channels
                    red, green, blue = rows[8*(diagram['y']+gy)+y][at:at+3]
                    actual_dark = red+green+blue < 384
                    shape_mismatches += actual_dark != expected_dark
                    if expected_dark:
                        color_ok = [max(red,green,blue)<64, red>green+64 and red>blue+64,
                                    blue>red+64 and blue>green+64, green>red+64 and green>blue+64][palette]
                        color_mismatches += not color_ok
    return {'result_text_pixel_mismatches':mismatches,'drawn_pattern_pixel_mismatches':shape_mismatches,'drawn_pattern_color_mismatches':color_mismatches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repositories', type=Path)
    parser.add_argument('--only', nargs='*')
    args = parser.parse_args()
    repositories = args.repositories.resolve()
    compiler = repositories/'kitaqgb/kitaqgb.exe'
    emulator = repositories/'kokura/kokura-cli.exe'
    output = SITE/'verification/api-tiles'
    output.mkdir(parents=True, exist_ok=True)
    contracts = json.loads((SITE/'tools/api_descriptions/tile_contracts.json').read_text(encoding='utf-8'))
    results_path = output/'results.json'
    previous = json.loads(results_path.read_text(encoding='utf-8')).get('examples',[]) if results_path.exists() and args.only else []
    results = {r['api']:r for r in previous}
    report = {'scope':'LCD-off tile addressing, data and CGB attributes; no LCD-on timing or hardware claim',
              'compiler_sha256':hashlib.sha256(compiler.read_bytes()).hexdigest(),
              'emulator_sha256':hashlib.sha256(emulator.read_bytes()).hexdigest(),
              'shared_source_sha256':{name:hashlib.sha256((SITE/'samples'/name).read_bytes()).hexdigest() for name in ['gb_common.h','gb_tile_example.h','font_gb.h']}}
    for key, contract in contracts.items():
        name = key.split(':',1)[1]
        if args.only and name not in args.only: continue
        example = SITE/contract['example']['program']
        rom = output/(name+'.gb')
        if rom.exists(): rom.unlink()
        command = [str(compiler),str(example),'-I',str(repositories/'kitaqgb/lib'),'-I',str(SITE/'samples'),'-o',str(rom),'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--no-disasm','--no-cache']
        proc = subprocess.run(command,cwd=output,capture_output=True,timeout=60)
        (output/(name+'-build.txt')).write_bytes(proc.stdout+proc.stderr)
        result = {'api':name,'checked_at':datetime.now(timezone.utc).isoformat(),'source_sha256':hashlib.sha256(example.read_bytes()).hexdigest(),'build_exit':proc.returncode,'runs':[]}
        if proc.returncode == 0 and rom.exists():
            result['rom_sha256'] = hashlib.sha256(rom.read_bytes()).hexdigest()
            for hardware in ['dmg','cgb']:
                picture = output/(name+'-'+hardware+'.png')
                runtime = output/(name+'-'+hardware+'.json')
                # Remove only these exact outputs so failed runs cannot reuse old evidence.
                for artifact in [picture,runtime]:
                    if artifact.exists(): artifact.unlink()
                run = subprocess.run([str(emulator),str(rom),'--hardware',hardware,'--run-frames','90','--png',str(picture),'--dump-report',str(runtime)],cwd=output,capture_output=True,timeout=60)
                errors = check_result_pixels(picture, contract['example']['image'], hardware) if picture.exists() else {'result_text_pixel_mismatches':-1,'drawn_pattern_pixel_mismatches':-1,'drawn_pattern_color_mismatches':-1}
                observed = json.loads(runtime.read_text(encoding='utf-8')) if runtime.exists() else {}
                record = {'hardware':hardware,'exit':run.returncode,**errors,'frames_executed':observed.get('meta',{}).get('frames_executed'),'stop_reason':observed.get('stop_reason'),'unsupported_opcodes':observed.get('unsupported_opcodes')}
                if run.returncode != 0:
                    (output/(name+'-'+hardware+'-runtime.txt')).write_bytes(run.stdout+run.stderr)
                result['runs'].append(record)
                # Keep the observations needed to assess this sample, without large unused traces.
                if runtime.exists() and all(value == 0 for value in errors.values()) and run.returncode == 0:
                    compact = {'scope':report['scope'],'meta':observed.get('meta'),'cpu':observed.get('cpu'),'stop_reason':observed.get('stop_reason'),'video':observed.get('video'),'unsupported_opcodes':observed.get('unsupported_opcodes'),'result_check':record}
                    runtime.write_text(json.dumps(compact,indent=2),encoding='utf-8')
        result['expected_image'] = contract['example']['image']
        result['passed'] = proc.returncode == 0 and len(result['runs']) == 2 and all(r['exit']==0 and r['result_text_pixel_mismatches']==0 and r['drawn_pattern_pixel_mismatches']==0 and r['drawn_pattern_color_mismatches']==0 and r['frames_executed']==90 for r in result['runs'])
        results[name] = result
        report['examples'] = list(results.values())
        report['passed'] = sum(r['passed'] for r in results.values())
        report['tested'] = len(results)
        results_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(name + ': ' + ('PASS' if result['passed'] else 'FAIL'),flush=True)
    if any(not r['passed'] for r in results.values()):raise SystemExit(1)
    cleanup_build_outputs(output)


if __name__ == '__main__':main()
