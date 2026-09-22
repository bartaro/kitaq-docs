"""Exercise CHR memory selection, option conflicts and cached build isolation."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'publish/library_docs_20260914/fc-effects/chr-ram'
COMPILER=ROOT/'publish/github_20260912/kitaqfc/kitaqfc.exe'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=OUT/'case.c';source.write_text('void main(){while(1){}}\n')
    artwork=OUT/'tiles.chr';artwork.write_bytes(bytes([0xA5])*8192)
    cases=[('default',[],True,1),('ram',['--nes-chr-ram'],True,0),('rom-again',[],True,1),('art',['--nes-chr='+str(artwork)],True,1),('conflict-a',['--nes-chr-ram','--nes-chr='+str(artwork)],False,None),('conflict-b',['--nes-chr='+str(artwork),'--nes-chr-ram'],False,None),('cnrom',['--mapper=cnrom','--nes-chr-ram'],False,None),('mmc3',['--mapper=mmc3','--nes-chr-ram'],True,0)]
    rows=[]
    for name,flags,success,chr_count in cases:
        rom=OUT/'case.nes'
        p=subprocess.run([str(COMPILER),str(source),'-o',str(rom),'--no-disasm']+flags,cwd=OUT,capture_output=True,timeout=90)
        (OUT/(name+'.txt')).write_bytes(p.stdout+p.stderr)
        passed=(p.returncode==0)==success
        if success:
            data=rom.read_bytes();passed &= data[5]==chr_count and len(data)==16+data[4]*16384+data[5]*8192
            if name=='art':passed &= data[-8192:]==artwork.read_bytes()
        rows.append(dict(case=name,passed=passed,exit=p.returncode));print(name,passed,flush=True)
    (OUT/'results.json').write_text(json.dumps(rows,indent=2));assert all(r['passed'] for r in rows)

if __name__=='__main__':main()
