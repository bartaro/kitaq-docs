"""Exercise channel tables, delay boundaries and SPSC queue control on real ROMs.

The deterministic state fixtures disable NMI and call the consumer explicitly.
The separate example checker verifies actual automatic NMI playback and PCM.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
ap=argparse.ArgumentParser();ap.add_argument('--compiler',type=Path,default=REPOS/'kitaqfc/kitaqfc.exe');opt=ap.parse_args()
compiler=opt.compiler.resolve();emulator=REPOS/'kurosaki/kurosaki.exe';lib=REPOS/'kitaqfc/lib/audio_vblank.c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=SITE/'verification/api-fc-audio-vblank/state';out.mkdir(parents=True,exist_ok=True)
prefix='''#include "audio_vblank.h"
#include "intrinsics.h"
__location(0x0700) u8 result[16];
u8 record[5];
__prg_rom const u8 phrase[10]={1,24,254,254,254,2,28,255,255,255};
void check(u8 value){result[0]++;if(value==0)result[1]++;}
void main(){u8 i;u16 j;__ppu_mask_set(0);__ppu_ctrl_set(0);nes_audio_vblank_init();
'''
boundary='''
check(nes_audio_vblank_free()==7);check(nes_audio_vblank_queued()==0);
check(nes_audio_vblank_is_playing()==0);check(nes_audio_vblank_underruns()==0);
record[0]=1;record[1]=24;record[2]=255;record[3]=255;record[4]=255;
check(nes_audio_vblank_enqueue(0)==0);
record[1]=72;check(nes_audio_vblank_enqueue(record)==0);record[1]=24;
record[4]=32;check(nes_audio_vblank_enqueue(record)==0);record[4]=255;
for(i=0;i<7;i++)check(nes_audio_vblank_enqueue(record)==1);
check(nes_audio_vblank_free()==0);check(nes_audio_vblank_enqueue(record)==0);
nes_audio_vblank_start();__nes_audio_vblank_tick();
check(nes_audio_vblank_queued()==6);check(nes_audio_vblank_enqueue(record)==1);
for(i=0;i<7;i++)__nes_audio_vblank_tick();
check(nes_audio_vblank_queued()==0);__nes_audio_vblank_tick();
check(nes_audio_vblank_underruns()==1);
for(j=0;j<300;j++)__nes_audio_vblank_tick();
check(nes_audio_vblank_underruns()==1);check(nes_audio_vblank_is_playing()==1);
check(nes_audio_vblank_enqueue(record)==1);__nes_audio_vblank_tick();
check(nes_audio_vblank_underruns()==1);__nes_audio_vblank_tick();
check(nes_audio_vblank_underruns()==2);
for(j=0;j<260;j++){nes_audio_vblank_enqueue(record);__nes_audio_vblank_tick();__nes_audio_vblank_tick();}
check(nes_audio_vblank_underruns()==255);
nes_audio_vblank_stop();check(nes_audio_vblank_is_playing()==0);check(nes_audio_vblank_queued()==0);
check(nes_audio_vblank_refill()==0);
check(nes_audio_vblank_set_music(0,1,0)==0);check(nes_audio_vblank_set_music(phrase,0,0)==0);
check(nes_audio_vblank_set_music(phrase,13108,0)==0);
record[1]=72;check(nes_audio_vblank_play_music(record,1,0)==0);
check(nes_audio_vblank_is_playing()==0);record[1]=24;
check(nes_audio_vblank_set_music(phrase,2,0)==1);check(nes_audio_vblank_refill()==3);
check(nes_audio_vblank_refill()==0);nes_audio_vblank_start();
__nes_audio_vblank_tick();check(nes_audio_vblank_queued()==2);
__nes_audio_vblank_tick();check(nes_audio_vblank_queued()==1);
__nes_audio_vblank_tick();check(nes_audio_vblank_is_playing()==1);
__nes_audio_vblank_tick();check(nes_audio_vblank_is_playing()==0);
check(nes_audio_vblank_play_music(phrase,2,1)==1);check(nes_audio_vblank_queued()==7);
for(j=0;j<100;j++){__nes_audio_vblank_tick();nes_audio_vblank_refill();}
check(nes_audio_vblank_is_playing()==1);
nes_audio_vblank_stop();record[0]=255;check(nes_audio_vblank_enqueue(record)==1);
nes_audio_vblank_start();__nes_audio_vblank_tick();record[0]=0;nes_audio_vblank_enqueue(record);
for(j=0;j<254;j++)__nes_audio_vblank_tick();check(nes_audio_vblank_is_playing()==1);
__nes_audio_vblank_tick();check(nes_audio_vblank_is_playing()==0);
check(nes_audio_vblank_set_timbre(4,0)==0);check(nes_audio_vblank_set_timbre(0,0x8C)==1);
check(nes_audio_vblank_set_timbre(1,0x4A)==1);check(nes_audio_vblank_set_timbre(2,0)==1);
check(nes_audio_vblank_set_timbre(2,1)==1);check(nes_audio_vblank_set_timbre(3,8)==1);
nes_audio_vblank_init();check(nes_audio_vblank_underruns()==0);
'''
channels='''
record[0]=1;record[1]=255;record[2]=255;record[3]=255;record[4]=255;
nes_audio_vblank_start();
for(i=0;i<72;i++){
    record[1]=i;record[2]=i;record[3]=i;record[4]=i&31;
    nes_audio_vblank_enqueue(record);__nes_audio_vblank_tick();
}
record[1]=255;record[2]=255;record[3]=255;record[4]=255;
nes_audio_vblank_enqueue(record);__nes_audio_vblank_tick();
record[1]=254;record[2]=254;record[3]=254;record[4]=254;
nes_audio_vblank_enqueue(record);__nes_audio_vblank_tick();
check(nes_audio_vblank_queued()==0);check(nes_audio_vblank_underruns()==0);
'''
rows=[]
for variant,flags in [('default',[]),('unoptimized',['-O0'])]:
 for name,body in [('boundary',boundary),('channels',channels)]:
  folder=out/(variant+'-'+name);folder.mkdir(exist_ok=True)
  source=folder/'case.c';rom=folder/'case.nes';snapshot=folder/'snapshot.json'
  source.write_text(prefix+body+'result[15]=165;while(1){}}',encoding='ascii')
  p=subprocess.run([str(compiler),str(lib),str(source),'-I',str(lib.parent),'-o',str(rom),'--mapper=nrom','--no-cache','--no-disasm']+flags,capture_output=True,timeout=90,cwd=folder)
  if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-2500:])
  p=subprocess.run([str(emulator),'run',str(rom),'--frames','240','--headless','--snapshot',str(snapshot)],capture_output=True,timeout=120,cwd=folder);assert p.returncode==0
  state=json.loads(snapshot.read_text());ram=state['bus']['ram'];actual=[ram[0x700],ram[0x701],ram[0x70F]]
  row=dict(name=name,variant=variant,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),actual=actual,passed=actual[1:]==[0,165] and actual[0]>0)
  if name=='channels':
   trace=folder/'trace.jsonl'
   p=subprocess.run([str(emulator),'trace',str(rom),'--frames','30','--out',str(trace),'--apu'],capture_output=True,timeout=120,cwd=folder);assert p.returncode==0
   events=[json.loads(line) for line in trace.read_text().splitlines()]
   writes=[(e['addr'],e['value']) for e in events if e.get('kind')=='apu.reg_write' and e.get('addr') in [0x4002,0x4003,0x4006,0x4007,0x400A,0x400B,0x400E,0x400F]]
   expected=[]
   for note in range(72):
    f=440*2**((note+36-69)/12);pulse=round(1789773/(16*f)-1);triangle=round(1789773/(32*f)-1)
    noise=(note&15)|(128 if note&16 else 0)
    expected += [(0x4002,pulse&255),(0x4003,pulse>>8),(0x4006,pulse&255),(0x4007,pulse>>8),(0x400A,triangle&255),(0x400B,triangle>>8),(0x400E,noise),(0x400F,0)]
   row.update(channel_writes=writes,expected_writes=expected,channel_write_count=len(writes))
   row['passed'] &= writes==expected
   if row['passed']:trace.unlink()
  print(variant,name,'PASS' if row['passed'] else 'FAIL',actual,row.get('channel_write_count'),flush=True)
  if row['passed']:snapshot.unlink()
  rows.append(row)
  (out/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),library_sha256=sha(lib),header_sha256=sha(lib.with_suffix('.h')),records=rows),indent=2),encoding='utf-8')
raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
