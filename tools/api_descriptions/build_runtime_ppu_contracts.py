"""Bind direct PPU helpers and both seek forms to source and executed examples."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
header=REPOS/'kitaqfc/lib/runtime.h';implementation=REPOS/'kitaqfc/lib/runtime.c'
declarations={r['name']:r for r in catalog.definitions(header)}
definitions={r['name']:r for r in catalog.definitions(implementation)}
pair_source=REPOS/'kitaqfc/lib/ppu.c'
pair_definitions={r['name']:r for r in catalog.definitions(pair_source)}
inventory=SITE/'reference/fc-api.json';data=json.loads(inventory.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
for name in ['nes_ppu_seek_bytes','nes_ppu_write_bytes','nes_ppu_fill']:
    if name not in records:
        record=dict(pair_definitions[name]);record.update(module='ppu',availability='implementation',definition=dict(pair_definitions[name]),example=None)
        data['records'].append(record);records[name]=record
rows={
 'nes_wait_nmi':('rp_wait_nmi',[],'runtime_ppu.c',['rq_setup']),
 'nes_vblank_wait':('rp_wait_blank',[],'runtime_ppu.c',['rq_setup']),
 'nes_ppu_seek':('rp_seek',[('ppu_addr','vq_dst_fc')],'runtime_ppu.c',['rq_setup','rp_timing']),
 'nes_ppu_seek_bytes':('rp_seek_bytes',[('hi / lo','rp_pair_address')],'ppu_address_pair.c',['rp_pair_setup','rp_timing']),
 'nes_ppu_stream_write':('rp_write',[('ppu_addr','vq_dst_fc'),('src','rp_source'),('len','rp_length')],'runtime_ppu.c',['rq_setup','rp_timing']),
 'nes_ppu_stream_fill':('rp_fill',[('ppu_addr','vq_dst_fc'),('value','vq_fill_value'),('len','rp_length')],'runtime_ppu.c',['rq_setup','rp_timing']),
 'nes_ppu_write_bytes':('rp_pair_write',[('hi / lo','rp_pair_address'),('src','rp_source'),('count','rp_pair_length')],'ppu_address_pair.c',['rp_pair_setup','rp_timing']),
 'nes_ppu_fill':('rp_pair_fill',[('hi / lo','rp_pair_address'),('value','vq_fill_value'),('count','rp_pair_length')],'ppu_address_pair.c',['rp_pair_setup','rp_timing'])}
def example(filename,marker):
    program='samples/api-examples/fc/'+filename;source=(SITE/program).read_text(encoding='utf-8')
    match=re.search(r'// example:'+marker+r':start\n(.*?)\s*// example:'+marker+r':end',source,re.S);assert match,marker
    snippet='\n'.join(line[4:] if line.startswith('    ') else line for line in match[1].strip().splitlines())
    return dict(program=program,code=snippet,expected=['rp_scene'] if filename=='runtime_ppu.c' else ['rp_pair_scene'],build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaqfc\\lib -I .\\kitaq-docs\\samples -o .\\out\\'+Path(filename).stem+'.nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\api-examples\\fc\\vram_shapes.chr --no-cache --no-disasm')
contracts={}
for name,(purpose,args,filename,notes) in rows.items():
    record=records[name];primary=declarations[name] if name in declarations else pair_definitions[name]
    for field in ['ret','args','signature','path','line','comment','body']:record[field]=primary[field]
    record['definition']=definitions[name] if name in definitions else pair_definitions[name]
    contract=dict(review='runtime-ppu-source-20260915',purpose=[purpose],args=[[arg,[message]] for arg,message in args],returns=['none'],notes=notes,example=example(filename,name))
    record.pop('implementation_excerpt',None)
    record.pop('alternative_definition',None)
    contract['record_sha256']=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
    contracts['fc:'+name]=contract
(HERE/'runtime_ppu_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'runtime_ppu_review_sources.json').write_text(json.dumps(dict(source_sha256={p.relative_to(REPOS).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [header,implementation,pair_source]},records={k:c['record_sha256'] for k,c in contracts.items()}),indent=2),encoding='utf-8')
(HERE/'runtime-ppu_modules.json').write_text(json.dumps({'fc:ppu':['rp_pair_setup']},indent=2),encoding='utf-8')
inventory.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
# Add the two headerless public functions to the existing PPU section. Other
# internal C helpers are separately audited, not presumed public by their name.
for language in ['', 'en']:
    page=SITE/language/'fc-library.html';raw=page.read_bytes();text=raw.decode('utf-8')
    for name in ['nes_ppu_seek_bytes','nes_ppu_write_bytes','nes_ppu_fill']:
        if 'id="api-'+name+'"' not in text:
            text=re.sub(r'(<h3[^>]*id="module-ppu"[^>]*>.*?</h3>)',lambda m:m[1]+'<details class="api searchable" id="api-'+name+'"><summary><code>'+name+'</code></summary></details>',text,count=1,flags=re.S)
    text=re.sub(r'(<h3[^>]*id="module-ppu"[^>]*>).*?(</h3>)',r'\1ppu.h / ppu.c\2',text,count=1,flags=re.S)
    page.write_bytes(text.encode('utf-8'))
print('Eight direct PPU contracts, including distinct word and byte-pair seek calls.')
