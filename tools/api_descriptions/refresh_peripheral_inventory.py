"""Refresh the 13 keyboard, light-gun and serial-bit intrinsic records."""
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'))
import catalog
catalog.ROOT=REPOS
comp=REPOS/'kitaqfc/kitaqfc/CodeGenerator.cs';source=comp.read_text(encoding='utf-8-sig');masked=catalog.clean(source)
path=SITE/'reference/fc-api.json';data=json.loads(path.read_text(encoding='utf-8'))
declarations={r['name']:r for r in catalog.definitions(REPOS/'kitaqfc/lib/intrinsics.h')}
start=source.index('        void EmitNormalizeBoolFromMask(');opened=masked.index('{',start);end=opened+1;depth=1
while depth:
    if masked[end]=='{':depth+=1
    elif masked[end]=='}':depth-=1
    end+=1
normalize=source[start:end];count=0
for r in data['records']:
    name=r['name']
    if not name.startswith(('__fkb_','__zapper_','__serial_')):continue
    count+=1
    for key in ['ret','args','signature','path','line','comment','body']:r[key]=declarations[name][key]
    target=name+'2' if name in ['__zapper_light','__zapper_trigger'] else name
    if name.startswith('__zapper_raw'):
        start=source.index('                case "'+name+'":');end=source.index('\n',start)
        excerpt=source[start:end]
    else:
        start=source.index('            EmitHelperStart("'+target+'");');end=source.index('            EmitHelperStart(',start+1)
        excerpt=source[start:end]
        if target.startswith('__zapper_'):
            excerpt='\n'.join(excerpt.splitlines()[:2])+'\n'+normalize
        else:
            # Stop at this helper's final RTS, excluding the next method's preamble.
            last=excerpt.rfind('EmitAsm("RTS");');assert last>=0
            excerpt=excerpt[:last+len('EmitAsm("RTS");')]
    r['implementation_excerpt']=excerpt.strip()
    r['implementation_source']=dict(path=comp.relative_to(REPOS).as_posix(),line=source.count('\n',0,start)+1)
assert count==13
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print('Refreshed 13 peripheral records.')
