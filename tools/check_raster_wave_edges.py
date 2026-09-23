"""Exercise raster state, wrapping, divider timing and LCD-off return in ROMs."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
SOURCE='''#include "gb_common.h"
#include "scroll.c"
#include "raster.c"
#pragma bank 0
__location(0xC600) u16 result[32];
RasterLineX effect;
void main() {
    m_init(); __wait_vblank(); M_LCDC=0;
    Raster_LineXInit(&effect, KQ_RASTER_LINE_TRAVEL_GATE, 250);
    result[0]=effect.phase;result[1]=effect.phase_step;result[2]=effect.frame_divider;
    Raster_LineXSetPhase(&effect,8);
    result[3]=Raster_LineXGetOffset(&effect,0);
    effect.frame_counter=2;
    Raster_LineXSetSpeed(&effect,3,0);
    result[4]=effect.phase;result[5]=effect.frame_divider;result[6]=effect.frame_counter;
    Raster_LineXSetProfile(&effect,KQ_RASTER_LINE_X_TITLE);
    result[7]=Raster_LineXGetOffset(&effect,0);
    result[8]=Raster_LineXGetOffset(&effect,15);
    result[9]=effect.phase_step;
    Raster_LineXSetPhase(&effect,255);
    result[10]=Raster_LineXGetOffset(&effect,1);
    Raster_LineXSetProfile(&effect,99);
    result[11]=Raster_LineXGetOffset(&effect,200);
    Raster_LineXSetPhase(&effect,23);
    effect.frame_counter=2;
    Raster_LineXRunFrame(&effect);
    result[12]=effect.phase;result[13]=effect.frame_counter;
    Raster_LineXInit(&effect,KQ_RASTER_LINE_TRAVEL_GATE,0);
    Raster_LineXSetSpeed(&effect,3,2);
    M_LCDC=0x91;
    Raster_LineXRunFrame(&effect);result[14]=effect.phase;
    Raster_LineXRunFrame(&effect);result[15]=effect.phase;
    Raster_LineXRunFrame(&effect);result[16]=effect.phase;
    Raster_LineXRunFrame(&effect);result[17]=effect.phase;
    Raster_LineXSetSpeed(&effect,0,1);
    Raster_LineXRunFrame(&effect);result[18]=effect.phase;
    result[19]=0xA55A;
    while(1){}
}
'''

def main():
    import subprocess,hashlib
    site=ROOT/'manual/latest';repos=ROOT/'publish/github_20260912'
    out=site/'verification/api-raster-wave/state';out.mkdir(parents=True,exist_ok=True)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    source=out/'case.c';source.write_text(SOURCE,encoding='utf-8')
    expected=[0,1,1,11,8,1,0,246,253,3,246,250,23,2,0,3,3,6,6,0xA55A]
    records=[]
    for variant,flags in [('default',[]),('unoptimized',['-O0']),('stack',['--abi=stack'])]:
        rom=out/(variant+'.gb')
        cmd=[repos/'kitaqgb/kitaqgb.exe',source,'-I',repos/'kitaqgb/lib','-I',site/'samples','-o',rom,'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--no-cache','--no-disasm']+flags
        result=subprocess.run(list(map(str,cmd)),capture_output=True,timeout=120)
        (out/(variant+'-build.txt')).write_bytes(result.stdout+result.stderr)
        assert result.returncode==0
        for mode in ['dmg','cgb']:
            report=out/(variant+'-'+mode+'.json')
            cmd=[repos/'kokura/kokura-cli.exe',rom,'--hardware',mode,'--run-frames','30','--dump-report',report,'--report-sections','meta,watched_memory','--watch-fields','preview']
            for n in [0,16,32]:cmd+=['--watch-window',f'r{n}:{0xC600+n}:{min(16,40-n)}']
            result=subprocess.run(list(map(str,cmd)),capture_output=True,timeout=120);assert result.returncode==0
            data=json.loads(report.read_text(encoding='utf-8'));windows={r['name']:r['preview_bytes'] for r in data['watched_memory']}
            raw=sum((windows['r'+str(n)] for n in [0,16,32]),[])
            actual=[raw[n]+256*raw[n+1] for n in range(0,40,2)]
            records.append(dict(variant=variant,mode=mode,actual=actual,expected=expected,passed=actual==expected,
                                rom=rom.relative_to(site).as_posix(),rom_sha256=sha(rom)))
            print(variant,mode,'PASS' if actual==expected else actual,flush=True)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    report=dict(records=records,passed=all(r['passed'] for r in records),source=source.relative_to(site).as_posix(),source_sha256=sha(source),
                script_sha256=sha(Path(__file__)),compiler_sha256=sha(repos/'kitaqgb/kitaqgb.exe'),emulator_sha256=sha(repos/'kokura/kokura-cli.exe'),
                library_sha256={name:sha(repos/'kitaqgb/lib'/name) for name in ['raster.c','raster.h','scroll.c','scroll.h']},
                support_sha256={name:sha(site/'samples'/name) for name in ['gb_common.h','font_gb.h']})
    (out/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    raise SystemExit(0 if report['passed'] else 1)

if __name__=='__main__':main()
