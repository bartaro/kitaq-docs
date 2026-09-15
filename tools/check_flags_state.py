"""Exercise every valid game-flag ID and every quest byte/value combination."""
from pathlib import Path
import hashlib, json, subprocess
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
OUT=SITE/'verification/api-flags/state';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
compiler=REPOS/'kitaqgb/kitaqgb.exe';emulator=REPOS/'kokura/kokura-cli.exe';library=REPOS/'kitaqgb/lib'
source=OUT/'case.c';rom=OUT/'case.gb';snapshot=OUT/'state.json'
source.write_text('''#include "rpg.h"
__location(0xC600) u8 result[336];
u16 failures;
void main(){u16 i;u16 value;u8 q;u8 bit;u8 packed;
    failures=0;for(i=0;i<336;i++)result[i]=204;
    for(i=0;i<2048;i++)flag_clear(i);
    for(q=0;q<64;q++)quest_set_state(q,0);
    // Check every valid flag, repeated writes and immediate neighbor isolation.
    for(i=0;i<2048;i++){
        if(flag_get(i)!=0)failures++;
        flag_set(i);flag_set(i);
        if(flag_get(i)!=1)failures++;
        if(i>0 && flag_get(i-1)!=0)failures++;
        if(i<2047 && flag_get(i+1)!=0)failures++;
        flag_clear(i);flag_clear(i);
        if(flag_get(i)!=0)failures++;
    }
    // Check all 64 quest entries with all 256 byte values, including overwrite.
    for(q=0;q<64;q++){
        for(value=0;value<256;value++){
            quest_set_state(q,(u8)value);
            if(quest_state(q)!=(u8)value)failures++;
            if(q>0 && quest_state(q-1)!=0)failures++;
            if(q<63 && quest_state(q+1)!=0)failures++;
        }
        quest_set_state(q,0);
    }
    // Capture all flag bytes and all quest bytes for a host-side comparison.
    for(i=0;i<2048;i++)if(i%3==0)flag_set(i);
    flag_set(2047);flag_clear(0);
    for(i=0;i<256;i++){
        packed=0;
        for(bit=0;bit<8;bit++)if(flag_get(i*8+bit))packed=(u8)(packed|(1<<bit));
        result[i]=packed;
    }
    for(q=0;q<64;q++){quest_set_state(q,(u8)(q*3+19));result[256+q]=quest_state(q);}
    result[320]=(u8)failures;result[321]=(u8)(failures>>8);result[335]=165;
    while(1){}
}
''',encoding='ascii')
for path in [rom,snapshot]:path.unlink(missing_ok=True)
command=[str(compiler),str(source),str(library/'flags.c'),'-I',str(library),'-o',str(rom),'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=dmg','--no-cache','--no-disasm']
process=subprocess.run(command,cwd=OUT,capture_output=True,timeout=90);(OUT/'build.txt').write_bytes(process.stdout+process.stderr)
report={'source_sha256':sha(source),'script_sha256':sha(Path(__file__)),'compiler_sha256':sha(compiler),'emulator_sha256':sha(emulator),'source_files':{'kitaqgb/lib/rpg.h':sha(library/'rpg.h'),'kitaqgb/lib/flags.c':sha(library/'flags.c')},'build_exit':process.returncode,'passed':False,'flag_ids':2048,'quest_ids':64,'quest_values_per_id':256}
if process.returncode==0:
    command=[str(emulator),str(rom),'--hardware','dmg','--run-frames','1200','--dump-report',str(snapshot)]
    for offset in range(0,336,16):command+=['--watch-window',f'result{offset}:{0xC600+offset}:16']
    process=subprocess.run(command,cwd=OUT,capture_output=True,timeout=180);(OUT/'runtime.txt').write_bytes(process.stdout+process.stderr);report['runtime_exit']=process.returncode
    if process.returncode==0:
        state=json.loads(snapshot.read_text(encoding='utf-8'));watches={w['name']:w for w in state['watched_memory']};actual=[]
        for offset in range(0,336,16):
            w=watches['result'+str(offset)];assert w['addr']==0xC600+offset and w['size']==16 and not w.get('preview_truncated',False)
            actual+=w['preview_bytes']
        expected=[]
        for byte in range(256):expected.append(sum(1<<bit for bit in range(8) if ((byte*8+bit)%3==0 or byte*8+bit==2047) and byte*8+bit!=0))
        expected += [(q*3+19)&255 for q in range(64)]+[0,0]+[204]*13+[165]
        report.update(actual=actual,expected=expected,rom_sha256=sha(rom),frames=1200,passed=actual==expected)
        if report['passed']:
            snapshot.write_text(json.dumps({'actual':actual,'expected':expected,'passed':True},indent=2),encoding='utf-8');cleanup_build_outputs(OUT)
(OUT/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'flag_ids':2048,'quest_byte_combinations':64*256}))
raise SystemExit(0 if report['passed'] else 1)
