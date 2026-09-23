"""Check all 256 ROM sine samples on GB and FC, including byte-phase wrap."""
from pathlib import Path
import argparse,hashlib,json,math,re,subprocess

SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
 out=args.output.resolve();out.mkdir(parents=True,exist_ok=True);rows=[];tables={}
 for platform,filename in [('gb','math.c'),('fc','math_lut.c')]:
  repo=REPOS/('kitaq'+platform);source=repo/'lib'/filename;compiler=repo/('kitaq'+platform+'.exe')
  text=source.read_text(encoding='utf-8');body=text[text.index('{')+1:text.index('}')];values=[int(n) for n in re.findall(r'\d+',body)]
  assert len(values)==256 and values[::64]==[128,255,128,1]
  assert all(values[i]+values[(i+128)&255]==256 for i in range(256))
  assert all(abs((values[i]-128)-127*math.cos(2*math.pi*(i-64)/256))<=0.500000001 for i in range(256))
  tables[platform]=values
  emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
  variants=[('default',[]),('O0',['-O0'])]+([('stack',['--abi=stack'])] if platform=='gb' else [('no-inline',['--no-small-inline']),('fastcall',['--fastcall-v2'])])
  for variant,flags in variants:
   folder=out/platform/variant;folder.mkdir(parents=True,exist_ok=True);program=folder/'case.c';rom=folder/('case.gb' if platform=='gb' else 'case.nes')
   # A word counter visits 0..255 without wrapping early; an independent byte
   # phase verifies that the final sample wraps to the first on increment.
   code=('#include "math_lut.h"\n' if platform=='fc' else '')+'#pragma bank 0\n#include "'+filename+'"\n#pragma bank 0\n'
   address='0xC600' if platform=='gb' else '0x0600'
   code+='__location('+address+') u8 result[262];\nvoid main(){u16 i;u8 phase;for(i=0;i<256;i++)result[i]=MATH_SIN[(u8)i];phase=255;result[256]=MATH_SIN[phase];phase++;result[257]=MATH_SIN[phase];result[258]=(u8)sizeof(MATH_SIN);result[259]=(u8)(sizeof(MATH_SIN)>>8);result[260]=0x5A;result[261]=0xA5;while(1){}}\n'
   program.write_text(code,encoding='utf-8')
   command=[str(compiler),str(program),'-I',str(repo/'lib'),'-o',str(rom),'--no-cache','--no-disasm',*flags]
   command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb'] if platform=='gb' else ['--mapper=nrom']
   p=subprocess.run(command,cwd=folder,capture_output=True,timeout=90)
   assert p.returncode==0,(p.stdout+p.stderr).decode(errors='replace')
   for mode in (['dmg','cgb'] if platform=='gb' else ['ntsc']):
    state=folder/(mode+'.json')
    if platform=='gb':
     cmd=[str(emulator),str(rom),'--hardware',mode,'--run-frames','30','--dump-report',str(state),'--report-sections','meta,watched_memory','--watch-fields','preview']
     for n in range(0,262,16):cmd+=['--watch-window',f'sine{n}:{0xC600+n}:{min(16,262-n)}']
    else:cmd=[str(emulator),'run',str(rom),'--frames','30','--headless','--snapshot',str(state)]
    run=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=90);assert run.returncode==0
    data=json.loads(state.read_text())
    if platform=='gb':
     watches={r['name']:r['preview_bytes'] for r in data['watched_memory']};actual=sum((watches['sine'+str(n)] for n in range(0,262,16)),[])
    else:actual=data['bus']['ram'][0x600:0x600+262]
    expected=values+[125,128,0,1,0x5A,0xA5]
    row=dict(platform=platform,variant=variant,mode=mode,passed=actual==expected,actual=actual,expected=expected,source_sha256=sha(source),program_sha256=sha(program),rom_sha256=sha(rom),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator))
    rows.append(row);print(platform,variant,mode,'PASS' if row['passed'] else 'FAIL',flush=True)
    (out/'report.json').write_text(json.dumps(dict(records=rows,passed=all(r['passed'] for r in rows),checker_sha256=sha(Path(__file__))),indent=2))
    assert row['passed']
    state.unlink()
 assert tables['gb']==tables['fc'] and len(rows)==10
 print('10 target runs: all256 samples, sizeof and phase wrap verified.')

if __name__=='__main__':main()
