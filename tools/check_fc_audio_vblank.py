"""Prove automatic NMI music with a stalled foreground producer and captured PCM."""
from pathlib import Path
import argparse,hashlib,json,subprocess,wave,struct,math
from check_batch200 import dependencies
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
ap=argparse.ArgumentParser();ap.add_argument('--compiler',type=Path,default=REPOS/'kitaqfc/kitaqfc.exe');opt=ap.parse_args()
compiler=opt.compiler.resolve();emulator=REPOS/'kurosaki/kurosaki.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=SITE/'verification/api-fc-audio-vblank/example';out.mkdir(parents=True,exist_ok=True)
source=SITE/'samples/api-examples/fc/audio_vblank.c';lib=REPOS/'kitaqfc/lib/audio_vblank.c'
rows=[]
for mode,flags in [('nrom',[]),('mmc3',['--library-lto-lite']),('nrom-O0',['-O0'])]:
 folder=out/mode;folder.mkdir(exist_ok=True);rom=folder/'example.nes';snapshot=folder/'snapshot.json';image=folder/'screen.png';wav=folder/'music.wav'
 command=[str(compiler),str(lib),str(source),'-I',str(lib.parent),'-I',str(SITE/'samples'),'-o',str(rom),'--mapper='+mode.split('-')[0],'--nes-chr='+str(SITE/'samples/font.chr'),'--no-cache','--no-disasm']+flags
 p=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-3500:])
 p=subprocess.run([str(emulator),'run',str(rom),'--frames','300','--snapshot',str(snapshot),'--png',str(image)],capture_output=True,timeout=120,cwd=folder)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-2500:])
 p=subprocess.run([str(emulator),'audio-export',str(rom),'--frames','300','--wav',str(wav)],capture_output=True,timeout=120,cwd=folder)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-2500:])
 state=json.loads(snapshot.read_text());ram=state['bus']['ram'];actual=[ram[0x700+i] for i in [0,1,2,3,4,5,6,7,15]];expected=[1,7,0,1,0,1,1,0,165]
 labels=[(1,1,'NMI MUSIC / FOUR CHANNELS'),(1,4,'CH1 PULSE 1 / CH2 PULSE 2'),(1,6,'CH3 TRIANGLE / CH4 NOISE'),(1,9,'RAM QUEUE: SEVEN RECORDS'),(1,11,'90 FRAMES WITHOUT REFILL'),(1,15,'PHRASE COMPLETE / SILENT'),(1,17,'UNDERRUNS 0 / MATH OK')]
 errors=check_pixels(image,labels,'fc')
 with wave.open(str(wav),'rb') as w:
  assert w.getsampwidth()==2;rate=w.getframerate();channels=w.getnchannels();raw=w.readframes(w.getnframes())
 samples=struct.unpack('<'+'h'*(len(raw)//2),raw)
 def stats(a,b):
  values=samples[int(a*rate)*channels:int(b*rate)*channels]
  return dict(peak=max(map(abs,values),default=0),rms=math.sqrt(sum(v*v for v in values)/max(1,len(values))))
 segments={name:stats(a,b) for name,a,b in [('during_busy',0.6,1.3),('after_refill',2,3),('after_end',4.2,4.8)]}
 inputs=dependencies(source,lib.parent);inputs['kitaqfc/lib/audio_vblank.c']=sha(lib);inputs['samples/font.chr']=sha(SITE/'samples/font.chr')
 row=dict(platform='fc',mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),audio=wav.relative_to(SITE).as_posix(),audio_sha256=sha(wav),input_sha256=inputs,compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),actual=actual,expected=expected,label_pixel_mismatches=errors,audio_segments=segments,passed=actual==expected and errors==0 and segments['during_busy']['rms']>100 and segments['after_refill']['rms']>100 and segments['after_end']['peak']==0)
 rows.append(row);print(mode,'PASS' if row['passed'] else 'FAIL',actual,'pixels',errors,segments,flush=True)
 if row['passed']:snapshot.unlink();cleanup_build_outputs(folder)
 (out/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=rows),indent=2),encoding='utf-8')
raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
