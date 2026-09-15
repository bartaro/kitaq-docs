"""Build original sound lessons and verify captured PCM and observable state.

Uses only the Python standard library for audio. No native audio backend is loaded.
"""
from pathlib import Path
import argparse,array,hashlib,json,math,os,subprocess,sys,wave
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs
from check_entity_callbacks import check_pixels
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists(): REPOS=SITE.parent
OUT=SITE/'verification/api-sound'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def pcm(path):
    with wave.open(str(path),'rb') as f:
        assert f.getsampwidth()==2 and f.getcomptype()=='NONE'
        rate,channels=f.getframerate(),f.getnchannels()
        samples=array.array('h',f.readframes(f.getnframes()))
    if sys.byteorder!='little':samples.byteswap()
    return rate,[samples[ch::channels] for ch in range(channels)]

def measure(path,start,end):
    rate,channels=pcm(path);result=[]
    for data in channels:
        segment=data[int(start*rate):int(end*rate)]
        assert segment
        mean=sum(segment)/len(segment)
        result.append({'rms':math.sqrt(sum(x*x for x in segment)/len(segment)),
                       'ac_rms':math.sqrt(sum((x-mean)**2 for x in segment)/len(segment)),
                       'peak':max(abs(x) for x in segment),
                       'difference_rms':math.sqrt(sum((b-a)**2 for a,b in zip(segment,segment[1:]))/(len(segment)-1)),
                       'positive_crossings':sum(a<=mean<b for a,b in zip(segment,segment[1:])),
                       'frames':len(segment)})
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case');args=parser.parse_args()
    specs=json.loads((SITE/'tools/api_descriptions/sound_examples.json').read_text(encoding='utf-8'))
    records=[]
    for spec in specs:
        group=spec['group']
        if args.case and group!=args.case:continue
        platform=spec['platform'];folder=OUT/group;folder.mkdir(parents=True,exist_ok=True)
        source=SITE/spec['source'];compiler=REPOS/('kitaq'+platform)/('kitaq'+platform+'.exe')
        emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
        rom=folder/('example.'+spec.get('container','gb' if platform=='gb' else 'nes'));lib=compiler.parent/'lib'
        cmd=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),
             *[flag.replace('{SITE}',str(SITE)) for flag in spec['build_flags']]]
        build=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120)
        (folder/'build.txt').write_bytes(build.stdout+build.stderr)
        if build.returncode:raise RuntimeError(group+': '+(build.stdout+build.stderr).decode('utf-8',errors='replace')[-2200:])
        for mode in spec['modes']:
            sub=folder/mode;sub.mkdir(exist_ok=True);audio=sub/'sound.wav';image=sub/'screen.png';report=sub/'runtime.json'
            environment=None
            if spec.get('container')=='fds':
                # KUROSAKI direct-boots this disk's RAM image and redirects vectors.
                # The all-zero test fixture supplies no firmware routines and is
                # deliberately not distributed as a replacement device BIOS.
                stub=folder/'empty-firmware-fixture.bin';stub.write_bytes(bytes(8192))
                environment={**os.environ,'KUROSAKI_DISKSYS_ROM':str(stub)}
            if platform=='gb':
                cmd=[str(emulator),str(rom),'--hardware',mode,'--run-frames',str(spec['frames']),
                    '--record-wav',str(audio),
                    '--png',str(image),'--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview']
                for offset in range(0,128,16):cmd+=['--watch-window',f'r{offset}:{0xC600+offset}:16']
                run=subprocess.run(cmd,cwd=sub,capture_output=True,timeout=120,env=environment)
                (sub/'run.txt').write_bytes(run.stdout+run.stderr);assert run.returncode==0,(group,mode)
                state=json.loads(report.read_text(encoding='utf-8'));watches={w['name']:w['preview_bytes'] for w in state['watched_memory']}
                raw=sum([watches['r'+str(i)] for i in range(0,128,16)],[])
            else:
                cmd=[str(emulator),'run',str(rom),'--frames',str(spec['frames']),'--headless','--snapshot',str(report),'--png',str(image)]
                run=subprocess.run(cmd,cwd=sub,capture_output=True,timeout=120,env=environment)
                (sub/'run.txt').write_bytes(run.stdout+run.stderr);assert run.returncode==0,(group,mode)
                raw=json.loads(report.read_text(encoding='utf-8'))['bus']['ram'][0x600:0x680]
                cmd=[str(emulator),'audio-export',str(rom),'--frames',str(spec['frames']),'--wav',str(audio)]
                run=subprocess.run(cmd,cwd=sub,capture_output=True,timeout=120,env=environment)
                (sub/'audio.txt').write_bytes(run.stdout+run.stderr);assert run.returncode==0,group
            expected=spec['expected']+[0]*(127-len(spec['expected']))+[0xA5]
            checks=[]
            for segment in spec['segments']:
                metrics=measure(audio,segment['start'],segment['end']);kind=segment['kind']
                if kind=='silent':passed=all(m['peak']<=segment.get('max_peak',0) for m in metrics)
                elif kind=='tone':passed=all(m['ac_rms']>100 for m in metrics)
                elif kind in ('left','right'):
                    active=0 if kind=='left' else 1;other=1-active
                    # A DMG high-pass transient decays after switching routing.
                    # Require no periodic tone in the off side, not zero DC residue.
                    passed=(metrics[active]['ac_rms']>100 and
                            metrics[other]['difference_rms']<metrics[active]['difference_rms']*0.03 and
                            metrics[other]['positive_crossings']<=2)
                else:raise ValueError(kind)
                if 'hz' in segment:
                    duration=segment['end']-segment['start']
                    measured=metrics[0]['positive_crossings']/duration
                    passed=passed and abs(measured-segment['hz'])<=segment.get('tolerance_hz',8)
                checks.append({**segment,'metrics':metrics,'passed':passed})
            row={'platform':platform,'group':group,'mode':mode,'source':spec['source'],'source_sha256':sha(source),
                 'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),'image':image.relative_to(SITE).as_posix(),'image_sha256':sha(image),
                 'audio':audio.relative_to(SITE).as_posix(),'audio_sha256':sha(audio),'compiler_sha256':sha(compiler),'emulator_sha256':sha(emulator),
                 'input_sha256':dependencies(source,lib),'actual':raw,'expected':expected,'segments':checks,'frames':spec['frames']}
            import re
            title=re.search(r'sound_begin\("([^"]+)"\)',source.read_text(encoding='utf-8')).group(1)
            row['playback_clip']=spec.get('playback_clip',True)
            row['label_pixel_mismatches']=check_pixels(image,[(1,1,title),(1,3,'EXTERNAL PORT DATA' if not row['playback_clip'] else 'LISTEN TO THE WAV'),(1,5,'SEQUENCE COMPLETE')],platform)
            row['passed']=raw==expected and all(c['passed'] for c in checks) and row['label_pixel_mismatches']==0
            if platform=='fc':row['input_sha256']['samples/font.chr']=sha(SITE/'samples/font.chr')
            if 'midi_bytes' in spec:
                trace=sub/'serial-trace.jsonl'
                run=subprocess.run([str(emulator),'trace',str(rom),'--frames','50','--mem-read','--mem-write','--out',str(trace)],cwd=sub,capture_output=True,timeout=120)
                assert run.returncode==0
                events=[json.loads(line) for line in trace.read_text(encoding='utf-8').splitlines()]
                bits=[r for r in events if r['kind']=='mem.write' and r['addr']==0x4016]
                frames=[bits[i:i+10] for i in range(0,len(bits),10)]
                encoded=[sum(f[j+1]['value']<<j for j in range(8)) for f in frames if len(f)==10]
                cells=[b['cpu_cycle']-a['cpu_cycle'] for f in frames for a,b in zip(f,f[1:])]
                reads=[r for r in events if r['kind']=='mem.read' and r['addr']==0x4017]
                receive_cells=[b['cpu_cycle']-a['cpu_cycle'] for a,b in zip(reads,reads[1:])]
                row['serial']={'bytes':encoded,'expected_bytes':spec['midi_bytes'],'tx_bit_cycles':cells,'rx_read_cycles':receive_cells,
                    'framing':all(len(f)==10 and f[0]['value']==0 and f[-1]['value']==1 for f in frames)}
                row['serial']['passed']=(encoded==spec['midi_bytes'] and row['serial']['framing'] and set(cells)=={57} and receive_cells==[81]+[57]*7)
                row['passed']=row['passed'] and row['serial']['passed']
            records.append(row)
            print(group,mode,'PASS' if row['passed'] else 'FAIL','RAM',[(i,a,b) for i,(a,b) in enumerate(zip(raw,expected)) if a!=b][:12],
                  'audio',[(c['name'],c['passed']) for c in checks],flush=True)
        cleanup_build_outputs(folder)
    target=OUT/((args.case+'-results.json') if args.case else 'results.json')
    target.write_text(json.dumps({'records':records,'script_sha256':sha(Path(__file__))},indent=2),encoding='utf-8')
    raise SystemExit(0 if records and all(r['passed'] for r in records) else 1)
if __name__=='__main__':main()
