"""Compare complete OAM buffers against an independent priority-order oracle."""
from pathlib import Path
import hashlib,json,subprocess
from api_build_cleanup import cleanup_build_outputs

SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
OUT=SITE/'verification/api-sprite-order/state';OUT.mkdir(parents=True,exist_ok=True)
LIB=REPOS/'kitaqgb/lib';COMPILER=REPOS/'kitaqgb/kitaqgb.exe';EMU=REPOS/'kokura/kokura-cli.exe'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()

def regular(n):
    return [[8+(i%16)*8,40,i,(i*17)&255,(i*3)%4] for i in range(n)]

edge=[[-8,40,1,0,0],[-7,40,2,0,0],[159,40,3,0,0],[160,40,4,0,0],
      [-32768,40,5,0,0],[32767,40,6,0,0],[40,-16,7,0,0],[40,-15,8,0,0],
      [40,-8,9,0,0],[40,-7,10,0,0],[40,143,11,0,0],[40,144,12,0,0],
      [40,-32768,13,0,0],[40,32767,14,0,0],[40,40,15,0,4],[40,40,16,0,255]]
cases=[]
def add(name,inputs,capacity=255,height=8,phase=0,limit=40,mode=0):
    cases.append(dict(name=name,inputs=inputs,capacity=capacity,height=height,phase=phase,limit=limit,mode=mode))
add('empty',[],phase=255)
add('one',regular(1),phase=255)
add('four-priority-bands',regular(32))
add('rotated-bands',regular(32),phase=17)
add('phase-normalization',regular(7),phase=255)
add('zero-limit',regular(15),phase=14,limit=0)
add('one-output',regular(15),phase=7,limit=1)
add('limit-clamped-to-40',regular(64),phase=63,limit=255)
add('capacity-full',regular(12),capacity=3,phase=2)
add('maximum-255-items',regular(255),phase=254)
add('clip-8-pixels',edge,height=8,phase=2)
add('clip-16-pixels',edge,height=16,phase=4)
add('zero-capacity',regular(3),capacity=0,phase=23)
add('bad-height',regular(3),height=12,phase=25)
add('null-item-storage',regular(3),phase=12,mode=1)
add('count-exceeds-capacity',regular(3),capacity=3,phase=14,mode=2)
add('begin-preserves-phase',regular(12),phase=11,mode=3)

def expected(case):
    enabled=case['capacity']>0 and case['height'] in [8,16] and case['mode']!=1
    accepted=[]
    if enabled:
        for x,y,tile,flags,priority in case['inputs']:
            if len(accepted)<case['capacity'] and -8<x<160 and -case['height']<y<144 and priority<4:
                accepted.append([y+16,x+8,tile,flags,priority])
    count=len(accepted);phase=case['phase'];init=int(enabled);pushed=count
    if case['mode']==2:count=case['capacity']+1
    if case['mode']==3:count=0;accepted=[]
    if not enabled or case['mode']==2:
        output=[0xCC]*168;written=0
    else:
        if count:
            phase%=count
            cyclic=accepted[phase:]+accepted[:phase]
            chosen=sorted(cyclic,key=lambda item:item[4])[:min(case['limit'],40)]
            phase=(phase+1)%count
        else:chosen=[];phase=0
        written=len(chosen)
        output=[0xCC]*4+[byte for item in chosen for byte in item[:4]]+[0]*(160-written*4)+[0xCC]*4
    return output+[init,pushed,count,phase,written,0xA5]

inputs=[];metadata=[]
for case in cases:
    metadata.append([len(inputs),len(case['inputs']),case['capacity'],case['height'],case['phase'],case['limit'],case['mode']])
    inputs+=case['inputs']
