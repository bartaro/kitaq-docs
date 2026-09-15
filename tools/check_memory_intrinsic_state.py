"""Compare complete RAM ranges for variable-length and fixed-size memory intrinsics.

KOKURA watches are split into 16-byte windows so their previews contain every
checked byte. KUROSAKI snapshots are reduced to the same observations after a
successful check; large unrelated machine-state dumps are not retained.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess

SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--platform',choices=['gb','fc'],required=True)
parser.add_argument('--only')
args=parser.parse_args();platform=args.platform
OUT=SITE/'verification/api-memory-intrinsics'/platform
OUT.mkdir(parents=True,exist_ok=True)
compiler=REPOS/('kitaq'+platform)/('kitaq'+platform+'.exe')
emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_addr,dest_addr,result_addr=(0xC4E8,0xC8F0,0xC700) if platform=='gb' else (0x2E8,0x4F0,0x700)
SIZE=264
cases=[]
for fill in [False,True]:
    for small in [False,True]:
        counts=[0,1,16,17,32,33,64,65,255]+([] if small else [256,257])
        callee=('__memset' if fill else '__memcpy')+('_small' if small else '')
        for count in counts:
            for dynamic in [False,True]:
                cases.append(dict(name=callee[2:]+'-'+str(count)+('-runtime' if dynamic else '-constant'),callee=callee,count=count,fill=fill,dynamic=dynamic,getters=dynamic,fixed=False))
        cases.append(dict(name=callee[2:]+'-zero-argument-effects',callee=callee,count=0,fill=fill,dynamic=False,getters=True,fixed=False))
for count in [16,32]:
    for getters in [False,True]:
        cases.append(dict(name='copy'+str(count)+('-getters' if getters else '-direct'),callee='__copy'+str(count),count=count,fill=False,dynamic=False,getters=getters,fixed=True))

prefix=f'''// Original bounded memory-transfer fixture with leading/trailing guards.
__location({source_addr}) u8 source[{SIZE}];
__location({dest_addr}) u8 destination[{SIZE}];
__location({result_addr}) u8 seen[4];
u16 requested;
u8* getdst(){{seen[0]=seen[0]+1;return destination+1;}}
const u8* getsrc(){{seen[1]=seen[1]+1;return source+1;}}
u8 getvalue(){{seen[1]=seen[1]+1;return 0x5A;}}
u16 getcount(){{seen[2]=seen[2]+1;return requested;}}
void __memcpy(void* dst,const void* src,u16 len);
void __memcpy_small(void* dst,const void* src,u8 len);
void __memset(void* dst,u8 value,u16 len);
void __memset_small(void* dst,u8 value,u8 len);
void __copy16(void* dst,const void* src);
void __copy32(void* dst,const void* src);
'''

rows=[]
for case in cases:
    if args.only and case['name']!=args.only:continue
    folder=OUT/case['name'];folder.mkdir(exist_ok=True)
    source=folder/'case.c';rom=folder/('case.'+('gb' if platform=='gb' else 'nes'));state_path=folder/'state.json'
    arguments=['getdst()' if case['getters'] else 'destination+1']
    arguments.append(('getvalue()' if case['dynamic'] else '0x5A') if case['fill'] else ('getsrc()' if case['getters'] else 'source+1'))
    if not case['fixed']:arguments.append('getcount()' if case['dynamic'] else str(case['count']))
    text=prefix+'void main(){u16 i;seen[0]=0;seen[1]=0;seen[2]=0;seen[3]=0;requested='+str(case['count'])+';'
    text+='for(i=0;i<'+str(SIZE)+';i++){source[i]=(u8)(i*13+7);destination[i]=0xCC;}'
    text+=case['callee']+'('+','.join(arguments)+');seen[3]=165;while(1){}}'
    source.write_text(text,encoding='ascii')
    for path in [rom,state_path]:path.unlink(missing_ok=True)
    command=[str(compiler),str(source),'--no-cache','--no-disasm','-o',str(rom)]
    if platform=='gb':command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=dmg']
    process=subprocess.run(command,cwd=folder,capture_output=True,timeout=60)
    (folder/'build.txt').write_bytes(process.stdout+process.stderr)
    row={**case,'source_sha256':sha(source),'build_exit':process.returncode,'passed':False}
    if process.returncode==0:
        if platform=='gb':
            command=[str(emulator),str(rom),'--hardware','dmg','--run-frames','16','--watch-window',f'seen:{result_addr}:4','--dump-report',str(state_path)]
            for label,start in [('source',source_addr),('destination',dest_addr)]:
                for offset in range(0,SIZE,16):command+=['--watch-window',f'{label}{offset}:{start+offset}:{min(16,SIZE-offset)}']
        else:
            command=[str(emulator),'run',str(rom),'--frames','16','--headless','--snapshot',str(state_path)]
        process=subprocess.run(command,cwd=folder,capture_output=True,timeout=60)
        (folder/'runtime.txt').write_bytes(process.stdout+process.stderr);row['runtime_exit']=process.returncode
        if process.returncode==0:
            state=json.loads(state_path.read_text(encoding='utf-8'))
            if platform=='gb':
                watches={w['name']:w for w in state['watched_memory']}
                actual={}
                for label,start,size in [('source',source_addr,SIZE),('destination',dest_addr,SIZE),('seen',result_addr,4)]:
                    values=[]
                    for offset in range(0,size,16):
                        watch=watches[label if label=='seen' else label+str(offset)]
                        assert watch['addr']==start+offset and watch['size']==min(16,size-offset) and not watch.get('preview_truncated',False)
                        values+=watch['preview_bytes']
                    actual[label]=values
            else:
                ram=state['bus']['ram'];actual={'source':ram[source_addr:source_addr+SIZE],'destination':ram[dest_addr:dest_addr+SIZE],'seen':ram[result_addr:result_addr+4]}
            expected_source=[(i*13+7)&255 for i in range(SIZE)];expected_dest=[204]*SIZE
            expected_dest[1:case['count']+1]=[90]*case['count'] if case['fill'] else expected_source[1:case['count']+1]
            expected_seen=[int(case['getters']),int(case['dynamic'] if case['fill'] else case['getters']),int(case['dynamic']),165]
            expected={'source':expected_source,'destination':expected_dest,'seen':expected_seen}
            row.update(actual=actual,expected=expected,rom_sha256=sha(rom),passed=actual==expected)
            if row['passed']:
                state_path.write_text(json.dumps({'platform':platform,'observed':actual,'expected':expected,'passed':True},indent=2),encoding='utf-8')
    rows.append(row)
    if not row['passed']:print(case['name'],'FAIL',json.dumps({k:v for k,v in row.items() if k not in ['actual','expected']}),flush=True)
    elif len(rows)%12==0:print(platform,len(rows),'cases passed',flush=True)
    report={'platform':platform,'script_sha256':sha(Path(__file__)),'compiler_sha256':sha(compiler),'emulator_sha256':sha(emulator),'cases':rows}
    (OUT/('selected_report.json' if args.only else 'state_checks.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
assert rows
print(platform,sum(row['passed'] for row in rows),'/',len(rows),'passed',flush=True)
raise SystemExit(0 if all(row['passed'] for row in rows) else 1)
