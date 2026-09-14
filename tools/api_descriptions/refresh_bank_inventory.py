"""Refresh the reviewed bank API records from the public source checkout only."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'))
import catalog
catalog.ROOT=REPOS
common=['bank_switch','bank_get_current','far_data_read8','far_data_read16','far_data_read','farptr_make',
        'farptr_read8','farptr_read16','farptr_read','far_call','__bankof','__farcall','__bankswitch','__farpeek8','__farpeek16']
evidence={}
def block(text,anchor):
    """Retain a complete dispatch block, ignoring braces in comments and strings."""
    start=text.index(anchor);masked=catalog.clean(text);opened=masked.index('{',start)
    depth=1;end=opened+1
    while depth:
        if masked[end]=='{':depth+=1
        elif masked[end]=='}':depth-=1
        end+=1
    return text[start:end],text.count('\n',0,start)+1
for platform in ['gb','fc']:
    names=common+(['__farcall_ptr'] if platform=='gb' else ['__prg_bank_set'])
    path=SITE/'reference'/(platform+'-api.json');data=json.loads(path.read_text(encoding='utf-8'))
    records={r['name']:r for r in data['records']}
    lib=REPOS/('kitaq'+platform)/'lib';comp=REPOS/('kitaq'+platform)/('kitaq'+platform)/'CodeGenerator.cs'
    source=comp.read_text(encoding='utf-8-sig')
    headers=[lib/'bank.h']+([lib/'intrinsics.h'] if platform=='fc' else [])
    declarations={r['name']:r for header in headers for r in catalog.definitions(header)}
    definitions={r['name']:r for r in catalog.definitions(lib/'bank.c') if r['body']}
    for name in names:
        record=records[name]
        if name in declarations:
            declaration=declarations[name]
            for key in ['ret','args','signature','path','line','comment','body']:
                record[key]=declaration[key]
            record.pop('arity_only',None)
        if not name.startswith('__'):
            record['definition']=definitions.get(name)
        else:
            if platform=='gb':
                excerpt,line=block(source,'            if (funcName == "'+name+'")')
            elif name in ['__bankswitch','__prg_bank_set']:
                start=source.index('                case "__prg_bank_set":')
                end=source.index('                // Controller sampling',start)
                excerpt=source[start:end].rstrip();line=source.count('\n',0,start)+1
            elif name in ['__farpeek8','__farpeek16']:
                start=source.index('            EmitHelperStart("'+name+'");')
                end=source.index('            EmitHelperStart(',start+1)
                excerpt=source[start:end].rstrip();line=source.count('\n',0,start)+1
            elif name=='__bankof':
                anchor='            if (expr.MatchAny(Tag.Call, out funcExpr, out args) &&'
                start=source.rfind(anchor,0,source.index('                // Resolve __bankof from placement'))
                assert start>=0
                excerpt,offset=block(source[start:],anchor);line=source.count('\n',0,start)+offset
            else:
                dispatch=source.index('        void EmitCall(')
                excerpt,line=block(source[dispatch:],'            if (string.Equals(funcName, "__farcall", StringComparison.Ordinal))')
                line+=source.count('\n',0,dispatch)
            record['implementation_excerpt']=excerpt.strip()
            record['implementation_source']={'path':comp.relative_to(REPOS).as_posix(),'line':line}
        # Source snippets remain exact source; teaching programs are bound by bank_contracts.json.
        evidence[platform+':'+name]={'path':record['path'],'line':record['line'],
            'record_sha256':hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    for file in [*headers,lib/'bank.c',comp]:
        evidence[file.relative_to(REPOS).as_posix()]={'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
(HERE/'bank_review_sources.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
print('Refreshed 32 bank API records without changing inventory membership.')
