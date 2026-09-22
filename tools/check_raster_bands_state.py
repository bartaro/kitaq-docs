"""Check wrapper errors, table bytes and interrupt-control effects in GB ROMs."""
from pathlib import Path
import hashlib,json,re,subprocess
from check_batch200 import dependencies
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912';OUT=SITE/'verification/api-raster-bands/state';OUT.mkdir(parents=True,exist_ok=True)
compiler=REPOS/'kitaqgb/kitaqgb.exe';emulator=REPOS/'kokura/kokura-cli.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
steps=[];expected=[];names=[]
def code(s):steps.append(s)
def check(name,expr,want):
 steps.append(f'result[{len(expected)}]={expr};');expected.append(want);names.append(name)
code('LCDC=0;IE=0;Raster_Init();')
check('initial count','Raster_GetCount()',0);check('initial error','Raster_GetLastError()',0)
check('LY144','Raster_Push(144,1,2)',2);check('error getter','Raster_GetLastError()',2);check('getter does not clear error','Raster_GetLastError()',2)
check('failed append keeps count','Raster_GetCount()',0)
check('valid append clears error','Raster_Push(10,1,2)',0);check('clear error','Raster_GetLastError()',0)
check('equal LY','Raster_Push(10,2,3)',3);check('descending LY','Raster_Push(9,2,3)',3);check('count unchanged','Raster_GetCount()',1)
check('commit retains previous failure','Raster_Commit()',3);check('IE enabled','IE&3',3)
code('Raster_Clear();');check('clear count','Raster_GetCount()',0);check('clear error','Raster_GetLastError()',0);check('clear STAT coincidence','STAT&64',0)
check('hud top low','Raster_BuildHudTop(0,8,9)',4);check('hud top high','Raster_BuildHudTop(144,8,9)',4)
check('hud top valid','Raster_BuildHudTop(32,8,9)',0);check('hud top count','Raster_GetCount()',2)
check('invalid leaves table','Raster_BuildHudBottom(255,1,2)',4);check('invalid keeps count','Raster_GetCount()',2)
check('hud bottom zero','Raster_BuildHudBottom(0,1,2)',4);check('hud bottom valid','Raster_BuildHudBottom(112,10,11)',0)
check('parallax2 zero','Raster_BuildParallax2(0,1,2,3)',4);check('parallax2 high','Raster_BuildParallax2(144,1,2,3)',4)
check('parallax2 valid','Raster_BuildParallax2(64,4,8,9)',0);check('parallax2 count','Raster_GetCount()',2)
check('parallax3 zero','Raster_BuildParallax3(0,80,1,2,3,4)',4);check('parallax3 equal','Raster_BuildParallax3(80,80,1,2,3,4)',4)
check('parallax3 reversed','Raster_BuildParallax3(81,80,1,2,3,4)',4);check('parallax3 high','Raster_BuildParallax3(80,144,1,2,3,4)',4)
check('parallax3 valid','Raster_BuildParallax3(40,80,1,2,3,4)',0);check('parallax3 count','Raster_GetCount()',3)
code('Raster_Clear();')
table=[]
for name,expr,record in [
 ('push','Raster_Push(0,1,2)',[0,1,2,0,0,1]),
 ('extended mask','Raster_PushEx(10,3,4,5,6,255)',[10,3,4,5,6,31]),
 ('window raw','Raster_PushWindowRaw(20,7,8,KQ_RASTER_WIN_SHOW)',[20,0,0,7,8,6]),
 ('window screen','Raster_PushWindowScreen(30,24,40,KQ_RASTER_WIN_HIDE)',[30,0,0,31,40,10]),
 ('bg and window','Raster_PushBgWindowScreen(40,5,6,24,48,KQ_RASTER_WIN_SHOW)',[40,5,6,31,48,7]),
 ('color payload','Raster_PushBgColor0(50,0xFC1F)',[50,31,252,0,0,16]),
 ('window byte wrap','Raster_PushWindowScreen(60,249,255,128)',[60,0,0,0,255,2]),
 ('last visible line','Raster_Push(143,255,254)',[143,255,254,0,0,1])]:check(name,expr,0);table+=record
check('capacity','Raster_GetCount()',8);check('full before ordering','Raster_Push(1,0,0)',1);check('invalid LY before full','Raster_Push(255,0,0)',2)
code('IE=16;');check('commit returns last error','Raster_Commit()',2);check('commit preserves other IE','IE',19)
code('Raster_Disable();');check('disabled count','Raster_GetCount()',0);check('disabled error','Raster_GetLastError()',0);check('disabled STAT','STAT&64',0);check('disable keeps IE','IE',19)
check('empty commit','Raster_Commit()',0);check('done','0xA55A',42330)
rows=[]
for variant,flags in [('default',[]),('unoptimized',['-O0']),('stack',['--abi=stack'])]:
 folder=OUT/variant;folder.mkdir(exist_ok=True);source=folder/'case.c';rom=folder/'case.gb'
 source.write_text('#include "scroll.c"\n#include "raster.c"\n__location(0xFF40) u8 LCDC;\n__location(0xFF41) u8 STAT;\n__location(0xFFFF) u8 IE;\n__location(0xC600) u16 result['+str(len(expected))+'];\nvoid main(){'+''.join(steps)+'while(1){}}',encoding='ascii')
 cmd=[compiler,source,'-I',compiler.parent/'lib','-o',rom,'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--no-cache','--no-disasm']+flags
 p=subprocess.run(list(map(str,cmd)),capture_output=True,cwd=folder,timeout=120);assert p.returncode==0,(p.stdout+p.stderr)[-2200:]
 mapping=(folder/'case.map').read_text();address=int(re.search(r'^([0-9A-F]+)\s+.*\b__kq_scroll_split_table\s*$',mapping,re.M)[1],16)
 for mode in ['dmg','cgb']:
  report=folder/(mode+'.json');cmd=[emulator,rom,'--hardware',mode,'--run-frames','60','--dump-report',report,'--report-sections','meta,watched_memory','--watch-fields','preview']
  for start in range(0,len(expected)*2,16):cmd+=['--watch-window',f'r{start}:{0xC600+start}:{min(16,len(expected)*2-start)}']
  for start in range(0,48,16):cmd+=['--watch-window',f't{start}:{address+start}:16']
  p=subprocess.run(list(map(str,cmd)),capture_output=True,cwd=folder,timeout=120);assert p.returncode==0,p.stderr[-1000:]
  watches={w['name']:w['preview_bytes'] for w in json.loads(report.read_text())['watched_memory']}
  raw=sum([watches['r'+str(n)] for n in range(0,len(expected)*2,16)],[]);actual=[raw[i]+256*raw[i+1] for i in range(0,len(raw),2)];actual_table=sum([watches['t'+str(n)] for n in range(0,48,16)],[])
  passed=actual==expected and actual_table==table
  row=dict(platform='gb',variant=variant,mode=mode,passed=passed,actual=actual,expected=expected,checks=names,table=actual_table,expected_table=table,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),input_sha256=dependencies(source,compiler.parent/'lib'),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator));rows.append(row)
  print(variant,mode,'PASS' if passed else 'FAIL',[(names[i],a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b],actual_table if actual_table!=table else '',flush=True)
  if passed:report.unlink()
  (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=rows),indent=2),encoding='utf-8')
raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
