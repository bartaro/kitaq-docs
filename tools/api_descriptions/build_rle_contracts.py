"""Bind the RAM/far/VRAM RLE descriptions to source and the decoded-tile example."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
header=REPOS/'kitaqgb/lib/rpg.h';library=REPOS/'kitaqgb/lib/rle.c';compiler=REPOS/'kitaqgb/kitaqgb/CodeGenerator.cs'
decl={r['name']:r for r in catalog.definitions(header)};defs={r['name']:r for r in catalog.definitions(library)}
path=SITE/'reference/gb-api.json';data=json.loads(path.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
program='samples/api-examples/gb/rle_shapes.c';sample=(SITE/program).read_text(encoding='utf-8');contracts={};evidence={}
for name,purpose,demo in [('rle_decode','rle_near','rle_demo_near'),('rle_decode_far','rle_far','rle_demo_far'),('__rle_decode_vram','rle_vram','rle_demo_vram')]:
    record=records[name]
    for key in ['ret','args','signature','path','line','comment','body']:record[key]=decl[name][key]
    record['arity_only']=False
    if name.startswith('__'):
        source=compiler.read_text(encoding='utf-8');start=source.index('if (funcName == "__rle_decode_vram")');masked=catalog.clean(source);i=masked.index('{',start)+1;depth=1
        while depth:depth+=(masked[i]=='{')-(masked[i]=='}');i+=1
        record['definition']=None;record['implementation_excerpt']=source[start:i]
        record['implementation_source']={'path':compiler.relative_to(REPOS).as_posix(),'line':source.count('\n',0,start)+1}
    else:record['definition']=defs[name]
    fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
    match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',sample,re.S);assert match
    code='\n'.join(s[4:] if s.startswith('    ') else s for s in match[1].splitlines())
    args=[['dst',['rle_vram_dst' if name.startswith('__') else 'rle_ram_dst']]]
    if name!='rle_decode':args.append(['bank',['rle_bank']])
    args.append(['src',['rle_src' if name=='rle_decode' else 'rle_far_src']])
    notes=['rle_format','rle_bounds']+(['rle_vram_timing','rle_vbk'] if name.startswith('__') else ['rle_ram_timing'])+['rle_bank_context','rle_build']
    contracts['gb:'+name]={'review':'rle-source-20260915','purpose':[purpose],'args':args,'returns':['rle_return'],'notes':notes,'record_sha256':fingerprint,
        'example':{'program':program,'code':code,'expected':[demo,'rle_shapes','rle_proof'],'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\samples\\api-examples\\gb\\rle_shapes.c -I .\\kitaqgb\\lib -I .\\kitaq-docs\\samples -o .\\out\\rle_shapes.gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --cart=mbc5 --romsize=64k --no-cache --no-disasm'}}
    evidence['gb:'+name]={'record_sha256':fingerprint,'header_line':record['line']}
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'rle_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'rle_review_sources.json').write_text(json.dumps({'source_sha256':{p.relative_to(REPOS).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [header,library,compiler,compiler.with_name('Assembler.cs'),compiler.with_name('Optimizer.cs')]},'records':evidence},indent=2),encoding='utf-8')
(HERE/'rle_modules.json').write_text(json.dumps({'gb:rpg':['rle_module']},indent=2),encoding='utf-8')
print('3 RLE contracts bound to source and decoded-tile examples.')
