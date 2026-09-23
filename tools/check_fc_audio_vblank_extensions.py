"""Execute pause/SFX state contracts and compare APU writes at exact tick boundaries."""
from pathlib import Path
import hashlib,json,subprocess,sys
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-fc-audio-vblank/extensions/state';OUT.mkdir(parents=True,exist_ok=True)
lib=REPOS/'kitaqfc/lib';compiler=lib.parent/'kitaqfc.exe';emu=REPOS/'kurosaki/kurosaki.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prefix='''#include "audio_vblank.c"
#include "intrinsics.h"
__location(0x0700) u8 result[16];
u8 effect[35];
__prg_rom const u8 bg[15]={2,21,17,12,3,2,24,255,255,255,2,26,255,255,255};
__prg_rom const u8 fx[5]={3,45,255,255,255};
void check(u8 ok){result[0]++;if(ok==0)result[1]++;}
void tick(u8 phase){result[14]=phase;__nes_audio_vblank_tick();}
void main(){u8 i;u8 old_delay;u8 old_sfx;u8 old_cursor;
__ppu_mask_set(0);__ppu_ctrl_set(0);nes_audio_vblank_init();
'''
controls='''
check(nes_audio_vblank_play_sfx(0,1,1)==0);
check(nes_audio_vblank_play_sfx(fx,0,1)==0);
check(nes_audio_vblank_play_sfx(fx,8,1)==0);
check(nes_audio_vblank_play_sfx(fx,1,0)==0);
check(nes_audio_vblank_play_sfx(fx,1,16)==0);
check(nes_audio_vblank_is_playing()==0);
check(nes_audio_vblank_play_sfx(fx,1,1)==1);
check(nes_audio_vblank_is_playing()==0);
__nes_audio_vblank_tick();check(nav_sfx_active==1);check(nav_sfx_delay==3);
check(nav_notes[0]==254);check(nav_sfx_notes[0]==45);
effect[0]=0;effect[1]=45;effect[2]=255;effect[3]=255;effect[4]=255;
check(nes_audio_vblank_play_sfx(effect,1,1)==0);check(nav_sfx_delay==3);
effect[0]=1;effect[1]=72;check(nes_audio_vblank_play_sfx(effect,1,1)==0);
effect[1]=45;effect[4]=32;check(nes_audio_vblank_play_sfx(effect,1,1)==0);
effect[4]=255;check(nes_audio_vblank_queued()==0);
nes_audio_vblank_pause(1);old_sfx=nav_sfx_delay;old_cursor=nav_sfx_cursor;
for(i=0;i<9;i++)__nes_audio_vblank_tick();
check(nav_sfx_delay==old_sfx);check(nav_sfx_cursor==old_cursor);check(nav_sfx_active==1);
nes_audio_vblank_pause(0);__nes_audio_vblank_tick();check(nav_sfx_delay==2);
nes_audio_vblank_stop_sfx();__nes_audio_vblank_tick();check(nav_sfx_active==0);check(nav_effective_mask==0);check(nav_enabled==0);
check(nes_audio_vblank_play_music(bg,3,1)==1);__nes_audio_vblank_tick();
check(nes_audio_vblank_play_sfx(fx,1,1)==1);__nes_audio_vblank_tick();
old_delay=nav_delay;old_sfx=nav_sfx_delay;old_cursor=nav_sfx_cursor;
nes_audio_vblank_pause(1);for(i=0;i<11;i++)__nes_audio_vblank_tick();
check(nav_delay==old_delay);check(nav_sfx_delay==old_sfx);check(nav_sfx_cursor==old_cursor);
check(nes_audio_vblank_is_playing()==1);check(nes_audio_vblank_underruns()==0);
nes_audio_vblank_pause(0);__nes_audio_vblank_tick();check(nav_sfx_delay==2);check(nav_notes[0]==24);
nes_audio_vblank_stop();check(nav_active==0);check(nav_sfx_active==0);check(nav_paused==0);check(nav_enabled==0);
check(nes_audio_vblank_queued()==0);check(nes_audio_vblank_refill()==0);
for(i=0;i<7;i++){effect[i*5]=1;effect[i*5+1]=45;effect[i*5+2]=255;effect[i*5+3]=255;effect[i*5+4]=255;}
check(nes_audio_vblank_play_sfx(effect,7,0xF1)==1);check(nav_sfx_mask==1);
effect[1]=12;__nes_audio_vblank_tick();check(nav_sfx_notes[0]==45);
for(i=0;i<6;i++)__nes_audio_vblank_tick();check(nav_sfx_active==1);
__nes_audio_vblank_tick();check(nav_sfx_active==0);check(nav_enabled==0);
// Every physical mask bit owns exactly its channel, including triangle/noise.
effect[0]=1;effect[1]=21;effect[2]=17;effect[3]=12;effect[4]=3;
for(i=0;i<4;i++){
check(nes_audio_vblank_play_sfx(effect,1,(u8)(1<<i))==1);
__nes_audio_vblank_tick();check(nav_enabled==(u8)(1<<i));
__nes_audio_vblank_tick();check(nav_enabled==0);
}
effect[0]=255;check(nes_audio_vblank_play_sfx(effect,1,15)==1);
__nes_audio_vblank_tick();check(nav_enabled==15);
for(i=0;i<254;i++)__nes_audio_vblank_tick();check(nav_sfx_active==1);
__nes_audio_vblank_tick();check(nav_sfx_active==0);check(nav_enabled==0);
check(nes_audio_vblank_set_timbre(3,NES_AUDIO_NOISE_ENVELOPE|15)==1);check(nav_timbre[3]==15);
check(nes_audio_vblank_set_timbre(3,15)==1);check(nav_timbre[3]==63);
'''
overlay='''
nes_audio_vblank_play_music(bg,3,1);tick(1);
nes_audio_vblank_play_sfx(fx,1,1);tick(2);tick(3);tick(4);tick(5);
effect[0]=10;effect[1]=48;effect[2]=255;effect[3]=255;effect[4]=255;
nes_audio_vblank_play_sfx(effect,1,1);tick(6);nes_audio_vblank_stop_sfx();tick(7);
nes_audio_vblank_pause(1);tick(8);nes_audio_vblank_pause(0);tick(9);tick(10);
nes_audio_vblank_stop();tick(11);check(nav_enabled==0);
'''
rows=[]
for variant,flags in [('default',[]),('unoptimized',['-O0']),('no-inline',['--no-small-inline']),('fastcall',['--fastcall-v2'])]:
 for name,body in [('controls',controls),('overlay',overlay)]:
  folder=OUT/(name+'-'+variant);folder.mkdir(exist_ok=True);source=folder/'case.c';rom=folder/'case.nes';state=folder/'state.json'
  source.write_text(prefix+body+'result[15]=165;while(1){}}',encoding='ascii')
  p=subprocess.run([str(compiler),str(source),'-I',str(lib),'-o',str(rom),'--mapper=mmc3','--no-cache','--no-disasm',*flags],cwd=folder,capture_output=True,timeout=90)
  (folder/'build.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0,(p.stdout+p.stderr)[-2000:]
  p=subprocess.run([str(emu),'run',str(rom),'--frames','60','--snapshot',str(state)],cwd=folder,capture_output=True,timeout=90);assert p.returncode==0
  ram=json.loads(state.read_text())['bus']['ram'];actual=[ram[0x700],ram[0x701],ram[0x70f]]
  row=dict(name=name,variant=variant,actual=actual,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),passed=actual[0]>0 and actual[1:]==[0,165])
  if name=='overlay':
   trace=folder/'trace.jsonl';p=subprocess.run([str(emu),'trace',str(rom),'--frames','3','--apu','--mem-write','--out',str(trace)],cwd=folder,capture_output=True,timeout=90);assert p.returncode==0
   phase=0;writes={i:[] for i in range(1,12)}
   for line in trace.open(encoding='utf-8'):
    e=json.loads(line)
    if e.get('kind')=='mem.write' and e.get('addr')==0x70e:phase=e['value']
    if phase in writes and e.get('kind')=='apu.reg_write' and e.get('addr') in [0x4002,0x4006,0x400a,0x400e]:writes[phase].append([e['addr'],e['value']])
   def pulse(n):return round(1789773/(16*440*2**((n+36-69)/12))-1)&255
   def triangle(n):return round(1789773/(32*440*2**((n+36-69)/12))-1)&255
   all_bg=[[0x4002,pulse(21)],[0x4006,pulse(17)],[0x400a,triangle(12)],[0x400e,3]]
   expected={1:all_bg,2:[[0x4002,pulse(45)]],3:[],4:[],5:[[0x4002,pulse(26)]],6:[[0x4002,pulse(48)]],7:all_bg,8:[],9:all_bg,10:[[0x4002,pulse(24)]],11:[]}
   row.update(writes=writes,expected_writes=expected);row['passed'] &= writes==expected
   if row['passed']:trace.unlink()
  rows.append(row);print(name,variant,'PASS' if row['passed'] else 'FAIL',actual,flush=True)
  if not row['passed'] and name=='overlay':print(row['writes'],row['expected_writes'],flush=True)
  if row['passed']:state.unlink()
  (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),compiler_sha256=sha(compiler),emulator_sha256=sha(emu),library_sha256=sha(lib/'audio_vblank.c'),header_sha256=sha(lib/'audio_vblank.h'),records=rows),indent=2),encoding='utf-8')
assert all(r['passed'] for r in rows)
