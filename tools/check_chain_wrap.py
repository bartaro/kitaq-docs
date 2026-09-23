"""Check normalized wrapped displacements for every supported field size."""
from pathlib import Path
import json,hashlib,subprocess,argparse
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
ap=argparse.ArgumentParser();ap.add_argument('--platform',choices=['gb','fc']);args=ap.parse_args()
OUT=SITE/'verification/api-chain-wrap/state';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cases=[]
for size in range(1,257):
 if size<=9:pairs={(a,b) for a in range(size) for b in range(size)}
 else:
  h=size//2;pairs={(0,0),(0,size-1),(size-1,0),(0,h),(h,0),(0,h+1),(h+1,0),(h-1,size-1),(size-1,h-1),(1,size-1),(size-1,1),(1,2),(2,1)}
 for target,current in sorted(pairs):
  # Select the minimum-magnitude displacement among the direct route and one
  # crossing in either direction. Put the direct route first for exact ties.
  direct=target-current;delta=min([direct,direct-size,direct+size],key=abs)
  cases.append([target,current,size,delta&65535])
rows=[]
for platform in ([args.platform] if args.platform else ['gb','fc']):
 lib=REPOS/('kitaq'+platform)/'lib';compiler=lib.parent/('kitaq'+platform+'.exe');emu=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
 variants=[('default',[]),('O0',['-O0'])]+([('stack',['--abi=stack'])] if platform=='gb' else [('no-inline',['--no-small-inline']),('fastcall',['--fastcall-v2'])])
 for part,start in enumerate(range(0,len(cases),512)):
  selected=cases[start:start+512]
  for variant,flags in variants:
   folder=OUT/platform/str(part)/variant;folder.mkdir(parents=True,exist_ok=True);source=folder/'case.c';rom=folder/('case.gb' if platform=='gb' else 'case.nes')
   source.write_text('#include "chain.c"\n'+
    'typedef __packed struct {u8 target;u8 current;u16 size;u16 expected;} Test;\n__prg_rom Test inputs[]={'+','.join('{'+','.join(map(str,row))+'}' for row in selected)+'};\n'+
    '__location('+('0xC600' if platform=='gb' else '0x0600')+') u16 result[5];\nvoid main(){u16 i;u16 actual;for(i=0;i<'+str(len(selected))+';i++){actual=(u16)chain_wrap_delta(inputs[i].target,inputs[i].current,inputs[i].size);if(actual!=inputs[i].expected){result[1]++;result[2]=i;result[3]=actual;}result[0]++;}result[4]=0xA55A;while(1){}}',encoding='ascii')
   command=[str(compiler),str(source),'-I',str(lib),'-o',str(rom),'--no-cache','--no-disasm',*flags]
   command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=128k'] if platform=='gb' else ['--mapper=mmc3']
   p=subprocess.run(command,cwd=folder,capture_output=True,timeout=120);(folder/'build.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0,(p.stdout+p.stderr)[-2000:]
   for mode in (['dmg','cgb'] if platform=='gb' else ['ntsc']):
    state=folder/(mode+'.json');command=[str(emu),str(rom),'--hardware',mode,'--run-frames','600','--dump-report',str(state),'--report-sections','meta,watched_memory','--watch-fields','preview','--watch-window','result:0xC600:10'] if platform=='gb' else [str(emu),'run',str(rom),'--frames','600','--snapshot',str(state)]
    p=subprocess.run(command,cwd=folder,capture_output=True,timeout=120);assert p.returncode==0
    data=json.loads(state.read_text());raw=data['watched_memory'][0]['preview_bytes'] if platform=='gb' else data['bus']['ram'][0x600:0x60a]
    actual=[raw[i]+256*raw[i+1] for i in range(0,10,2)];expected=[len(selected),0,0,0,0xA55A]
    row=dict(platform=platform,part=part,variant=variant,mode=mode,cases=len(selected),actual=actual,expected=expected,passed=actual==expected,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),compiler_sha256=sha(compiler),emulator_sha256=sha(emu),library_sha256=sha(lib/'chain.c'),header_sha256=sha(lib/'chain.h'))
    rows.append(row);print(platform,part,variant,mode,'PASS' if row['passed'] else 'FAIL',actual,flush=True)
    if row['passed']:state.unlink()
    report=dict(script_sha256=sha(Path(__file__)),vector_count=len(cases),vectors_sha256=hashlib.sha256(json.dumps(cases).encode()).hexdigest(),records=rows,passed=all(r['passed'] for r in rows))
    (OUT/((args.platform+'-' if args.platform else '')+'results.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    if not row['passed']:raise SystemExit(1)
