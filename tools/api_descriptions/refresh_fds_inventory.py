"""Refresh only the 20 non-audio FDS records from the public compiler checkout."""
from pathlib import Path
import json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'))
import catalog
catalog.ROOT=REPOS
lib=REPOS/'kitaqfc/lib';comp=REPOS/'kitaqfc/kitaqfc/CodeGenerator.cs'
source=comp.read_text(encoding='utf-8-sig');masked=catalog.clean(source)
path=SITE/'reference/fc-api.json';data=json.loads(path.read_text(encoding='utf-8'))
headers=[lib/'intrinsics.h',lib/'fds.h',lib/'fds_file.h',lib/'fds_overlay.h',lib/'nes_game.h']
declarations={r['name']:r for h in headers for r in catalog.definitions(h)}
names=['__fds_'+n for n in ['available','disk_ready','side','error','wait_ready','wait_insert','file_exists','file_size',
                          'current_bank','is_bank_resident','overlay_function_count','load_file','save_file','load_bank',
                          'require_bank','load_overlay','farcall','overlay_farcall']]+['nes_fds_load_bank','nes_fds_farcall']
count=0
for record in data['records']:
    name=record['name']
    if name not in names:continue
    count+=1
    if name in declarations:
        for key in ['ret','args','signature','path','line','comment','body']:
            record[key]=declarations[name][key]
    target='__fds_wait_ready' if name=='__fds_wait_insert' else name
    if name.startswith('nes_'):continue
    anchor='            EmitHelperStart("'+target+'");'
    if anchor in source:
        start=source.index(anchor);end=source.index('            EmitHelperStart(',start+len(anchor))
    elif name in ['__fds_farcall','__fds_overlay_farcall']:
        start=source.index('            if (string.Equals(funcName, "__fds_overlay_farcall", StringComparison.Ordinal)')
        opened=masked.index('{',start);depth=1;end=opened+1
        while depth:
            if masked[end]=='{':depth+=1
            elif masked[end]=='}':depth-=1
            end+=1
    elif name=='__fds_available':
        start=source.index('            if (funcName == "__fds_available")');end=source.index('            if (!isFds)',start)
    else:
        start=source.index('                case "'+name+'":',source.index('        bool EmitFdsIntrinsicCall('))
        end=source.index('                case ',start+1)
    record['implementation_excerpt']=source[start:end].strip()
    record['implementation_source']=dict(path=comp.relative_to(REPOS).as_posix(),line=source.count('\n',0,start)+1)
assert count==20
path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Refreshed 20 FDS API records.')
