"""Bind the thirteen RNG APIs to exact compiler/library source and teaching programs."""
from pathlib import Path
import hashlib, json, re, sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
contracts={};sources={};evidence={}
library_names=['rng_seed','rng8','rng_next8','rng16','rng_next16','rand_range','rng_range','rng_chance','weighted_choice']
purposes={'rng_seed':'rng_wrap_seed','rng8':'rng_wrap_byte','rng_next8':'rng_alias_byte','rng16':'rng_word','rng_next16':'rng_alias_word','rand_range':'rng_bound','rng_range':'rng_alias_bound','rng_chance':'rng_chance','weighted_choice':'rng_weighted'}
demos={'rng_seed':'rng_demo_wrap','rng8':'rng_demo_wrap','rng_next8':'rng_demo_next8','rng16':'rng_demo_word','rng_next16':'rng_demo_next16','rand_range':'rng_demo_bound','rng_range':'rng_demo_alias_bound','rng_chance':'rng_demo_chance','weighted_choice':'rng_demo_weighted'}
def block(source,start):
    masked=catalog.clean(source);i=masked.index('{',start)+1;depth=1
    while depth:depth+=(masked[i]=='{')-(masked[i]=='}');i+=1
    return source[start:i].strip(),source.count('\n',0,start)+1

for platform in ['gb','fc']:
    header=REPOS/('kitaq'+platform)/'lib'/('rpg.h' if platform=='gb' else 'intrinsics.h')
    compiler=REPOS/('kitaq'+platform)/('kitaq'+platform)/'CodeGenerator.cs'
    source=compiler.read_text(encoding='utf-8')
    declarations={r['name']:r for r in catalog.definitions(header)}
    for p in [header,compiler]:sources[p.relative_to(REPOS).as_posix()]=sha(p)
    if platform=='gb':
        library=REPOS/'kitaqgb/lib/rng.c';definitions={r['name']:r for r in catalog.definitions(library)}
        sources[library.relative_to(REPOS).as_posix()]=sha(library)
    path=SITE/'reference'/(platform+'-api.json');data=json.loads(path.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
    for name in ['__rng_seed','__rng8']+(library_names if platform=='gb' else []):
        record=records[name]
        for key in ['ret','args','signature','path','line','comment','body']:record[key]=declarations[name][key]
        record['arity_only']=False
        if name.startswith('__'):
            if platform=='gb':excerpt,line=block(source,source.index('if (funcName == "'+name+'")'))
            else:
                start=source.index('            EmitHelperStart("'+name+'");')
                end=source.index('            EmitAsm("RTS");',start)+len('            EmitAsm("RTS");')
                excerpt=source[start:end].strip();line=source.count('\n',0,start)+1
                dispatch=re.search(r'case "'+name+r'":.*?(?=\n *case ")',source,re.S);assert dispatch
                excerpt=dispatch[0].strip()+'\n\n'+excerpt
            record['definition']=None;record['implementation_excerpt']=excerpt
            record['implementation_source']={'path':compiler.relative_to(REPOS).as_posix(),'line':line}
        else:
            record['definition']=definitions[name];record.pop('implementation_excerpt',None);record.pop('implementation_source',None)
        fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
        sample='rng_core' if platform=='fc' else 'rng_choices' if name in ['rand_range','rng_range','rng_chance','weighted_choice'] else 'rng_values'
        program='samples/api-examples/'+platform+'/'+sample+'.c';sample_source=(SITE/program).read_text(encoding='utf-8')
        match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',sample_source,re.S);assert match,name
        code='\n'.join(s[4:] if s.startswith('    ') else s for s in match[1].splitlines() if not re.match(r'\s*// example:',s))
        build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaq'+platform+'\\kitaq'+platform+'.exe .\\kitaq-docs\\'+program.replace('/','\\')
        if platform=='gb':build+=' .\\kitaqgb\\lib\\rng.c'
        build+=' -I .\\kitaq'+platform+'\\lib -I .\\kitaq-docs\\samples -o .\\out\\'+sample
        build+='.gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb' if platform=='gb' else '.nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\font.chr'
        build+=' --no-cache --no-disasm'
        args=[];notes=['rng_shared','rng_targets'];result=['rng_ret_byte']
        purpose=purposes.get(name,'rng_seed_'+platform if name=='__rng_seed' else 'rng_byte_'+platform)
        demo=demos.get(name,('rng_demo_seed_' if name=='__rng_seed' else 'rng_demo_byte_')+platform)
        if name in ['__rng_seed','rng_seed']:args=[['seed',['rng_seed_arg']]];result=['none'];notes.insert(0,'rng_zero_'+platform)
        if name=='__rng8':notes[:0]=['rng_algorithm_'+platform,'rng_zero_'+platform]
        if name in ['rng16','rng_next16']:result=['rng_ret_word']
        if name in ['rand_range','rng_range']:args=[['max',['rng_max_arg']]];result=['rng_ret_bound'];notes.insert(0,'rng_modulo')
        if name=='rng_chance':args=[['percent',['rng_percent_arg']]];result=['rng_ret_chance'];notes.insert(0,'rng_modulo')
        if name=='weighted_choice':args=[['weights',['rng_weights_arg']],['count',['rng_count_arg']]];result=['rng_ret_weighted'];notes.insert(0,'rng_weight_bias')
        if platform=='gb':notes.append('rng_link')
        contracts[platform+':'+name]={'review':'rng-source-20260915','purpose':[purpose],'args':args,'returns':result,'notes':notes,'record_sha256':fingerprint,'example':{'program':program,'code':code,'build':build,'expected':[demo,'rng_screen_'+platform,'rng_proof']}}
        evidence[platform+':'+name]={'record_sha256':fingerprint,'header_line':record['line']}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'rng_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'rng_review_sources.json').write_text(json.dumps({'source_sha256':sources,'records':evidence},indent=2),encoding='utf-8')
(HERE/'rng_modules.json').write_text(json.dumps({'gb:rpg':['rng_module']},indent=2),encoding='utf-8')
print('13 RNG contracts bound to source and Japanese/English examples.')
