"""Bind nine FC OAM intrinsics to their individual compiler paths and executed samples."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
header=REPOS/'kitaqfc/lib/intrinsics.h';compiler=REPOS/'kitaqfc/kitaqfc/CodeGenerator.cs';source=compiler.read_text(encoding='utf-8')
declarations={r['name']:r for r in catalog.definitions(header)}
p=SITE/'reference/fc-api.json';data=json.loads(p.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
shared=(SITE/'samples/fc_oam_example.h').read_text(encoding='utf-8')
rows={
 '__oam_clear':('fo_clear',[],'none',['fo_shadow']),
 '__sprite_set':('fo_set',[('index','fo_index'),('x','sp_x'),('y','sp_y_fc'),('tile','sp_tile_arg'),('attr','fo_attr_arg')],'none',['fo_shadow']),
 '__sprite_move':('fo_move',[('index','fo_index'),('x','sp_x'),('y','sp_y_fc')],'none',['fo_shadow']),
 '__sprite_tile':('fo_tile',[('index','fo_index'),('tile','sp_tile_arg')],'none',['fo_shadow']),
 '__sprite_attr':('fo_attr',[('index','fo_index'),('attr','fo_attr_arg')],'none',['fo_shadow']),
 '__sprite_hide':('fo_hide',[('index','fo_index')],'none',['fo_shadow']),
 '__metasprite_draw':('fo_meta',[('oam_index','fo_index'),('base_x','sp_x'),('base_y','sp_y_fc'),('metasprite','fo_stream_arg')],'fo_meta_return',['fo_shadow','fo_meta_limit']),
 '__oam_dma':('fo_dma',[],'none',['fo_timing']),
 '__oam_dma_page':('fo_dma_page',[('page','fo_page_arg')],'none',['fo_timing'])}
contracts={};evidence={}
for name,(purpose,args,returns,notes) in rows.items():
 record=records[name]
 for key in ['ret','args','signature','path','line','comment','body']:record[key]=declarations[name][key]
 if name in ['__oam_dma','__oam_dma_page']:
  excerpt=next(line.strip() for line in source.splitlines() if 'case "'+name+'":' in line)
 else:
  a=source.index('            EmitHelperStart("'+name+'");');b=source.index('            EmitAsm("RTS");',a)+len('            EmitAsm("RTS");');excerpt=source[a:b].strip()
 record['implementation_excerpt']=excerpt
 fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
 program='samples/api-examples/fc/'+('oam_page.c' if name=='__oam_dma_page' else 'oam_intrinsics.c')
 text=shared+'\n'+(SITE/program).read_text(encoding='utf-8')
 match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',text,re.S);assert match,name
 snippet='\n'.join(line.strip() for line in match[1].splitlines())
 build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaqfc\\lib -I .\\kitaq-docs\\samples --nes-chr=.\\kitaq-docs\\samples\\sprite_example.chr -o .\\out\\'+Path(program).stem+'.nes --no-cache --no-disasm'
 contracts['fc:'+name]={'review':'fc-oam-source-20260915','purpose':[purpose],'args':[[arg,[key]] for arg,key in args],'returns':[returns],'notes':notes,'record_sha256':fingerprint,'example':{'program':program,'code':snippet,'build':build,'expected':['fo_scene','fo_page_example' if name=='__oam_dma_page' else 'fo_default_example']}}
 evidence[name]={'record_sha256':fingerprint,'header_line':record['line']}
(HERE/'fc_oam_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'fc_oam_review_sources.json').write_text(json.dumps({'source_sha256':{p.relative_to(REPOS).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [header,compiler,REPOS/'kitaqfc/kitaqfc/Lowerer.cs']},'records':evidence},indent=2),encoding='utf-8')
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print('9 FC OAM contracts bound to current compiler source.')
