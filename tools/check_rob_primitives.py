"""Execute generated FC optical primitives; inspect every PPUMASK write and frame.

These checks establish rendering-mask timing, not reception by a physical robot.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess

SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
ap=argparse.ArgumentParser()
ap.add_argument('--compiler',type=Path,default=REPOS/'kitaqfc/kitaqfc.exe')
ap.add_argument('--output',type=Path,default=SITE/'verification/api-rob/state')
ap.add_argument('--smoke',action='store_true')
opt=ap.parse_args();out=opt.output.resolve();out.mkdir(parents=True,exist_ok=True)
compiler=opt.compiler.resolve();emulator=REPOS/'kurosaki/kurosaki.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cases=[]
def add(name,body,masks,final):cases.append((name,body,masks,final))
for value in [0,1,255]:add('flash-'+str(value),f'__rob_flash({value});',[30 if value else 0],30 if value else 0)
for on,off in [(0,0),(0,3),(3,0),(2,4),(4,2),(1,255),(255,1),(255,255)]:
 add(f'pulse-{on}-{off}',f'__rob_pulse({on},{off});',[30]*on+[0]*off,0 if off else 30 if on else 10)
for value in [0,255,128,64,32,16,8,4,2,1,85,170]:
 masks=[]
 for bit in range(7,-1,-1):masks+=([30]*4+[0]*2) if value&(1<<bit) else ([30]*2+[0]*4)
 add('byte-'+str(value),f'__rob_send_byte({value});',masks,0)
if opt.smoke:cases=[next(c for c in cases if c[0]=='byte-128')]
rows=[]
for variant,flags in [('default',[]),('unoptimized',['-O0'])]:
 if opt.smoke and variant!='default':continue
 for name,body,masks,final in cases:
  folder=out/(variant+'-'+name);folder.mkdir(exist_ok=True)
  source=folder/'case.c';rom=folder/'case.nes';snapshot=folder/'snapshot.json';trace=folder/'trace.jsonl'
  source.write_text('#include "intrinsics.h"\n__location(0x0700) u8 result[4];\nvoid main(){'
   '__ppu_off();__vramq_clear();__oam_clear();__ppu_ctrl_set(0x80);__ppu_mask_set(10);'
   '__nmi_wait();result[0]=17;result[1]=__nmi_ready();'+body+
   'result[2]=__nmi_ready()-result[1];result[3]=__ppu_mask_get();result[0]=165;while(1){}}',encoding='ascii')
  command=[str(compiler),str(source),'-I',str(REPOS/'kitaqfc/lib'),'-o',str(rom),'--no-cache','--no-disasm']+flags
  p=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
  row=dict(name=name,variant=variant,source=str(source),source_sha256=sha(source),build_exit=p.returncode,passed=False)
  if p.returncode:print(p.stdout.decode(errors='replace'),p.stderr.decode(errors='replace'))
  if not p.returncode:
   frames=len(masks)+15
   p=subprocess.run([str(emulator),'run',str(rom),'--frames',str(frames),'--snapshot',str(snapshot),'--headless'],capture_output=True,timeout=120,cwd=folder)
   row['runtime_exit']=p.returncode
   if not p.returncode:
    state=json.loads(snapshot.read_text());ram=state['bus']['ram'];actual=[ram[0x700],ram[0x702],ram[0x703],state['bus']['ppu']['mask']]
    expected=[165,len(masks)%256,final,final]
    row.update(actual=actual,expected=expected,rom_sha256=sha(rom),rom=str(rom))
    p=subprocess.run([str(emulator),'trace',str(rom),'--frames',str(frames),'--out',str(trace),'--ppu'],capture_output=True,timeout=120,cwd=folder)
    events=[json.loads(s) for s in trace.read_text().splitlines()] if trace.exists() else []
    writes=[e for e in events if e.get('kind')=='ppu.reg_write' and e.get('addr')==0x2001]
    # Initialization ends with mask 10. All later writes belong to the primitive.
    start=next((i+1 for i,e in enumerate(writes) if e.get('value')==10),len(writes))
    writes=writes[start:];got=[e['value'] for e in writes];ticks=[e['frame'] for e in writes]
    row.update(mask_writes=got,expected_masks=masks,write_frames=ticks,trace_exit=p.returncode,
      passed=p.returncode==0 and actual==expected and got==masks and len(ticks)==len(masks) and all(b-a==1 for a,b in zip(ticks,ticks[1:])))
    if row['passed']:snapshot.unlink();trace.unlink()
  rows.append(row);print(variant,name,'PASS' if row['passed'] else 'FAIL',flush=True)
  (out/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),header_sha256=sha(REPOS/'kitaqfc/lib/intrinsics.h'),codegen_sha256=sha(REPOS/'kitaqfc/kitaqfc/CodeGenerator.cs'),records=rows),indent=2),encoding='utf-8')
print('Report:',out/'results.json')
raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
