"""Document implemented PPU library calls and their executable color lesson."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
header=REPOS/'kitaqfc/lib/ppu.h';implementation=header.with_suffix('.c')
declarations={r['name']:r for r in catalog.definitions(header)}
definitions={r['name']:r for r in catalog.definitions(implementation)}
inventory=SITE/'reference/fc-api.json';data=json.loads(inventory.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
program='samples/api-examples/fc/ppu_implemented.c';source=(SITE/program).read_text(encoding='utf-8')
rows={
 'nes_ppu_screen_off':('pd_off',[],'pd_return'),
 'nes_ppu_screen_on':('pd_on',[('ctrl / mask','pd_controls')],'pd_return'),
 'nes_ppu_load_palette':('pd_palette',[('pal32','pd_pal_arg')],'pd_return'),
 'nes_ppu_clear_nt':('pd_clear',[('nt_base / tile / attr','pd_nt_args')],'pd_return')}
contracts={}
for name,(purpose,args,returns) in rows.items():
    record=records[name]
    for field in ['ret','args','signature','path','line','comment','body']:record[field]=declarations[name][field]
    record['definition']=definitions[name];record['availability']='implementation';record.pop('implementation_excerpt',None)
    match=re.search(r'// example:'+name+r':start\n(.*?)\s*// example:'+name+r':end',source,re.S);assert match,name
    snippet='\n'.join(line[4:] if line.startswith('    ') else line for line in match[1].strip().splitlines())
    contracts['fc:'+name]=dict(review='ppu-declarations-source-20260915',purpose=[purpose],args=[[arg,[message]] for arg,message in args],returns=[returns],notes=['pd_scope'],
        record_sha256=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest(),
        example=dict(program=program,code=snippet,expected=['pd_scene'],build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\samples\\api-examples\\fc\\ppu_implemented.c -I .\\kitaqfc\\lib -I .\\kitaq-docs\\samples -o .\\out\\ppu_implemented.nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\api-examples\\fc\\vram_shapes.chr --no-cache --no-disasm'))
(HERE/'ppu_declaration_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'ppu_declaration_review_sources.json').write_text(json.dumps(dict(source_sha256={p.relative_to(REPOS).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [header,implementation]},records={k:c['record_sha256'] for k,c in contracts.items()}),indent=2),encoding='utf-8')
inventory.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Four PPU library calls bound to implementations and executed examples.')
