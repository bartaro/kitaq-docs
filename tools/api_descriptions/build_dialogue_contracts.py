"""Bind windowed dialogue operations to exact library bodies and complete programs."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog
catalog.ROOT=REPOS
header=REPOS/'kitaqgb/lib/rpg.h';library=REPOS/'kitaqgb/lib/text.c'
decl={r['name']:r for r in catalog.definitions(header)};defs={r['name']:r for r in catalog.definitions(library)}
path=SITE/'reference/gb-api.json';data=json.loads(path.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
contracts={};evidence={}
for name,kind in [('text_open','open'),('text_close','close'),('text_set_speed','speed'),
                  ('text_print','print'),('text_print_far','far'),('text_choice','choice')]:
    record=records[name]
    for key in ['ret','args','signature','path','line','comment','body']:record[key]=decl[name][key]
    record['definition']=defs[name];record['arity_only']=False
    fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
    stem='dialogue_choice' if kind=='choice' else 'dialogue_flow'
    program='samples/api-examples/gb/'+stem+'.c';sample=(SITE/program).read_text(encoding='utf-8')
    match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',sample,re.S);assert match
    code='\n'.join(line[4:] if line.startswith('    ') else line for line in match[1].splitlines())
    args=[]
    if kind=='open':args=[[key,['dlg_'+key]] for key in ['x','y','w','h']]
    elif kind=='speed':args=[['speed',['dlg_speed_arg']]]
    elif kind=='print':args=[['str',['dlg_str']]]
    elif kind=='far':args=[['bank',['dlg_bank']],['str',['dlg_far_str']]]
    elif kind=='choice':args=[['choices',['dlg_choices']],['count',['dlg_count']]]
    notes=['dlg_setup','dlg_blocking','dlg_timing','dlg_build']
    if kind in ['print','far']:notes[1:1]=['dlg_controls','dlg_paging','dlg_closed']
    if kind=='close':notes.insert(1,'dlg_closed')
    if kind=='choice':notes[1:1]=['dlg_choice_area','dlg_choice_input']
    contracts['gb:'+name]={'review':'dialogue-source-20260915','purpose':['dlg_'+kind],
        'args':args,'returns':['dlg_choice_return' if kind=='choice' else 'dlg_void'],'notes':notes,'record_sha256':fingerprint,
        'example':{'program':program,'code':code,'expected':['dlg_demo_'+kind,'dlg_proof'],
        'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaqgb\\lib -I .\\kitaq-docs\\samples -o .\\out\\'+stem+'.gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --cart=mbc5 --romsize=64k --no-cache --no-disasm'}}
    evidence['gb:'+name]={'record_sha256':fingerprint,'header_line':record['line'],'definition_line':defs[name]['line']}
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'dialogue_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
sources=[header,library,REPOS/'kitaqgb/kitaqgb/CodeGenerator.cs']
(HERE/'dialogue_review_sources.json').write_text(json.dumps({'source_sha256':{p.relative_to(REPOS).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'records':evidence},indent=2),encoding='utf-8')
(HERE/'dialogue_modules.json').write_text(json.dumps({'gb:rpg':['dlg_module']},indent=2),encoding='utf-8')
print('6 dialogue contracts bound to source.')
