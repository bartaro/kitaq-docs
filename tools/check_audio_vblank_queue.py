"""Execute producer boundary, bank, interrupt and long-playback checks in DMG/CGB."""
from pathlib import Path
import hashlib,json,subprocess
from check_sound_examples import SITE,REPOS,measure
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=SITE/'verification/api-audio-queue';out.mkdir(parents=True,exist_ok=True)
    source=SITE/'samples/api-examples/gb/audio_vblank_queue.c'
    compiler=REPOS/'kitaqgb/kitaqgb.exe';emulator=REPOS/'kokura/kokura-cli.exe';lib=compiler.parent/'lib'
    rows=[]
    for variant,flags in [('default',[]),('unoptimized',['-O0']),('stack',['--abi=stack'])]:
        folder=out/variant;folder.mkdir(exist_ok=True);rom=folder/'example.gb'
        cmd=[str(compiler),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=128k','--no-cache','--no-disasm']+flags
        build=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120)
        (folder/'build.txt').write_bytes(build.stdout+build.stderr)
        if build.returncode:raise RuntimeError((build.stdout+build.stderr).decode(errors='replace')[-3500:])
        for mode in ['dmg','cgb']:
            report=folder/(mode+'.json');audio=folder/(mode+'.wav');image=folder/(mode+'.png')
            run=subprocess.run([str(emulator),str(rom),'--hardware',mode,'--run-frames','330','--record-wav',str(audio),'--png',str(image),'--dump-report',str(report),'--report-sections','meta,watched_memory','--watch-fields','preview','--watch-window','data:50688:16','--watch-window','done:50815:1'],cwd=folder,capture_output=True,timeout=120)
            (folder/(mode+'-run.txt')).write_bytes(run.stdout+run.stderr)
            assert run.returncode==0
            watches={w['name']:w['preview_bytes'] for w in json.loads(report.read_text(encoding='utf-8'))['watched_memory']}
            actual=watches['data'][:7];expected=[0,49,0,0,1,1,0]
            playing=measure(audio,1.0,1.2);stopped=measure(audio,4.8,5.0)
            passed=actual==expected and watches['done']==[165] and all(m['ac_rms']>100 for m in playing) and all(m['difference_rms']<1 for m in stopped)
            row=dict(variant=variant,mode=mode,actual=actual,expected=expected,done=watches['done'],playing=playing,stopped=stopped,passed=passed,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),audio=audio.relative_to(SITE).as_posix(),audio_sha256=sha(audio),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),input_sha256=dependencies(source,lib))
            rows.append(row);print(variant,mode,'PASS' if passed else 'FAIL',actual,flush=True)
            (out/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=rows,passed=all(r['passed'] for r in rows)),indent=2),encoding='utf-8')
        cleanup_build_outputs(folder)
    raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
if __name__=='__main__':main()
