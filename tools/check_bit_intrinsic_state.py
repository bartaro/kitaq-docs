"""Check complete guarded buffers and bit-test return values on GB and FC."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--platform',choices=['gb','fc'],required=True)
parser.add_argument('--only')
args=parser.parse_args();platform=args.platform
OUT=SITE/'verification/api-bit-intrinsics'/platform;OUT.mkdir(parents=True,exist_ok=True)
compiler=REPOS/('kitaq'+platform)/('kitaq'+platform+'.exe')
emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base,result=(0xC4F1,0xC780) if platform=='gb' else (0x02F1,0x0700)
SIZE=520;cases=[]
for op in ['test','set','clear','toggle']:
    for bit in [0,1,2,3,4,5,6,7,8,255,2047,2048,4095]:
        for dynamic in [False,True]:
            cases.append(dict(op=op,bit=bit,dynamic=dynamic,initial='pattern'))
for initial in ['zero','full']:
    for bit in range(8):
        for dynamic in [False,True]:cases.append(dict(op='test',bit=bit,dynamic=dynamic,initial=initial))
rows=[]
for case in cases:
    name=case['op']+'-'+str(case['bit'])+'-'+case['initial']+'-'+('runtime' if case['dynamic'] else 'constant')
    if args.only and name!=args.only:continue
    folder=OUT/name;folder.mkdir(exist_ok=True)
    source=folder/'case.c';rom=folder/('case.gb' if platform=='gb' else 'case.nes');state_path=folder/'state.json'
    value={'pattern':'(u8)(i*13+7)','zero':'0','full':'255'}[case['initial']]
    index='getindex()' if case['dynamic'] else str(case['bit'])
    pointer='getbase()' if case['dynamic'] else 'data+1'
    call='__bit_'+case['op']+'('+pointer+','+index+');'
    if case['op']=='test':call='seen[0]='+call
    text=f'''// Original guarded bit-operation fixture; addresses deliberately cross pages.
__location({base}) u8 data[{SIZE}];
__location({result}) u8 seen[4];
u16 requested;
u8* getbase(){{seen[1]=seen[1]+1;return data+1;}}
u16 getindex(){{seen[2]=seen[2]+1;return requested;}}
u8 __bit_test(u8* p,u16 bit);
void __bit_set(u8* p,u16 bit);
void __bit_clear(u8* p,u16 bit);
void __bit_toggle(u8* p,u16 bit);
void main(){{u16 i;seen[0]=238;seen[1]=0;seen[2]=0;seen[3]=0;
requested={case['bit']};for(i=0;i<{SIZE};i++)data[i]={value};
data[0]=204;data[519]=204;
{call}
seen[3]=165;while(1){{}}
}}
'''
    source.write_text(text,encoding='ascii')
    for p in [rom,state_path]:p.unlink(missing_ok=True)
    command=[str(compiler),str(source),'--no-cache','--no-disasm','-o',str(rom)]
    if platform=='gb':command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=dmg']
    process=subprocess.run(command,cwd=folder,capture_output=True,timeout=60)
    (folder/'build.txt').write_bytes(process.stdout+process.stderr)
    row={**case,'name':name,'source_sha256':sha(source),'build_exit':process.returncode,'passed':False}
    if process.returncode==0:
        if platform=='gb':
            command=[str(emulator),str(rom),'--hardware','dmg','--run-frames','16','--watch-window',f'seen:{result}:4','--dump-report',str(state_path)]
            for offset in range(0,SIZE,16):command+=['--watch-window',f'data{offset}:{base+offset}:{min(16,SIZE-offset)}']
        else:command=[str(emulator),'run',str(rom),'--frames','16','--headless','--snapshot',str(state_path)]
        process=subprocess.run(command,cwd=folder,capture_output=True,timeout=60)
        (folder/'runtime.txt').write_bytes(process.stdout+process.stderr);row['runtime_exit']=process.returncode
        if process.returncode==0:
            state=json.loads(state_path.read_text(encoding='utf-8'))
            if platform=='gb':
                watches={w['name']:w for w in state['watched_memory']};observed={}
                for label,start,size in [('data',base,SIZE),('seen',result,4)]:
                    values=[]
                    for offset in range(0,size,16):
                        w=watches[label if label=='seen' else label+str(offset)]
                        assert w['addr']==start+offset and w['size']==min(16,size-offset) and not w.get('preview_truncated',False)
                        values+=w['preview_bytes']
                    observed[label]=values
            else:
                ram=state['bus']['ram'];observed={'data':ram[base:base+SIZE],'seen':ram[result:result+4]}
            data=[(i*13+7)&255 if case['initial']=='pattern' else 0 if case['initial']=='zero' else 255 for i in range(SIZE)]
            data[0]=data[519]=204;offset=1+case['bit']//8;mask=1<<(case['bit']%8)
            answer=238
            if case['op']=='test':answer=int(bool(data[offset]&mask)) if platform=='gb' else data[offset]&mask
            elif case['op']=='set':data[offset]|=mask
            elif case['op']=='clear':data[offset]&=255^mask
            else:data[offset]^=mask
            expected={'data':data,'seen':[answer,int(case['dynamic']),int(case['dynamic']),165]}
            row.update(actual=observed,expected=expected,rom_sha256=sha(rom),passed=observed==expected)
            if row['passed']:
                state_path.write_text(json.dumps({'actual':observed,'expected':expected,'passed':True},indent=2),encoding='utf-8')
                cleanup_build_outputs(folder)
    rows.append(row)
    if not row['passed']:print(platform,name,'FAIL',flush=True)
    elif len(rows)%16==0:print(platform,len(rows),'passed',flush=True)
    report={'platform':platform,'script_sha256':sha(Path(__file__)),'compiler_sha256':sha(compiler),'emulator_sha256':sha(emulator),'cases':rows}
    (OUT/('selected_report.json' if args.only else 'state_checks.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(platform,sum(r['passed'] for r in rows),'/',len(rows),'passed',flush=True)
raise SystemExit(0 if rows and all(r['passed'] for r in rows) else 1)
