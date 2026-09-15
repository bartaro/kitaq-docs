"""Bind the copied-payload runtime queue to its C implementation and executed example."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
header=REPOS/'kitaqfc/lib/runtime.h';implementation=REPOS/'kitaqfc/lib/runtime.c'
declarations={r['name']:r for r in catalog.definitions(header)}
definitions={r['name']:r for r in catalog.definitions(implementation)}
inventory=SITE/'reference/fc-api.json';data=json.loads(inventory.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
program='samples/api-examples/fc/runtime_queue.c';source=(SITE/program).read_text(encoding='utf-8')
rows={
 'nes_vram_queue_clear':('rq_clear',[],'none'),
 'nes_vram_queue_try_write':('rq_write',[('ppu_addr','vq_dst_fc'),('src','rq_source'),('len','rq_length')],'rq_result'),
 'nes_vram_queue_try_fill':('rq_fill',[('ppu_addr','vq_dst_fc'),('value','vq_fill_value'),('len','rq_length')],'rq_result'),
 'nes_vram_queue_nmi_flush':('rq_flush',[],'none')}
contracts={}
for name,(purpose,args,returns) in rows.items():
    record=records[name]
    for field in ['ret','args','signature','path','line','comment','body']:record[field]=declarations[name][field]
    record['definition']=definitions[name]
    match=re.search(r'// example:'+name+r':start\n(.*?)\s*// example:'+name+r':end',source,re.S);assert match,name
    snippet='\n'.join(line[4:] if line.startswith('    ') else line for line in match[1].strip().splitlines())
    contracts['fc:'+name]=dict(review='runtime-queue-source-20260915',purpose=[purpose],args=[[arg,[message]] for arg,message in args],returns=[returns],notes=['rq_storage','rq_setup','rq_timing']+(['vq_dst_fc'] if name.endswith('nmi_flush') else []),
        record_sha256=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest(),
        example=dict(program=program,code=snippet,expected=['rq_counts','rq_shapes'],build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\samples\\api-examples\\fc\\runtime_queue.c -I .\\kitaqfc\\lib -I .\\kitaq-docs\\samples -o .\\out\\runtime_queue.nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\api-examples\\fc\\vram_shapes.chr --no-cache --no-disasm'))
(HERE/'runtime_queue_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'runtime_queue_review_sources.json').write_text(json.dumps(dict(source_sha256={p.relative_to(REPOS).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [header,implementation]},records={k:c['record_sha256'] for k,c in contracts.items()}),indent=2),encoding='utf-8')
(HERE/'runtime-queue_modules.json').write_text(json.dumps({'fc:runtime':['rq_setup','rq_storage','rq_timing']},indent=2),encoding='utf-8')
inventory.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Four runtime queue contracts bound to C source and executed example.')
