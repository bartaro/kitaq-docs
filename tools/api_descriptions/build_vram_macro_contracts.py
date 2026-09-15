"""Describe five queue macros using their exact expansions and executed program."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
header=REPOS/'kitaqfc/lib/nes_game.h';text=header.read_text(encoding='utf-8')
inventory=SITE/'reference/fc-api.json';data=json.loads(inventory.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
program='samples/api-examples/fc/vram_queue_macros.c';source=(SITE/program).read_text(encoding='utf-8')
specs={
 'nes_vram_put':('qi_put',[('addr','vq_dst_fc'),('value','vq_fill_value')]),
 'nes_vram_copy':('qi_copy',[('addr','vq_dst_fc'),('src','vq_source'),('len','qi_length')]),
 'nes_vram_fill':('qi_fill',[('addr','vq_dst_fc'),('value','vq_fill_value'),('len','qi_length')]),
 'nes_vram_commit':('qi_commit',[]),
 'nes_vram_clear_queue':('qi_clear',[])}
contracts={}
for name,(purpose,args) in specs.items():
    record=records[name]
    declaration=re.search(r'(?m)^#define[ \t]+'+name+r'\([^\n]*',text);assert declaration,name
    record['signature']=declaration[0];record['line']=text.count('\n',0,declaration.start())+1
    record['implementation_excerpt']=declaration[0]
    snippet=re.search(r'// example:'+name+r':start\n(.*?)\s*// example:'+name+r':end',source,re.S);assert snippet,name
    code='\n'.join(line[4:] if line.startswith('    ') else line for line in snippet[1].strip().splitlines())
    notes=(['qi_append'] if args else [])+['vq_units_fc','vm_surface','vq_serialize']
    contracts['fc:'+name]=dict(review='vram-macros-source-20260915',purpose=['ol_macro',purpose],args=[[arg,[message]] for arg,message in args],returns=['none'],notes=notes,
        record_sha256=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest(),
        example=dict(program=program,code=code,expected=['vm_example','qi_example_counts','qi_example_shapes','qi_example_zero'],
        build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\samples\\api-examples\\fc\\vram_queue_macros.c -I .\\kitaqfc\\lib -I .\\kitaq-docs\\samples -o .\\out\\vram_queue_macros.nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\api-examples\\fc\\vram_shapes.chr --no-cache --no-disasm'))
(HERE/'vram_macro_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'vram_macro_review_sources.json').write_text(json.dumps({'header_sha256':hashlib.sha256(header.read_bytes()).hexdigest(),'records':{key:contract['record_sha256'] for key,contract in contracts.items()}},indent=2),encoding='utf-8')
inventory.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Five queue macro contracts bound to source and a separately executed program.')
