"""Replay menu acceptance, cancellation, wrapping and held-key behavior in DMG/CGB."""
from pathlib import Path
import json,subprocess,hashlib
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-batch100';rows=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for kind in ['state','run','yesno','inventory']:
 source=SITE/'samples/api-examples/gb'/('batch_menu_'+kind+'.c');rom=OUT/('gb-menu_'+kind)/'example.gb'
 for name,sequence,index in [('accept','NONE:30;A:10;NONE:140',0),('cancel','NONE:30;B:10;NONE:140',255),('up_wrap','NONE:30;UP:10;NONE:10;A:10;NONE:120',1 if kind=='yesno' else 2),('hold_down','NONE:30;DOWN:60;NONE:10;A:10;NONE:70',1),('held_a','A:180',0),('both','NONE:30;A,B:10;NONE:140',255 if kind=='state' else 0),('down_accept','NONE:30;DOWN,A:10;NONE:140',1)]:
  expected=[index]
  if kind=='state':expected += [1 if index==255 else 0,255,255,0]
  elif kind=='run':expected += [0,255]
  elif kind=='inventory':expected += [42,255]
  expected += [0]*(79-len(expected))+[0xA55A]
  for mode in ['dmg','cgb']:
   folder=OUT/'state'/('menu-'+kind+'-'+name+'-'+mode);folder.mkdir(parents=True,exist_ok=True);report=folder/'runtime.json'
   exe=REPOS/'kokura/kokura-cli.exe';command=[str(exe),str(rom),'--hardware',mode,'--run-frames','180','--input-seq',sequence,'--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview']
   for offset in range(0,160,16):command+=['--watch-window',f'r{offset}:{0xC600+offset}:16']
   result=subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
   if result.returncode:raise RuntimeError(kind+' '+name)
   state=json.loads(report.read_text(encoding='utf-8'));watches={w['name']:w['preview_bytes'] for w in state['watched_memory']};raw=sum([watches['r'+str(i)] for i in range(0,160,16)],[])
   actual=[raw[i]+raw[i+1]*256 for i in range(0,160,2)]
   row={'name':kind+'-'+name,'mode':mode,'input_sequence':sequence,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),'actual':actual,'expected':expected,'passed':actual==expected,'emulator_sha256':sha(exe)}
   rows.append(row);print(kind,name,mode,'PASS' if row['passed'] else 'FAIL',flush=True)
   (OUT/'menu_input_checks.json').write_text(json.dumps({'records':rows,'script_sha256':sha(Path(__file__))},indent=2),encoding='utf-8')
if len(rows)!=56 or not all(r['passed'] for r in rows):raise SystemExit(1)
