"""Compare seeded output sequences and library draw consumption with a host model."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from api_build_cleanup import cleanup_build_outputs
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--platform',choices=['gb','fc'],required=True);parser.add_argument('--only')
args=parser.parse_args();platform=args.platform
OUT=SITE/'verification/api-rng'/platform;OUT.mkdir(parents=True,exist_ok=True)
compiler=REPOS/('kitaq'+platform)/('kitaq'+platform+'.exe');emulator=REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
address=0xC600 if platform=='gb' else 0x500
seeds=[0,1,255,256,0x1234,0x5AA5,0xA55A,0x8000,0xFFFF];cases=[]
for seed in seeds:
    for dynamic in [False,True]:cases.append(dict(api='__rng8',seed=seed,dynamic_seed=dynamic,seeder='__rng_seed'))
if platform=='gb':
    for seed in seeds:cases.append(dict(api='rng8',seed=seed,seeder='rng_seed'))
    for api in ['rng8','rng_next8','rng16','rng_next16']:
        for seed in [0,0x1234,0xFFFF]:cases.append(dict(api=api,seed=seed))
    for api in ['rand_range','rng_range']:
        for maximum in [0,1,2,3,10,100,255]:
            for seed in [0,0x1234]:cases.append(dict(api=api,seed=seed,argument=maximum))
    for percent in [0,1,50,99,100,101,255]:
        for seed in [0,0x1234]:cases.append(dict(api='rng_chance',seed=seed,argument=percent))
    for label,weights in [('empty',[]),('zeros',[0,0,0]),('one',[0,5,0]),('mixed',[1,3,6]),('max',[255]*255),('equal',[1]*255)]:
        for seed in [0,0x1234]:cases.append(dict(api='weighted_choice',seed=seed,weights=weights,label=label))

class Model:
    def __init__(self,seed):self.state=seed
    def byte(self):
        if platform=='gb':
            s=self.state or 0x5AA5;s=(s+0x5D17)&65535
            lo=(s&255)^(s>>8);hi=s>>8;hi=(((hi<<1)|(hi>>7))+lo)&255
            self.state=(hi<<8)|lo;return hi
        s=self.state or 0xA55A;self.state=(s>>1)^(0xB400 if s&1 else 0)
        return (self.state^(self.state>>8))&255
    def word(self):return (self.byte()<<8)|self.byte()
    def draw(self,case):
        api=case['api']
        if api in ['__rng8','rng8','rng_next8']:return self.byte()
        if api in ['rng16','rng_next16']:return self.word()
        if api in ['rand_range','rng_range']:
            n=case['argument'];return self.byte()%n if n else 0
        if api=='rng_chance':
            n=case['argument'];return 0 if n==0 else 1 if n>=100 else int(self.byte()%100<n)
        total=sum(case['weights'])
        if not total:return 0
        pick=self.word()%total
        for i,w in enumerate(case['weights']):
            if pick<w:return i
            pick-=w
        raise AssertionError('Weight model exhausted')

rows=[]
for ordinal,case in enumerate(cases):
    name=str(ordinal).zfill(3)+'-'+case['api'].lstrip('_')+'-'+str(case['seed'])
    if args.only and name!=args.only:continue
    folder=OUT/name;folder.mkdir(exist_ok=True);source=folder/'case.c';rom=folder/('case.gb' if platform=='gb' else 'case.nes');state_path=folder/'state.json'
    header='#include "rpg.h"\n' if platform=='gb' else '#include "intrinsics.h"\n'
    text=header+f'__location({address}) u8 result[80];\nu16 requested;\nu16 getseed(){{return requested;}}\n'
    if case['api']=='weighted_choice':text+='u8 weights[255];\n'
    text+='void main(){u8 i;u16 value;for(i=0;i<80;i++)result[i]=204;'
    seed=case['seed'];text+='requested='+str(seed)+';'+case.get('seeder','__rng_seed')+'('+('getseed()' if case.get('dynamic_seed') else str(seed))+');'
    if case['api']=='weighted_choice':
        weights=case['weights']
        if weights and len(set(weights))==1:text+='for(i=0;i<'+str(len(weights))+';i++)weights[i]='+str(weights[0])+';'
        else:text+=''.join('weights['+str(i)+']='+str(w)+';' for i,w in enumerate(weights))
        call='weighted_choice('+('weights' if weights else '(const u8*)0')+','+str(len(weights))+')'
    else:call=case['api']+'('+str(case['argument'])+')' if 'argument' in case else case['api']+'()'
    text+='for(i=0;i<32;i++){value='+call+';result[i*2]=(u8)value;result[i*2+1]=(u8)(value>>8);}'
    text+='for(i=0;i<8;i++)result[64+i]=__rng8();result[79]=165;while(1){}}'
    source.write_text(text,encoding='ascii')
    for p in [rom,state_path]:p.unlink(missing_ok=True)
    command=[str(compiler),str(source),'-I',str(REPOS/('kitaq'+platform)/'lib'),'--no-cache','--no-disasm','-o',str(rom)]
    if platform=='gb':command[2:2]=[str(REPOS/'kitaqgb/lib/rng.c')];command+=['--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=dmg']
    process=subprocess.run(command,cwd=folder,capture_output=True,timeout=60);(folder/'build.txt').write_bytes(process.stdout+process.stderr)
    row={**case,'name':name,'source_sha256':sha(source),'build_exit':process.returncode,'passed':False}
    if process.returncode==0:
        if platform=='gb':
            command=[str(emulator),str(rom),'--hardware','dmg','--run-frames','240','--dump-report',str(state_path)]
            for offset in range(0,80,16):command+=['--watch-window',f'result{offset}:{address+offset}:16']
        else:command=[str(emulator),'run',str(rom),'--frames','60','--headless','--snapshot',str(state_path)]
        process=subprocess.run(command,cwd=folder,capture_output=True,timeout=60);(folder/'runtime.txt').write_bytes(process.stdout+process.stderr);row['runtime_exit']=process.returncode
        if process.returncode==0:
            state=json.loads(state_path.read_text(encoding='utf-8'))
            if platform=='gb':
                watches={w['name']:w for w in state['watched_memory']};actual=[]
                for offset in range(0,80,16):
                    w=watches['result'+str(offset)];assert w['addr']==address+offset and w['size']==16 and not w.get('preview_truncated',False)
                    actual+=w['preview_bytes']
            else:actual=state['bus']['ram'][address:address+80]
            model=Model(seed);expected=[]
            for _ in range(32):
                value=model.draw(case);expected += [value&255,value>>8]
            expected += [model.byte() for _ in range(8)]+[204]*7+[165]
            row.update(actual=actual,expected=expected,rom_sha256=sha(rom),passed=actual==expected)
            if row['passed']:
                state_path.write_text(json.dumps({'actual':actual,'expected':expected,'passed':True},indent=2),encoding='utf-8');cleanup_build_outputs(folder)
    rows.append(row)
    if not row['passed']:print(platform,name,'FAIL',flush=True)
    elif len(rows)%10==0:print(platform,len(rows),'passed',flush=True)
    files={'kitaq'+platform+'/lib/'+('rpg.h' if platform=='gb' else 'intrinsics.h'):sha(REPOS/('kitaq'+platform)/'lib'/('rpg.h' if platform=='gb' else 'intrinsics.h'))}
    if platform=='gb':files['kitaqgb/lib/rng.c']=sha(REPOS/'kitaqgb/lib/rng.c')
    report={'platform':platform,'script_sha256':sha(Path(__file__)),'compiler_sha256':sha(compiler),'emulator_sha256':sha(emulator),'library_sha256':files,'cases':rows}
    (OUT/('selected_report.json' if args.only else 'state_checks.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(platform,sum(r['passed'] for r in rows),'/',len(rows),'passed',flush=True)
raise SystemExit(0 if rows and all(r['passed'] for r in rows) else 1)
