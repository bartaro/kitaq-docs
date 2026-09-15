"""Bind six GB text-layout contracts to their declarations, bodies and example."""
from pathlib import Path
import hashlib, json, re, sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog
catalog.ROOT=REPOS
header=REPOS/'kitaqgb/lib/rpg.h';library=REPOS/'kitaqgb/lib/text.c'
decl={r['name']:r for r in catalog.definitions(header)}
defs={r['name']:r for r in catalog.definitions(library)}
path=SITE/'reference/gb-api.json';data=json.loads(path.read_text(encoding='utf-8'))
records={r['name']:r for r in data['records']}
program='samples/api-examples/gb/text_layout.c';sample=(SITE/program).read_text(encoding='utf-8')
contracts={};evidence={}
for name,kind in [('text_window','window'),('text_clear_rect','clear'),('text_print_xy','xy'),
                  ('text_print_u8','u8'),('text_print_u16','u16'),('text_print_s16','s16')]:
    record=records[name]
    for key in ['ret','args','signature','path','line','comment','body']:record[key]=decl[name][key]
    record['definition']=defs[name];record['arity_only']=False
    fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
    match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',sample,re.S);assert match
    code='\n'.join(line[4:] if line.startswith('    ') else line for line in match[1].splitlines())
    args=[['x',['tl_x']],['y',['tl_y']]]
    if kind in ['window','clear']:args += [['w',['tl_w']],['h',['tl_h']]]
    elif kind=='xy':args += [['str',['tl_str']]]
    else:args += [['value',['tl_'+{'u8':'value8','u16':'value16','s16':'values16'}[kind]]]]
    notes=['tl_map','tl_font','tl_bounds','tl_timing','tl_build']
    if kind in ['u8','u16','s16','clear']:notes.insert(3,'tl_numeric')
    contracts['gb:'+name]={'review':'text-layout-source-20260915','purpose':['tl_'+kind],
        'args':args,'returns':['tl_return'],'notes':notes,'record_sha256':fingerprint,
        'example':{'program':program,'code':code,'expected':['tl_demo_'+kind,'tl_proof'],
            'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaqgb\\lib -I .\\kitaq-docs\\samples -o .\\out\\text_layout.gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --cart=mbc5 --romsize=64k --no-cache --no-disasm'}}
    evidence['gb:'+name]={'record_sha256':fingerprint,'header_line':record['line'],'definition_line':defs[name]['line']}
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'text-layout_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
sources=[header,library,REPOS/'kitaqgb/kitaqgb/CodeGenerator.cs']
(HERE/'text-layout_review_sources.json').write_text(json.dumps({'source_sha256':{p.relative_to(REPOS).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'records':evidence},indent=2),encoding='utf-8')
(HERE/'text-layout_modules.json').write_text(json.dumps({'gb:rpg':['tl_module']},indent=2),encoding='utf-8')
print('6 text-layout contracts bound to source.')
