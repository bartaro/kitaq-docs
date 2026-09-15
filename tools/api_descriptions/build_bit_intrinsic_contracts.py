"""Bind GB/FC bit operations to exact compiler source and authored English/Japanese prose."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
contracts={};sources={};evidence={}
shared=(SITE/'samples/bit_example_checks.h').read_text(encoding='utf-8')
def block(source,start):
    masked=catalog.clean(source);i=masked.index('{',start)+1;depth=1
    while depth:depth+=(masked[i]=='{')-(masked[i]=='}');i+=1
    return source[start:i].strip(),source.count('\n',0,start)+1
def method(source,name):
    match=re.search(r'(?m)^ *(?:void|bool) '+name+r'\(',catalog.clean(source));assert match,name
    return block(source,match.start())[0]
for platform in ['gb','fc']:
    header=REPOS/('kitaq'+platform)/'lib'/('rpg.h' if platform=='gb' else 'intrinsics.h')
    compiler=REPOS/('kitaq'+platform)/('kitaq'+platform)/'CodeGenerator.cs'
    source=compiler.read_text(encoding='utf-8')
    declarations={r['name']:r for r in catalog.definitions(header)}
    path=SITE/'reference'/(platform+'-api.json');data=json.loads(path.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
    for p in [header,compiler]:sources[p.relative_to(REPOS).as_posix()]=sha(p)
    program='samples/api-examples/'+platform+'/bit_intrinsics.c'
    build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaq'+platform+'\\kitaq'+platform+'.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaq'+platform+'\\lib -I .\\kitaq-docs\\samples -o .\\out\\bit_intrinsics.'
    build+='gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb' if platform=='gb' else 'nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\font.chr'
    build+=' --no-cache --no-disasm'
    for op in ['test','set','clear','toggle']:
        name='__bit_'+op;record=records[name]
        for key in ['ret','args','signature','path','line','comment','body']:record[key]=declarations[name][key]
        if platform=='gb':excerpt,line=block(source,source.index('if (funcName == "__bit_test" ||'))
        else:
            match=re.search(r'case "'+name+r'":.*?(?=\n *case ")',source,re.S);assert match,name
            excerpt=match[0].strip();line=source.count('\n',0,match.start())+1
            excerpt+='\n\n'+method(source,'TryEmitBitIntrinsicInline')+'\n\n'+method(source,'EmitBitHelper')
        record['arity_only']=False;record['definition']=None
        record['implementation_source']={'path':compiler.relative_to(REPOS).as_posix(),'line':line};record['implementation_excerpt']=excerpt
        fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
        match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',shared,re.S);assert match,name
        code='\n'.join(s[4:] if s.startswith('    ') else s for s in match[1].splitlines())
        notes=['bi_limits']+(['bi_concurrent'] if op!='test' else [])+(['bi_fc_helper'] if platform=='fc' else [])
        contracts[platform+':'+name]={'review':'bit-intrinsics-source-20260915','purpose':['bi_'+op],
          'args':[['p' if platform=='gb' else 'base',['bi_base']],['bit_index' if platform=='gb' else 'bit',['bi_index']]],
          'returns':['bi_return_'+platform if op=='test' else 'none'],'notes':notes,'record_sha256':fingerprint,
          'example':{'program':program,'code':code,'build':build,'expected':['bi_demo_'+op,'bi_screen_'+platform,'bi_proof']}}
        evidence[platform+':'+name]={'record_sha256':fingerprint,'header_line':record['line'],'compiler_line':line}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'bit_intrinsic_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'bit_intrinsic_review_sources.json').write_text(json.dumps({'source_sha256':sources,'records':evidence},indent=2),encoding='utf-8')
print('8 bit-operation contracts bound to source and Japanese/English examples.')
