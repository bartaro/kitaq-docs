"""Check an expansion-input observation program under KUROSAKI's D0-only controller model.

This proves the program builds and distinguishes the ordinary D0 snapshots from
the currently unimplemented D1/microphone signals. It does not verify nonzero
peripheral signals, their electrical timing, or hardware compatibility.
"""
from pathlib import Path
import subprocess,json,hashlib
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
folder=SITE/'verification/api-expansion-input';folder.mkdir(parents=True,exist_ok=True)
source=SITE/'samples/api-examples/fc/expansion_input.c'
compiler=REPOS/'kitaqfc/kitaqfc.exe';emulator=REPOS/'kurosaki/kurosaki.exe'
rom=folder/'example.nes';image=folder/'screen.png';report=folder/'runtime.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for path in [rom,image,report]:path.unlink(missing_ok=True)
command=[str(compiler),str(source),'-I',str(SITE/'samples'),'-I',str(REPOS/'kitaqfc/lib'),'-o',str(rom),'--mapper=nrom','--nes-chr='+str(SITE/'samples/font.chr'),'--no-cache','--no-disasm']
process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
(folder/'build.txt').write_bytes(process.stdout+process.stderr)
result={'platform':'fc','mode':'nrom','source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'compiler_sha256':sha(compiler),'build_command':command,'build_exit':process.returncode,'passed':False,
        'scope':'Build and default KUROSAKI D0-only observation. Nonzero expansion-pad D1 and microphone signals are not emulated here and are not verified by this run.'}
if process.returncode==0:
    timeline=[{'frame':start,'duration':duration,'pad1':p1,'pad2':p2,'reset':False,'disk_side':None,'expected_frame_hash':None} for start,duration,p1,p2 in [(0,30,0,0),(30,40,1,2),(70,110,0,0)]]
    replay={'format':'kurosaki-replay-v1','rom_sha256':sha(rom),'emulator_version':'0.1.0','region':'ntsc','frames':timeline,'expected_final_state_hash':None}
    replay_path=folder/'input.json';replay_path.write_text(json.dumps(replay,indent=2),encoding='utf-8')
    command=[str(emulator),'replay-run',str(rom),str(replay_path),'--frames','180','--png',str(image),'--json',str(report)]
    process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
    (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
    result.update(runtime_exit=process.returncode,run_command=command,input_timeline=timeline,rom_sha256=sha(rom),emulator_sha256=sha(emulator))
    if process.returncode==0 and image.exists():
        labels=[(1,0,'EXPANSION INPUT'),(1,4,'NORMAL P1'),(16,4,'001'),(1,5,'NORMAL P2'),(16,5,'002'),(1,7,'D1 PORT 1'),(1,8,'D1 PORT 2'),(1,9,'EXP ALIAS 1'),(1,10,'EXP ALIAS 2'),(1,12,'MIC LEVEL'),(1,13,'MIC DIRECT'),(1,14,'SIGNAL SNAPSHOT')]+[(16,y,'000') for y in [7,8,9,10,12,13]]
        errors=check_pixels(image,labels,'fc')
        frames=json.loads(report.read_text(encoding='utf-8')).get('frames')
        result.update(image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),expected_labels=labels,pixel_mismatches=errors,frames=frames,passed=errors==0 and frames==180)
if result['passed']:cleanup_build_outputs(folder)
(folder/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('D0-only observation','PASS' if result['passed'] else 'FAIL')
if not result['passed']:raise SystemExit(1)
