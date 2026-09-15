"""Bind the five GB flag/quest APIs to their source and teaching program."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
header=REPOS/'kitaqgb/lib/rpg.h';library=REPOS/'kitaqgb/lib/flags.c'
declarations={r['name']:r for r in catalog.definitions(header)};definitions={r['name']:r for r in catalog.definitions(library)}
path=SITE/'reference/gb-api.json';data=json.loads(path.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
program='samples/api-examples/gb/flags_quests.c';sample=(SITE/program).read_text(encoding='utf-8');contracts={};evidence={}
for name,purpose,demo in [('flag_get','flags_get','flags_demo_get'),('flag_set','flags_set','flags_demo_set'),('flag_clear','flags_clear','flags_demo_clear'),('quest_state','quest_get','quest_demo_get'),('quest_set_state','quest_set','quest_demo_set')]:
    record=records[name]
    for key in ['ret','args','signature','path','line','comment','body']:record[key]=declarations[name][key]
    record['definition']=definitions[name]
    fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
    match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',sample,re.S);assert match
    code='\n'.join(s[4:] if s.startswith('    ') else s for s in match[1].splitlines())
    args=[['id',['flags_id']]] if name.startswith('flag_') else [['quest_id',['quest_id']]]
    if name=='quest_set_state':args.append(['state',['quest_value']])
    result=['flags_boolean'] if name=='flag_get' else ['quest_byte'] if name=='quest_state' else ['none']
    contracts['gb:'+name]={'review':'flags-source-20260915','purpose':[purpose],'args':args,'returns':result,'notes':['flags_bounds','flags_storage','flags_link'],'record_sha256':fingerprint,
        'example':{'code':code,'program':program,'expected':[demo,'flags_screen','flags_proof'],'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\samples\\api-examples\\gb\\flags_quests.c .\\kitaqgb\\lib\\flags.c -I .\\kitaqgb\\lib -I .\\kitaq-docs\\samples -o .\\out\\flags_quests.gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --no-cache --no-disasm'}}
    evidence['gb:'+name]={'record_sha256':fingerprint,'header_line':record['line'],'definition_line':record['definition']['line']}
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'flags_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'flags_review_sources.json').write_text(json.dumps({'source_sha256':{p.relative_to(REPOS).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [header,library]},'records':evidence},indent=2),encoding='utf-8')
(HERE/'flags_modules.json').write_text(json.dumps({'gb:rpg':['flags_module']},indent=2),encoding='utf-8')
print('5 GB flag/quest contracts bound to source.')
