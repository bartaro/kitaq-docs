"""Confirm that enabled-display frame waits dispatch callbacks on successive hardware frames."""
from pathlib import Path
import json,subprocess,hashlib
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-batch100';records=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for platform in ['gb','fc']:
 folder=OUT/'state'/('timing-'+platform);folder.mkdir(parents=True,exist_ok=True);source=folder/'case.c';rom=folder/('case.gb' if platform=='gb' else 'case.nes')
 code='#include "system.c"\n__location('+('0xC600' if platform=='gb' else '0x0700')+') u8 phase[4];\n'
 if platform=='gb':code+='__location(0xFF40) u8 lcd;\n'
 code+='void callback(){phase[0]=phase[0]+1;phase[1]=system_get_frame8();}\nvoid main(){u8 i;for(i=0;i<4;i++)phase[i]=0;system_init();'
 if platform=='gb':code+='lcd=0x91;__wait_vblank();'
 code+='system_set_vblank_callback(callback);for(i=0;i<3;i++)system_wait_vblank();phase[2]=165;while(1){}}'
 source.write_text(code,encoding='utf-8');compiler=REPOS/('kitaq'+platform)/('kitaq'+platform+'.exe');lib=compiler.parent/'lib'
 command=[str(compiler),str(source),'-I',str(lib),'-o',str(rom),'--no-cache','--no-disasm']
 if platform=='gb':command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb']
 result=subprocess.run(command,cwd=folder,capture_output=True,timeout=120);(folder/'build.txt').write_bytes(result.stdout+result.stderr)
 if result.returncode:raise RuntimeError(platform+' timing build')
 for mode in (['dmg','cgb'] if platform=='gb' else ['nrom']):
  observations=[];exe=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
  if platform=='gb':
   timeline=folder/(mode+'.jsonl');report=folder/(mode+'.json')
   command=[str(exe),str(rom),'--hardware',mode,'--run-frames','12','--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview','--watch-window','phase:50688:4','--trace-point','frame_end','--timeline-out',str(timeline)]
   result=subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
   if result.returncode:raise RuntimeError('GB timing run')
   for line in timeline.read_text(encoding='utf-8').splitlines():
    row=json.loads(line);observations.append({'frame':row['completed_frames'],'phase':row['watched_memory'][0]['preview_bytes']})
  else:
   for frames in range(1,9):
    report=folder/('frame'+str(frames)+'.json');command=[str(exe),'run',str(rom),'--frames',str(frames),'--headless','--snapshot',str(report)]
    result=subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
    if result.returncode:raise RuntimeError('FC timing run')
    state=json.loads(report.read_text(encoding='utf-8'));observations.append({'frame':frames,'phase':state['bus']['ram'][0x700:0x704]})
  first=[next((o['frame'] for o in observations if o['phase'][0]>=count),None) for count in [1,2,3]]
  passed=all(f is not None for f in first) and first[1]-first[0]==1 and first[2]-first[1]==1 and observations[-1]['phase']==[3,3,165,0]
  row={'platform':platform,'mode':mode,'first_callback_frames':first,'observations':observations,'passed':passed,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),'compiler_sha256':sha(compiler),'emulator_sha256':sha(exe)}
  records.append(row);print(platform,mode,'callback frames',first,'PASS' if passed else 'FAIL',flush=True)
  (OUT/'timing_checks.json').write_text(json.dumps({'records':records,'script_sha256':sha(Path(__file__))},indent=2),encoding='utf-8')
if not all(row['passed'] for row in records):raise SystemExit(1)
