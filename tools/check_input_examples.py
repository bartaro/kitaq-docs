"""Replay actual controller input and compare each teaching program's displayed observations."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime,timezone
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs

SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
OUTPUT=SITE/'verification/api-input'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--only');opts=ap.parse_args()
    records=[]
    cases=[('gb','input_edges','dmg'),('gb','input_edges','cgb'),('gb','input_raw','dmg'),('gb','input_raw','cgb'),
           ('fc','input_edges','nrom'),('fc','input_raw','nrom'),('fc','pad_repeat','nrom')]
    for platform,name,mode in cases:
        ident=platform+'-'+name+'-'+mode
        if opts.only and ident!=opts.only:continue
        folder=OUTPUT/ident;folder.mkdir(parents=True,exist_ok=True)
        source=SITE/'samples/api-examples'/platform/(name+'.c')
        compiler=REPOS/('kitaq'+platform)/('kitaq'+platform+'.exe')
        emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
        lib=REPOS/('kitaq'+platform)/'lib'
        libraries=[lib/'input.c'] if name=='input_edges' else [lib/'pad.c',lib/'input_repeat.c'] if name=='pad_repeat' else []
        rom=folder/('example.gb' if platform=='gb' else 'example.nes');png=folder/'screen.png';report=folder/'runtime.json'
        for path in [rom,png,report]:path.unlink(missing_ok=True)
        command=[str(compiler),*map(str,libraries),str(source),'-I',str(lib),'-I',str(SITE/'samples'),'-o',str(rom),'--no-disasm','--no-cache']
        if platform=='gb':command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb']
        else:command+=['--mapper=nrom','--nes-chr='+str(SITE/'samples/font.chr')]
        result=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
        (folder/'build.txt').write_bytes(result.stdout+result.stderr)
        row={'id':ident,'platform':platform,'program':source.relative_to(SITE).as_posix(),'mode':mode,
             'build_exit':result.returncode,'build_command':command,'source_sha256':sha(source),
             'library_sha256':{str(p.relative_to(REPOS)):sha(p) for p in libraries},
             'compiler_sha256':sha(compiler),'emulator_sha256':sha(emulator),'passed':False}
        if result.returncode==0 and rom.exists():
            row['rom_sha256']=sha(rom)
            if platform=='gb':
                sequence='NONE:30;'+('A,RIGHT' if name=='input_raw' else 'A')+':40;NONE:110'
                run=[str(emulator),str(rom),'--hardware',mode,'--run-frames','180','--input-seq',sequence,'--png',str(png),'--dump-report',str(report)]
                row['input_sequence']=sequence
            else:
                pad1=129 if name=='input_raw' else 2 if name=='pad_repeat' else 1
                pad2=66 if name=='input_raw' else 0
                timeline=[{'frame':start,'duration':duration,'pad1':p1,'pad2':p2,'reset':False,'disk_side':None,'expected_frame_hash':None}
                          for start,duration,p1,p2 in [(0,30,0,0),(30,40,pad1,pad2),(70,110,0,0)]]
                replay={'format':'kurosaki-replay-v1','rom_sha256':sha(rom),'emulator_version':'0.1.0','region':'ntsc','frames':timeline,'expected_final_state_hash':None}
                replay_path=folder/'input.json';replay_path.write_text(json.dumps(replay,indent=2),encoding='utf-8')
                run=[str(emulator),'replay-run',str(rom),str(replay_path),'--frames','180','--png',str(png),'--json',str(report)]
                row['input_timeline']=timeline
            result=subprocess.run(run,capture_output=True,timeout=90,cwd=folder)
            (folder/'runtime.txt').write_bytes(result.stdout+result.stderr)
            row.update(runtime_exit=result.returncode,run_command=run)
            if result.returncode==0 and png.exists() and report.exists():
                state=json.loads(report.read_text(encoding='utf-8'))
                if platform=='gb':
                    state={k:state[k] for k in ['meta','cpu','video','stop_reason','unsupported_opcodes'] if k in state}
                    report.write_text(json.dumps(state,indent=2),encoding='utf-8')
                if name=='input_edges':
                    labels=[(1,0,'INPUT EDGES')]+[(1,y,label) for y,label in [(2,'FIRST DOWN'),(3,'FIRST PRESS'),(4,'FIRST REPEAT'),(5,'FIRST CURRENT'),(6,'HELD TICKS'),(7,'PRESS COUNT'),(8,'REPEAT COUNT'),(9,'RELEASE'),(10,'LAST CURRENT'),(11,'LAST PREVIOUS'),(13,'FAILED CHECKS')]]
                    labels += [(16,y,value) for y,value in [(2,'001'),(3,'001'),(4,'001'),(5,'016'),(6,'040'),(7,'001'),(8,'005'),(9,'001'),(10,'000'),(11,'016'),(13,'000')]]
                elif name=='pad_repeat':
                    labels=[(1,0,'NES PAD REPEAT')]+[(1,y,label) for y,label in [(2,'FIRST HELD'),(3,'FIRST TRIGGER'),(4,'FIRST REPEAT'),(6,'HELD TICKS'),(7,'PULSE COUNT'),(9,'RELEASE BITS'),(13,'FAILED CHECKS')]]
                    labels += [(16,y,value) for y,value in [(2,'002'),(3,'002'),(4,'002'),(6,'040'),(7,'019'),(9,'002'),(13,'000')]]
                elif platform=='gb':
                    labels=[(1,0,'GB RAW INPUT')]+[(1,y,label) for y,label in [(4,'ALL KEYS'),(5,'DIRECTIONS'),(6,'BUTTONS LOW'),(8,'EX CURRENT'),(9,'EX NEW PRESS'),(10,'HELD PRESS'),(13,'FAILED CHECKS')]]
                    labels += [(16,y,value) for y,value in [(4,'017'),(5,'001'),(6,'001'),(8,'017'),(9,'017'),(10,'000'),(13,'000')]]
                else:
                    labels=[(1,0,'FC RAW INPUT')]+[(1,y,label) for y,label in [(5,'RAW P1'),(6,'RAW P2'),(7,'SAFE P1'),(8,'SAFE P2'),(9,'BUTTONS P1'),(10,'DIRS P1'),(11,'ALIAS P1'),(12,'ALIAS P2'),(14,'FAILED CHECKS')]]
                    labels += [(16,y,value) for y,value in [(5,'129'),(6,'066'),(7,'129'),(8,'066'),(9,'001'),(10,'128'),(11,'129'),(12,'066'),(14,'000')]]
                errors=check_pixels(png,labels,platform)
                # KUROSAKI replay summaries wrap the run summary; inspect the actual completed frame count.
                summary=state.get('summary',state)
                frames=summary.get('frames',summary.get('meta',{}).get('frames_executed'))
                row.update(expected_labels=labels,pixel_mismatches=errors,frames=frames,
                           image=png.relative_to(SITE).as_posix(),image_sha256=sha(png),
                           passed=errors==0 and frames==180)
        if row['passed']:cleanup_build_outputs(folder)
        records.append(row);print(ident,'PASS' if row['passed'] else 'FAIL',flush=True)
    evidence={'checked_at':datetime.now(timezone.utc).isoformat(),'records':records,
              'scope':'Scripted controller input, ROM self-checks and displayed value pixel checks. Real controllers, DMC interference and expansion devices are not covered.'}
    (OUTPUT/('results.json' if not opts.only else opts.only+'-results.json')).write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    if not all(r['passed'] for r in records):raise SystemExit(1)

if __name__=='__main__':main()
