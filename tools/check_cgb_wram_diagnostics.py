"""Prove that unsupported targets and out-of-range constant banks are rejected."""
from pathlib import Path
import hashlib,json,subprocess
from api_build_cleanup import cleanup_build_outputs

SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
compiler=REPOS/'kitaqgb/kitaqgb.exe'
output=SITE/'verification/api-cgb-dma-wram/diagnostics'
cases=[('get_dual','cgb','__svbk_get()',2103),('get_dmg','dmg','__svbk_get()',2103),
       ('set_dual','cgb','__svbk_set(2)',2103),('set_dmg','dmg','__svbk_set(2)',2103),
       ('set_zero','cgb_only','__svbk_set(0)',2102),('set_eight','cgb_only','__svbk_set(8)',2102)]
records=[]
for name,target,expression,code in cases:
    folder=output/name;folder.mkdir(parents=True,exist_ok=True)
    source=folder/'invalid.c';rom=folder/'invalid.gb';rom.unlink(missing_ok=True)
    source.write_text('u8 __svbk_get();\nu8 __svbk_set(u8 bank);\nu8 result;\nvoid main() { result='+expression+'; while(1) {} }\n',encoding='utf-8')
    command=[str(compiler),str(source),'-o',str(rom),'--profile=dev','--stack-bank=fixed','--cgb='+target,'--no-cache','--no-disasm']
    process=subprocess.run(command,capture_output=True,timeout=90,cwd=folder)
    log=process.stdout+process.stderr;(folder/'build.txt').write_bytes(log)
    passed=process.returncode!=0 and ('KQ'+str(code)).encode() in log and not rom.exists()
    records.append({'id':name,'target':target,'source':source.relative_to(SITE).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'command':command,'expected_diagnostic':'KQ'+str(code),'exit_code':process.returncode,'passed':passed})
    if passed:cleanup_build_outputs(folder)
    print(name,'PASS' if passed else 'FAIL',flush=True)
(output/'results.json').write_text(json.dumps({'compiler_sha256':hashlib.sha256(compiler.read_bytes()).hexdigest(),'records':records,'scope':'Intentional compile failures: CGB-only target requirement and constant bank range. These invalid sources are diagnostic fixtures, not runnable sample programs.'},indent=2),encoding='utf-8')
if not all(row['passed'] for row in records):raise SystemExit(1)
