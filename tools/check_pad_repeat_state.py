"""Build the repeat-state teaching ROM and check deterministic action/timing observations."""
from pathlib import Path
import subprocess,json,hashlib
from check_entity_callbacks import check_pixels
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUTPUT=SITE/'verification/api-pad-repeat'
source=SITE/'samples/api-examples/gb/pad_repeat_state.c'
compiler=REPOS/'kitaqgb/kitaqgb.exe'
emulator=REPOS/'kokura/kokura-cli.exe'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
records=[]
for mode in ['dmg','cgb']:
    folder=OUTPUT/mode;folder.mkdir(parents=True,exist_ok=True)
    rom=folder/'example.gb';image=folder/'screen.png';report=folder/'runtime.json'
    for path in [rom,image,report]:path.unlink(missing_ok=True)
    command=[str(compiler),str(source),'-I',str(SITE/'samples'),'-I',str(REPOS/'kitaqgb/lib'),'-o',str(rom),'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--no-cache','--no-disasm']
    process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
    (folder/'build.txt').write_bytes(process.stdout+process.stderr)
    row={'mode':mode,'platform':'gb','source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'compiler_sha256':sha(compiler),'build_command':command,'build_exit':process.returncode,'passed':False}
    if process.returncode==0:
        command=[str(emulator),str(rom),'--hardware',mode,'--run-frames','180','--png',str(image),'--dump-report',str(report)]
        process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
        (folder/'runtime.txt').write_bytes(process.stdout+process.stderr)
        row.update(run_command=command,runtime_exit=process.returncode,rom_sha256=sha(rom),emulator_sha256=sha(emulator))
        if process.returncode==0 and image.exists():
            labels=[(1,0,'REPEAT STATE'),(1,2,'TICKS 0 3 5 7'),(1,4,'RIGHT PULSES'),(1,5,'DOWN PULSES'),(1,6,'ACTION PULSES'),(1,7,'ALIAS PULSES'),(1,10,'CHECKS'),(16,10,'057'),(1,12,'FAILED CHECKS'),(16,12,'000')]+[(16,y,'004') for y in [4,5,6,7]]
            errors=check_pixels(image,labels,'gb')
            data=json.loads(report.read_text(encoding='utf-8'))
            data={k:data[k] for k in ['meta','cpu','video','stop_reason','unsupported_opcodes'] if k in data}
            report.write_text(json.dumps(data,indent=2),encoding='utf-8')
            frames=data.get('meta',{}).get('frames_executed')
            row.update(image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),expected_labels=labels,pixel_mismatches=errors,frames=frames,passed=errors==0 and frames==180)
    if row['passed']:cleanup_build_outputs(folder)
    records.append(row);print(mode,'PASS' if row['passed'] else 'FAIL',flush=True)
(OUTPUT/'results.json').write_text(json.dumps({'records':records},indent=2),encoding='utf-8')
if not all(r['passed'] for r in records):raise SystemExit(1)
