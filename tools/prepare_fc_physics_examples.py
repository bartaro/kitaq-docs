"""Prepare FC lessons sharing the tested GB physics exercises and owned font."""
from pathlib import Path
SITE=Path(__file__).resolve().parents[1]

def main():
    font=(SITE/'samples/font.chr').read_bytes()[:2048]
    header='// Original ASCII glyphs by DAISUKE OBA, distributed under the MIT license.\n#pragma once\n__prg_rom u8 physics_font_fc[2048]={\n'
    header+='\n'.join(','.join(str(v) for v in font[i:i+32])+',' for i in range(0,len(font),32))+'\n};\n'
    (SITE/'samples/physics_font_fc.h').write_text(header,encoding='ascii')
    for group in ['body2d','surface','body3d']:
        path=SITE/f'samples/api-examples/gb/physics_{group}.c'
        source=path.read_text(encoding='utf-8').replace('#include "physics_visual.h"','#include "physics_visual_fc.h"\n#pragma bank 1')
        if group=='body3d':source=source.replace('#include "physics3d.c"','#include "fixed.c"\n#include "physics2d.c"\n#include "physics3d.c"')
        source=source.replace('0xC600','0x0600').replace('M_LCDC=0x91;','phys_end();')
        source=source.replace('// example:__smul16x8:start','// Exercise the same signed scaling through the portable physics API.').replace('    // example:__smul16x8:end\n','').replace('__smul16x8(-257,64)','kq2d_scale_q8(-257,64)')
        (SITE/f'samples/api-examples/fc/physics_{group}.c').write_text(source,encoding='utf-8')
if __name__=='__main__':main()
