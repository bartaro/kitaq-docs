"""Check explicitly aligned ROM arrays and their bytes on NROM and UxROM."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-sound/state/alignment'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--compiler');parser.add_argument('--tag',default='current');args=parser.parse_args()
    compiler=Path(args.compiler).resolve() if args.compiler else REPOS/'kitaqfc/kitaqfc.exe';rows=[]
    emulator=REPOS/'kurosaki/kurosaki.exe'
    for mapper in ['nrom','uxrom']:
      for zp in ['--no-zp-alloc','--zp-alloc']:
        folder=OUT/(args.tag+'-'+mapper+zp);folder.mkdir(parents=True,exist_ok=True)
        source=folder/'case.c';rom=folder/'case.nes';snapshot=folder/'state.json'
        declarations=[];checks=[];want=[]
        for i,alignment in enumerate([2,8,16,64,128,256]):
            bank=0 if mapper=='nrom' else i%3
            values=[(i*19+j)&255 for j in range(17)]
            declarations.append(f'#pragma bank {bank}\n__aligned({alignment}) __prg_rom u8 a{i}[17]={{'+','.join(map(str,values))+'};')
            checks.append(f'__bankswitch({max(bank,1)}); result[{i*4}]=(u8)(((u16)a{i}&{alignment-1})==0); result[{i*4+1}]=a{i}[0]; result[{i*4+2}]=a{i}[16]; result[{i*4+3}]=(u8)(sizeof(a{i})==17);')
            want +=[1,values[0],values[-1],1]
        code='#include "intrinsics.h"\n'+ '\n'.join(declarations)+'\n#pragma bank 0\n__location(0x0600) u8 result[25];\nvoid main(void) {\n'+'\n'.join(checks)+'\nresult[24]=0xA5; while(1){} }\n'
        source.write_text(code,encoding='utf-8')
        command=[str(compiler),str(source),'-I',str(REPOS/'kitaqfc/lib'),'-o',str(rom),'--mapper='+mapper,zp,'--no-cache','--no-disasm']
        run=subprocess.run(command,cwd=folder,capture_output=True,timeout=120);(folder/'build.txt').write_bytes(run.stdout+run.stderr);assert run.returncode==0
        run=subprocess.run([str(emulator),'run',str(rom),'--frames','30','--headless','--snapshot',str(snapshot)],cwd=folder,capture_output=True,timeout=120);assert run.returncode==0
        actual=json.loads(snapshot.read_text(encoding='utf-8'))['bus']['ram'][0x600:0x619];expected=want+[0xA5]
        row=dict(mapper=mapper,zp=zp,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),actual=actual,expected=expected,passed=actual==expected)
        rows.append(row);cleanup_build_outputs(folder)
        print(mapper,zp,'PASS' if row['passed'] else 'FAIL',[(i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b],flush=True)
    report=dict(compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),script_sha256=sha(Path(__file__)),records=rows)
    OUT.mkdir(parents=True,exist_ok=True);(OUT/(args.tag+'-results.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
if __name__=='__main__':main()
