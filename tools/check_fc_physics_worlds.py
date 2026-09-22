"""Run the GB body/world contract fixtures on the FC port in four compiler modes."""
from pathlib import Path
import hashlib,json,subprocess,sys
import check_physics_edges as original
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'publish/library_docs_20260914/fc-effects/physics-worlds'
LIB=ROOT/'publish/github_20260912/kitaqfc/lib'

def main():
    fixtures=[]
    def collect(platform,name,body,expected,include='',glob='',**unused):
        if 'physics2d_circle' in include or not ('physics2d.c' in include or 'physics3d.c' in include):return
        include=include.replace('#pragma bank 0','')
        if 'physics3d.c' in include:include='#include "fixed.c"\n#include "physics2d.c"\n'+include
        include=include.replace('#include "','#include "'+LIB.as_posix()+'/')
        source=include+'\n__location(0x0600) u16 result[64];\n'+glob+'\nvoid main(){u8 i;'+body+'result['+str(len(expected))+']=0xA55A;while(1){}}'
        fixtures.append(dict(name=name,source=source,expected=[x&65535 for x in expected]+[0xA55A]))
    original.execute=collect
    # The source runner's final aggregate assertion is irrelevant while collecting.
    original.rows.append(dict(passed=True));original.main()
    OUT.mkdir(parents=True,exist_ok=True);path=OUT/'fixtures.json';path.write_text(json.dumps(fixtures,indent=2),encoding='utf-8')
    result=subprocess.run([sys.executable,str(Path(__file__).with_name('check_compiler_parity.py')),'--platform','fc','--fc-mapper','mmc3','--fixtures',str(path),'--output',str(OUT/'state')])
    if result.returncode==0:
        report=OUT/'state/report.json';data=json.loads(report.read_text())
        data['library_sha256']={name:hashlib.sha256((LIB/name).read_bytes()).hexdigest() for name in ['physics2d.h','physics2d.c','physics3d.h','physics3d.c','fixed.h','fixed.c']}
        data['checker_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        data['fixture_author_sha256']=hashlib.sha256(Path(original.__file__).read_bytes()).hexdigest()
        report.write_text(json.dumps(data,indent=2),encoding='utf-8')
    raise SystemExit(result.returncode)
if __name__=='__main__':main()
