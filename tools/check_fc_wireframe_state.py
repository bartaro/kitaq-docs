"""Check projection limits, signed rotations and rejected model edges on the FC.

The host oracle derives tables from geometry, not by reading library constants.
Every viewport and compiler variant runs a complete, independently checked ROM.
"""
from pathlib import Path
import hashlib, json, math, subprocess
from check_batch200 import dependencies

SITE = Path(__file__).resolve().parents[1]
REPOS = SITE.parents[1] / 'publish/github_20260912'
OUT = SITE / 'verification/api-wireframe-fc/state'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
PROJECTION = [(12, -20, z, 0) for z in [-32768, -1, 0, 31, 32, 33, 127, 128, 254, 255, 256, 32767]]
PROJECTION += [(x, y, 96, 0) for x, y in [(-128, 0), (-127, 0), (-1, 0), (0, 0), (1, 0), (127, 0), (128, 0), (0, -128), (0, -127), (0, 127), (0, 128), (-127, -127), (127, 127)]]
PROJECTION += [(0, 0, 96, nulls) for nulls in [1, 2, 3]]
ROTATIONS = [(12, -20, 31, *(angle if axis == n else 0 for n in range(3)), 0) for axis in range(3) for angle in range(32)]
ROTATIONS += [(12, -20, 31, *angles, 0) for angles in [(3, 5, 7), (31, 31, 31), (32, 64, 96), (255, 255, 255)]]
ROTATIONS += [(12, -20, 31, 3, 5, 7, mask) for mask in [1, 2, 4, 7]]

