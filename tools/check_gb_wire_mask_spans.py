"""Validate DMG span byte boundaries against independently generated masks."""
from pathlib import Path
import json,subprocess
from check_gb_wire_hidden_speed import OUT,REPOS,sha

def main():
    records=[]
    # Every pair of bit offsets in one byte, adjacent bytes and distant bytes.
    spans=[]
    for a in range(8):
        for b in range(8):
            if a<=b:spans.append((a,b))
            spans.extend([(a,8+b),(a,120+b)])
    for height in [96,120]:
        rows=[]
        for n,(a,b) in enumerate(spans):
            y=[0,1,height-2,height-1][n%4]
            expected=[0xA5]*16
            for x in range(a,b+1):expected[x//8]|=0x80>>(x%8)
            rows.extend([y,a,b]+expected)
        folder=OUT/f'mask-spans-{height}';folder.mkdir(exist_ok=True)
        source=folder/'case.c';rom=folder/'case.gb'
        library=REPOS/'kitaqgb/lib/wire3d_dmg.c'
        prefix=f'''#pragma bank 0
#define WIRE3D_DMG_HEIGHT {height}
#include "wire3d_dmg.h"
__location(0xC110) u16 checked;
__location(0xC112) u16 failures;
__location(0xC114) u8 done;
'''
        body=f'''#pragma bank 0
__prg_rom u8 oracle[{len(rows)}]={{{','.join(map(str,rows))}}};
void main(){{
    u16 n;u16 base;u16 ofs;u8 y;u8 a;u8 b;u8 j;
    checked=0;failures=0;done=0;
    for(n=0;n<{len(spans)};n++){{
        base=n*19;y=oracle[base];a=oracle[base+1];b=oracle[base+2];
        ofs=(u16)y*16;
        for(j=0;j<16;j++)w3ddmg_occlusion_mask[ofs+j]=165;
        w3ddmg_mask_set_span(y,a,b);
        for(j=0;j<16;j++){{
            if(w3ddmg_occlusion_mask[ofs+j]!=oracle[base+3+j])failures++;
            checked++;
        }}
    }}
    // An invalid row must not alter any valid mask byte.
    for(ofs=0;ofs<{height*16};ofs++)w3ddmg_occlusion_mask[ofs]=90;
    w3ddmg_mask_set_span({height},0,127);
    w3ddmg_mask_set_span(255,0,127);
    for(ofs=0;ofs<{height*16};ofs++){{if(w3ddmg_occlusion_mask[ofs]!=90)failures++;checked++;}}
    done=1;while(1){{}}
}}
'''
        source.write_text(prefix+library.read_text()+body)
        cmd=[str(REPOS/'kitaqgb/kitaqgb.exe'),str(source),'-I',str(REPOS/'kitaqgb/lib'),'-o',str(rom),'--profile=dev','--stack-bank=fixed','--rst-disable','--cgb=cgb','--cart=mbc5','--romsize=256k','--no-cache','--no-disasm']
        p=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=180);(folder/'build.txt').write_bytes(p.stdout+p.stderr)
        assert p.returncode==0,str(folder)
        report=folder/'result.json'
        cmd=[str(REPOS/'kokura/kokura-cli.exe'),str(rom),'--hardware','dmg','--run-frames','1000','--watchpoint','0xC114','--watch-window','marks:49424:5','--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview']
        p=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=180);(folder/'run.txt').write_bytes(p.stdout+p.stderr)
        marks=json.loads(report.read_text())['watched_memory'][0]['preview_bytes']
        actual=marks[0]+256*marks[1];want=len(spans)*16+height*16
        passed=p.returncode==0 and actual==want and marks[2:]==[0,0,1]
        records.append(dict(height=height,spans=len(spans),checked_bytes=actual,expected_bytes=want,passed=passed,library_sha256=sha(library),source_sha256=sha(source),rom_sha256=sha(rom),compiler_sha256=sha(REPOS/'kitaqgb/kitaqgb.exe'),emulator_sha256=sha(REPOS/'kokura/kokura-cli.exe')))
        print(height,actual,passed,flush=True)
        (OUT/'mask-span-results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=records),indent=2))
        assert passed,marks

if __name__=='__main__':main()