source_text='''#pragma fixed_bank 0
#include "sprite_order.c"
typedef __packed struct {s16 x; s16 y; u8 tile; u8 flags; u8 priority;} Input;
typedef __packed struct {u16 start; u8 count; u8 capacity; u8 height; u8 phase; u8 limit; u8 mode;} Test;
__location(0xC800) SpriteOrderItem items[255];
__location(0xCD00) SpriteOrderOamEntry guarded[42];
__location(0xCDB0) SpriteOrder order;
__location(0xD000) u8 result[2958];
__location(0xDD00) u8 status[8];
__prg_rom Input inputs[]={INPUTS};
__prg_rom Test cases[]={CASES};
void main(){
 u8 k; u8 i; u8 j; u8 init; u8 accepted; u8 written; u16 base; Input* input; Test* test;
 status[0]=(u8)sizeof(SpriteOrderItem);status[1]=(u8)sizeof(SpriteOrderOamEntry);
 for(k=0;k<17;k++){
  test=&cases[k];
  for(i=0;i<168;i++)((u8*)guarded)[i]=0xCC;
  if(test->mode==1)init=sprite_order_init(&order,0,test->capacity,test->height);
  else init=sprite_order_init(&order,items,test->capacity,test->height);
  order.phase=test->phase;accepted=0;
  for(j=0;j<test->count;j++){
   input=&inputs[test->start+j];
   accepted=(u8)(accepted+sprite_order_push(&order,input->x,input->y,input->tile,input->flags,input->priority));
  }
  if(test->mode==2)order.count=(u8)(order.capacity+1);
  if(test->mode==3)sprite_order_begin(&order);
  written=sprite_order_build(&order,&guarded[1],test->limit);
  base=(u16)k*174;
  for(i=0;i<168;i++)result[base+i]=((u8*)guarded)[i];
  result[base+168]=init;result[base+169]=accepted;result[base+170]=order.count;
  result[base+171]=order.phase;result[base+172]=written;result[base+173]=0xA5;
 }
 status[2]=sprite_order_init(0,items,4,8);
 sprite_order_begin(0);
 status[3]=sprite_order_push(0,10,10,0,0,0);
 status[4]=sprite_order_build(0,&guarded[1],40);
 sprite_order_init(&order,items,4,8);order.phase=3;
 status[5]=sprite_order_build(&order,0,40);status[6]=order.phase;
 status[7]=0xA5;
 while(1){}
}
'''.replace('INPUTS',','.join('{'+','.join(map(str,row))+'}' for row in inputs)).replace('CASES',','.join('{'+','.join(map(str,row))+'}' for row in metadata))
records=[]
# A partial or interrupted matrix must never be recorded as a complete pass.
(OUT/'results.json').write_text(json.dumps(dict(records=[],passed=False)),encoding='utf-8')
for variant,flags in [('default',[]),('O0',['-O0']),('stack',['--abi=stack'])]:
    folder=OUT/variant;folder.mkdir(exist_ok=True);source=folder/'case.c';source.write_text(source_text,encoding='ascii');rom=folder/'case.gb'
    command=[str(COMPILER),str(source),'-I',str(LIB),'-o',str(rom),'--no-cache','--no-disasm','--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=128k',*flags]
    run=subprocess.run(command,cwd=folder,capture_output=True,timeout=120);(folder/'build.log').write_bytes(run.stdout+run.stderr)
    if run.returncode:raise AssertionError((run.stdout+run.stderr).decode(errors='replace')[-5000:])
    for mode in ['dmg','cgb']:
        report=folder/(mode+'.json')
        command=[str(EMU),str(rom),'--hardware',mode,'--run-frames','600','--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview']
        # The preview field exposes at most 16 bytes per watch, so collect
        # adjacent bounded windows instead of mistaking a preview for a dump.
        size=len(cases)*174
        for offset in range(0,size,16):command+=['--watch-window',f'bytes{offset}:0x{0xD000+offset:04X}:{min(16,size-offset)}']
        command+=['--watch-window','status:0xDD00:8']
        run=subprocess.run(command,cwd=folder,capture_output=True,timeout=120);assert run.returncode==0,run.stderr
        data=json.loads(report.read_text(encoding='utf-8'));windows=data['watched_memory']
        results=[];raw=[byte for window in windows[:-1] for byte in window['preview_bytes']]
        assert len(raw)==size
        for i,case in enumerate(cases):
            actual=raw[i*174:(i+1)*174];want=expected(case)
            results.append(dict(name=case['name'],actual=actual,expected=want,passed=actual==want))
        status=windows[-1]['preview_bytes'];okay=all(r['passed'] for r in results) and status==[5,4,0,0,0,0,3,0xA5]
        row=dict(variant=variant,mode=mode,passed=okay,cases=results,status=status,frames=data['meta']['frames_executed'],source_sha256=sha(source),rom_sha256=sha(rom),compiler_sha256=sha(COMPILER),emulator_sha256=sha(EMU))
        records.append(row)
        (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),library_sha256={p:sha(LIB/p) for p in ['sprite_order.c','sprite_order.h']},inputs_sha256=hashlib.sha256(json.dumps(cases,sort_keys=True).encode()).hexdigest(),records=records,passed=len(records)==6 and all(r['passed'] for r in records)),indent=2),encoding='utf-8')
        print(variant,mode,'PASS' if okay else 'FAIL',status,[(r['name'],next((n for n,(a,b) in enumerate(zip(r['actual'],r['expected'])) if a!=b),None),len(r['actual'])) for r in results if not r['passed']],flush=True)
        if not okay:raise SystemExit(1)
        report.unlink()
    cleanup_build_outputs(folder)
