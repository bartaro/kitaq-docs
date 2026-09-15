"""Bind twelve memory APIs to declarations, compiler bodies and checked RAM examples."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
templates=json.loads((HERE/'memory_intrinsic_example_texts.json').read_text(encoding='utf-8'))
shared=(SITE/'samples/memory_example_checks.h').read_text(encoding='utf-8')
rows={'__memcpy':('mi_copy',257,'COPY WORD'),'__memset':('mi_fill',257,'FILL WORD'),'__memcpy_small':('mi_copy_small',255,'COPY BYTE'),'__memset_small':('mi_fill_small',255,'FILL BYTE'),'__copy16':('mi_copy16',16,'COPY16'),'__copy32':('mi_copy32',32,'COPY32')}
contracts={};messages={};evidence={};source_hashes={}

def balanced(source,start):
    masked=catalog.clean(source);brace=masked.index('{',start);depth=1;i=brace+1
    while depth:
        depth+=(masked[i]=='{')-(masked[i]=='}');i+=1
    return source[start:i].strip(),source.count('\n',0,start)+1

def method(source,name):
    match=re.search(r'(?m)^ *(?:void|bool) '+name+r'\(',catalog.clean(source));assert match,name
    return balanced(source,match.start())[0]

for platform in ['gb','fc']:
    header=REPOS/('kitaq'+platform)/'lib'/('rpg.h' if platform=='gb' else 'intrinsics.h')
    compiler=REPOS/('kitaq'+platform)/('kitaq'+platform)/'CodeGenerator.cs'
    lowerer=compiler.parent/'Lowerer.cs'
    source=compiler.read_text(encoding='utf-8');lower=lowerer.read_text(encoding='utf-8')
    for path in [header,compiler,lowerer]:source_hashes[path.relative_to(REPOS).as_posix()]=sha(path)
    declarations={r['name']:r for r in catalog.definitions(header)}
    path=SITE/'reference'/(platform+'-api.json');data=json.loads(path.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
    program='samples/api-examples/'+platform+'/memory_intrinsics.c'
    build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaq'+platform+'\\kitaq'+platform+'.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaq'+platform+'\\lib -I .\\kitaq-docs\\samples -o .\\out\\memory_intrinsics.'
    build+='gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb' if platform=='gb' else 'nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\font.chr'
    build+=' --no-cache --no-disasm'
    for name,(purpose,count,label) in rows.items():
        fixed=name.startswith('__copy');fill=name.startswith('__memset');small=name.endswith('_small')
        record=records[name]
        for key in ['ret','args','signature','path','line','comment','body']:record[key]=declarations[name][key]
        if platform=='gb':
            base='__copy16' if fixed else '__memset' if fill else '__memcpy'
            a=source.index('if (funcName == "'+base+'" ||')
            excerpt,line=balanced(source,a)
            if fixed:excerpt+='\n\n'+method(source,'EmitRamMemcpyLoop')
        else:
            match=re.search(r'case "'+name+r'":.*?(?=\n *case ")',source,re.S);assert match,name
            excerpt=match[0].strip();line=source.count('\n',0,match.start())+1
            if not fixed:
                excerpt+='\n\n'+method(source,'TryEmitMemcpyOrMemsetInline')
                helper=method(source,'EmitHelperMemoryAndBit')
                excerpt+='\n\n'+helper[:helper.index('            EmitBitHelper(')].rstrip()+'\n        }'
            excerpt+='\n\n'+method(source,'EmitFixedMemcpy')
        # Preserve the call-lowering stage that evaluates observable argument effects.
        lower_excerpt,lower_line=balanced(lower,lower.index('if (expr.MatchAny(Tag.Call, out callFunc, out callArgs))'))
        record['arity_only']=False;record['definition']=None
        record['implementation_source']={'path':compiler.relative_to(REPOS).as_posix(),'line':line}
        record['implementation_excerpt']=excerpt+'\n\n// '+lowerer.relative_to(REPOS).as_posix()+':'+str(lower_line)+'\n'+lower_excerpt
        fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
        match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',shared,re.S);assert match,name
        snippet='\n'.join(line[4:] if line.startswith('    ') else line for line in match[1].splitlines())
        demo='mi_demo_'+name[2:]
        messages[demo]=[s.format(api=name,count=count,row=label,display=f'{count:03d}') for s in templates['mi_demo_'+('fill' if fill else 'copy')+'_template']]
        args=[['dst',['mi_dst']],['value' if fill else 'src',['mi_value' if fill else 'mi_src']]]
        if not fixed:args.append(['count' if platform=='gb' and not small else 'len',['mi_byte_count' if small else 'mi_word_count']])
        notes=([] if fixed else ['mi_zero'])+([] if fill else ['mi_overlap'])+['mi_mapping','mi_'+platform+'_access']
        contracts[platform+':'+name]={'review':'memory-intrinsics-source-20260915','purpose':[purpose],'args':args,'returns':['none'],'notes':notes,'record_sha256':fingerprint,'example':{'program':program,'code':snippet,'build':build,'expected':[demo,'mi_screen','mi_colors']}}
        evidence[platform+':'+name]={'record_sha256':fingerprint,'header_line':record['line'],'compiler_line':line,'lowerer_line':lower_line}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(contracts)==12
(HERE/'memory_intrinsic_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'memory_intrinsic_generated_texts.json').write_text(json.dumps(messages,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'memory_intrinsic_review_sources.json').write_text(json.dumps({'source_sha256':source_hashes,'records':evidence},indent=2),encoding='utf-8')
print('12 memory contracts bound to source, checked buffers and complete examples.')