def rotation(case):
    x, y, z, rx, ry, rz, nulls = case
    if nulls:
        return [x, y, z]
    trig = lambda angle: round(math.sin(2 * math.pi * (angle % 32) / 32) * 64)
    trunc = lambda value: (-1 if value < 0 else 1) * (abs(value) // 64)
    if ry % 32:
        s, c = trig(ry), trig(ry + 8)
        x, z = trunc(x * c + z * s), trunc(z * c - x * s)
    if rx % 32:
        s, c = trig(rx), trig(rx + 8)
        y, z = trunc(y * c - z * s), trunc(y * s + z * c)
    if rz % 32:
        s, c = trig(rz), trig(rz + 8)
        x, y = trunc(x * c - y * s), trunc(x * s + y * c)
    return [x, y, z]

def expectation(width, height):
    values = []
    labels = []
    for index, (x, y, z, nulls) in enumerate(PROJECTION):
        valid = not nulls and -127 <= x <= 127 and -127 <= y <= 127 and 32 <= z <= 255
        output = [0, 1234, -2345]
        if valid:
            scale = min(255, round(64 * width / z))
            offset = lambda value: (-1 if value < 0 else 1) * (abs(value) * scale // 128)
            output = [1, width // 2 + offset(x), height // 2 - offset(y)]
        values += output
        labels += [f'projection-{index}-{field}' for field in ['status', 'x', 'y']]
    for index, case in enumerate(ROTATIONS):
        values += rotation(case)
        labels += [f'rotation-{index}-{axis}' for axis in ['x', 'y', 'z']]
    values += [0] * 6 + [0, 1, width // 2, height // 2]
    labels += ['near-line-skipped', 'far-line-skipped', 'null-vertices', 'null-edges', 'empty-model', 'no-edges', 'rejected-vertex', 'last-valid-vertex', 'last-projected-x', 'last-projected-y']
    values += [0xA55A]
    labels += ['done']
    assert len(values) <= 512
    expected = [v & 65535 for v in values] + [0x7777] * (512 - len(values))
    labels += ['untouched-' + str(i) for i in range(len(values), 512)]
    pixels = bytearray(1536)
    scale = min(255, round(64 * width / 96))
    extent = 10 * scale // 128
    y = height // 2
    for x in range(width // 2 - extent, width // 2 + extent + 1):
        pixels[((y // 8) * (width // 8) + x // 8) * 8 + y % 8] |= 128 >> (x % 8)
    return expected, labels, bytes(pixels)

def array(name, rows):
    return '__prg_rom s16 ' + name + '[]={' + ','.join(str(v) for row in rows for v in row) + '};\n'

BODY = r'''
__location(0x0600) u8 done;
__location(0x71FE) u16 guard_before;
__location(0x7200) u16 result[512];
__location(0x7600) u16 guard_after;
s16 px; s16 py; s16 pz; s16 sx; s16 sy;
Wire3DFC_Vec3 vertices[25];
__prg_rom Wire3DFC_Edge edges[]={{0,1},{0,2},{24,0},{255,0}};
u16 nonzero(){u16 n;u16 count;count=0;for(n=0;n<1536;n++){if(w3dfc_pixels[n])count++;}return count;}
void main(){
    u16 n;u16 at;u16 base;u8 nulls;u8 ok;
    Wire3DFC_Init();done=0;guard_before=0x1357;guard_after=0x2468;
    for(n=0;n<512;n++)result[n]=0x7777;
    at=0;
    for(n=0;n<PROJECTION_COUNT;n++){
        base=n*4;px=projection[base];py=projection[base+1];pz=projection[base+2];nulls=(u8)projection[base+3];sx=1234;sy=-2345;
        if(nulls==0)ok=Wire3DFC_ProjectPoint(px,py,pz,&sx,&sy);
        else if(nulls==1)ok=Wire3DFC_ProjectPoint(px,py,pz,0,&sy);
        else if(nulls==2)ok=Wire3DFC_ProjectPoint(px,py,pz,&sx,0);
        else ok=Wire3DFC_ProjectPoint(px,py,pz,0,0);
        result[at++]=ok;result[at++]=sx;result[at++]=sy;
    }
    for(n=0;n<ROTATION_COUNT;n++){
        base=n*7;px=rotations[base];py=rotations[base+1];pz=rotations[base+2];nulls=(u8)rotations[base+6];
        if(nulls==0)Wire3DFC_RotatePoint(&px,&py,&pz,(u8)rotations[base+3],(u8)rotations[base+4],(u8)rotations[base+5]);
        else if(nulls==1)Wire3DFC_RotatePoint(0,&py,&pz,3,5,7);
        else if(nulls==2)Wire3DFC_RotatePoint(&px,0,&pz,3,5,7);
        else if(nulls==4)Wire3DFC_RotatePoint(&px,&py,0,3,5,7);
        else Wire3DFC_RotatePoint(0,0,0,3,5,7);
        result[at++]=px;result[at++]=py;result[at++]=pz;
    }
    for(n=0;n<25;n++){vertices[n].x=0;vertices[n].y=0;vertices[n].z=0;}
    vertices[0].x=-10;vertices[1].x=10;vertices[2].z=-65;vertices[24].x=40;vertices[24].y=20;
    Wire3DFC_BeginFrame();
    Wire3DFC_DrawLine3D(-10,0,31,10,0,96);result[at++]=nonzero();
    Wire3DFC_DrawLine3D(-10,0,96,10,0,256);result[at++]=nonzero();
    Wire3DFC_DrawModel(0,25,edges,4,0,0,96,0,0,0);result[at++]=nonzero();
    Wire3DFC_DrawModel(vertices,25,0,4,0,0,96,0,0,0);result[at++]=nonzero();
    Wire3DFC_DrawModel(vertices,0,edges,4,0,0,96,0,0,0);result[at++]=nonzero();
    Wire3DFC_DrawModel(vertices,25,edges,0,0,0,96,0,0,0);result[at++]=nonzero();
    Wire3DFC_DrawModel(vertices,25,edges,4,0,0,96,0,0,0);
    result[at++]=w3dfc_valid[2];result[at++]=w3dfc_valid[23];
    result[at++]=w3dfc_projected_x[23];result[at++]=w3dfc_projected_y[23];
    result[at++]=0xA55A;done=165;while(1){}
}
'''

def main():
    rows = []
    compiler = REPOS / 'kitaqfc/kitaqfc.exe'
    emulator = REPOS / 'kurosaki/kurosaki.exe'
    lib = compiler.parent / 'lib'
    for width, height in [(64,48), (96,64), (128,96)]:
        expected, labels, pixels = expectation(width, height)
        for variant, flags in [('default',[]), ('O0',['-O0']), ('no-inline',['--no-small-inline']), ('fastcall',['--fastcall-v2'])]:
            folder = OUT / (str(width) + '-' + variant)
            folder.mkdir(parents=True, exist_ok=True)
            source = folder / 'case.c'
            rom = folder / 'case.nes'
            header = f'#define WIRE3D_FC_WIDTH {width}\n#define WIRE3D_FC_HEIGHT {height}\n#include "wire3d.c"\n#define PROJECTION_COUNT {len(PROJECTION)}\n#define ROTATION_COUNT {len(ROTATIONS)}\n'
            source.write_text(header + array('projection', PROJECTION) + array('rotations', ROTATIONS) + BODY, encoding='ascii')
            # The exhaustive fixture exceeds NROM's two code banks. MMC3 gives
            # it room without changing the library's PRG-RAM address contract;
            # the separate projection/line/clear teaching tests cover NROM.
            command = [str(compiler), str(source), '-I', str(lib), '-o', str(rom), '--mapper=mmc3', '--nes-chr-ram', '--no-cache', '--no-disasm'] + flags
            build = subprocess.run(command, cwd=folder, capture_output=True, timeout=180)
            (folder / 'build.txt').write_bytes(build.stdout + build.stderr)
            assert build.returncode == 0, (folder, (build.stdout + build.stderr)[-1800:])
            state = folder / 'state.json'
            run = subprocess.run([str(emulator), 'run', str(rom), '--frames', '240', '--headless', '--snapshot', str(state)], cwd=folder, capture_output=True, timeout=120)
            assert run.returncode == 0, run.stderr[-1600:]
            data = json.loads(state.read_text(encoding='utf-8'))
            # MMC3 snapshots prefix PRG RAM with 12 scalar bytes, an eight-byte
            # IRQ clock counter and eight bank registers (Mapper::snapshot_bytes).
            memory = bytes(data['mapper_private'][28:28+8192])
            actual = [int.from_bytes(memory[n:n+2], 'little') for n in range(0x1200, 0x1600, 2)]
            guards = [int.from_bytes(memory[n:n+2], 'little') for n in [0x11FE, 0x1600]]
            actual_pixels = memory[0x800:0xE00]
            mismatches = [(labels[i], a, b) for i, (a, b) in enumerate(zip(actual, expected)) if a != b]
            row = dict(platform='fc', group='wire3d-state', mode=f'{width}x{height}', variant=variant,
                       source=source.relative_to(SITE).as_posix(), source_sha256=sha(source), rom=rom.relative_to(SITE).as_posix(), rom_sha256=sha(rom),
                       compiler_sha256=sha(compiler), emulator_sha256=sha(emulator), input_sha256=dependencies(source,lib), mapper='mmc3',
                       actual=actual, expected=expected, guards=guards, expected_guards=[0x1357,0x2468], done=data['bus']['ram'][0x600],
                       projection_cases=len(PROJECTION), rotation_cases=len(ROTATIONS),
                       pixel_buffer_sha256=hashlib.sha256(actual_pixels).hexdigest(), expected_pixel_buffer_sha256=hashlib.sha256(pixels).hexdigest())
            row['passed'] = actual == expected and guards == [0x1357,0x2468] and row['done'] == 165 and actual_pixels == pixels
            rows.append(row)
            (OUT / 'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)), records=rows), indent=2), encoding='utf-8')
            print(width, variant, 'PASS' if row['passed'] else 'FAIL', mismatches[:8], 'guards', guards, 'pixels', actual_pixels == pixels, flush=True)
            if row['passed']:
                assert state.resolve(strict=True).is_relative_to(OUT.resolve(strict=True))
                state.unlink()
            assert row['passed'], folder
    assert len(rows) == 12

if __name__ == '__main__':
    main()
