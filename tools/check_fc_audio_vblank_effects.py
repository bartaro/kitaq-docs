"""Validate actual NMI pause/resume, SFX ownership and natural noise decay in recorded PCM."""
from pathlib import Path
import hashlib,json,subprocess,wave,struct,math
from check_batch200 import dependencies
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-fc-audio-vblank/extensions/example';OUT.mkdir(parents=True,exist_ok=True)
lib=REPOS/'kitaqfc/lib';compiler=lib.parent/'kitaqfc.exe';emu=REPOS/'kurosaki/kurosaki.exe'
source=SITE/'samples/api-examples/fc/audio_vblank_effects.c';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
labels=[(1,1,'NMI MUSIC / PAUSE AND SFX'),(1,4,'CH1 BGM 220 HZ / SFX 880 HZ'),(1,7,'SFX ENDS: BGM RETURNS'),(1,10,'PAUSE: SILENT FOR 30 FRAMES'),(1,13,'CH4: ONE SHOT NOISE DECAY'),(1,17,'COMPLETE / ALL CHANNELS OFF')]
rows=[]
for variant,mapper,flags in [('nrom','nrom',[]),('mmc3','mmc3',['--library-lto-lite']),('nrom-O0','nrom',['-O0'])]:
 folder=OUT/variant;folder.mkdir(exist_ok=True);rom=folder/'example.nes';state=folder/'state.json';image=folder/'screen.png';audio=folder/'effects.wav';trace=folder/'trace.jsonl'
 def run(args):
  p=subprocess.run([str(x) for x in args],cwd=folder,capture_output=True,timeout=120)
  assert p.returncode==0,(p.stdout+p.stderr)[-2500:]
 run([compiler,lib/'audio_vblank.c',source,'-I',lib,'-I',SITE/'samples','-o',rom,'--mapper='+mapper,'--nes-chr='+str(SITE/'samples/font.chr'),'--no-cache','--no-disasm',*flags])
 run([emu,'run',rom,'--frames','330','--snapshot',state,'--png',image])
 run([emu,'trace',rom,'--frames','310','--mem-write','--apu','--out',trace])
 run([emu,'audio-export',rom,'--frames','330','--wav',audio])
 phases={};noise_triggers=[]
 for line in trace.open(encoding='utf-8'):
  event=json.loads(line)
  if event.get('kind')=='mem.write' and event.get('addr')==0x710:phases[event['value']]=dict(frame=event['frame'],cycle=event['cpu_cycle'],time=event['cpu_cycle']/1789773)
  if event.get('kind')=='apu.reg_write' and event.get('addr')==0x400f:noise_triggers.append(event['value'])
 assert set(phases)==set(range(1,9));t={k:v['time'] for k,v in phases.items()}
 with wave.open(str(audio),'rb') as w:
  assert w.getsampwidth()==2;rate=w.getframerate();channels=w.getnchannels();raw=w.readframes(w.getnframes())
 values=struct.unpack('<'+'h'*(len(raw)//2),raw)
 def segment(a,b,frequency=None):
  samples=values[int(a*rate)*channels:int(b*rate)*channels:channels]
  peak=max(map(abs,samples));rms=math.sqrt(sum(x*x for x in samples)/len(samples));record=dict(start=a,end=b,peak=peak,rms=rms)
  if frequency:
   threshold=peak*0.25;low=False;edges=[]
   for i,value in enumerate(samples):
    if value < -threshold:low=True
    elif value > threshold and low:edges.append(i);low=False
   measured=(len(edges)-1)*rate/(edges[-1]-edges[0]) if len(edges)>1 else 0
   record.update(expected_hz=frequency,measured_hz=measured,frequency_ok=abs(measured-frequency)/frequency<0.03)
  return record
 segments={
  'background':segment(t[1]+0.1,t[2]-0.06,220),
  'effect':segment(t[2]+0.1,t[2]+0.4,880),
  'automatic_return':segment(t[2]+0.56,t[3]-0.03,220),
  'paused':segment(t[3]+0.15,t[4]-0.03),
  'resumed':segment(t[4]+0.1,t[5]-0.06,220),
  'long_effect':segment(t[5]+0.04,t[6]-0.04,880),
  'explicit_return':segment(t[6]+0.08,t[7]-0.06,220),
  'noise_early':segment(t[7]+0.1,t[7]+0.2),
  'noise_late':segment(t[7]+0.65,t[7]+0.8),
  'noise_decayed':segment(t[7]+1.25,t[8]-0.02),
  'finished':segment(t[8]+0.15,t[8]+0.5)}
 ram=json.loads(state.read_text())['bus']['ram'];actual=[*ram[0x700:0x705],ram[0x70f]];expected=[1,1,1,1,0,165]
 pixels=check_pixels(image,labels,'fc')
 ok=actual==expected and pixels==0 and all(s.get('frequency_ok',True) for s in segments.values())
 ok &= all(segments[k]['peak']==0 for k in ['paused','noise_decayed','finished'])
 ok &= segments['noise_early']['rms']>segments['noise_late']['rms']>100 and noise_triggers==[8]
 ok &= phases[4]['frame']-phases[3]['frame']==30 and phases[6]['frame']-phases[5]['frame']==15
 inputs=dependencies(source,lib);inputs['kitaqfc/lib/audio_vblank.c']=sha(lib/'audio_vblank.c');inputs['samples/font.chr']=sha(SITE/'samples/font.chr')
 row=dict(platform='fc',mode=variant,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),audio=audio.relative_to(SITE).as_posix(),audio_sha256=sha(audio),compiler_sha256=sha(compiler),emulator_sha256=sha(emu),input_sha256=inputs,actual=actual,expected=expected,label_pixel_mismatches=pixels,phases=phases,audio_segments=segments,noise_triggers=noise_triggers,passed=bool(ok))
 rows.append(row);print(variant,'PASS' if ok else 'FAIL',actual,'pixels',pixels,flush=True)
 print(json.dumps(segments),flush=True)
 if ok:state.unlink();trace.unlink();cleanup_build_outputs(folder)
 (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=rows),indent=2),encoding='utf-8')
assert all(r['passed'] for r in rows)
