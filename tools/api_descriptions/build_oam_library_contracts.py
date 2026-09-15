"""Bind OAM macros, C helpers and rotating-pool drawing to distinct tested examples."""
from pathlib import Path
import hashlib, json, re, sys
HERE=Path(__file__).resolve().parent; SITE=HERE.parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
sources=['nes_game.h','runtime.h','runtime.c','metasprite.h','metasprite.c','oam_fair.h','oam_fair_impl.h']
definitions={name:{r['name']:r for r in catalog.definitions(REPOS/'kitaqfc/lib'/name)} for name in sources}
for filename in sources:
    text=(REPOS/'kitaqfc/lib'/filename).read_text(encoding='utf-8')
    for match in re.finditer(r'(?m)^#define[ \t]+(\w+)\(([^\n)]*)\)[ \t]*([^\n]*(?:\\\n[^\n]*)*)',text):
        name,args,body=match.groups()
        definitions[filename][name]=dict(name=name,ret='macro',args=args,signature=match[0],path='kitaqfc/lib/'+filename,line=text.count('\n',0,match.start())+1,comment='',body='',kind='macro')
inventory=SITE/'reference/fc-api.json';data=json.loads(inventory.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}

def example(program,marker,expected):
    program='samples/api-examples/fc/'+program
    text=(SITE/'samples/fc_oam_alias_example.h').read_text(encoding='utf-8')+'\n'+(SITE/program).read_text(encoding='utf-8')
    match=re.search(r'// example:'+re.escape(marker)+r':start\s*\n(.*?)\s*// example:'+re.escape(marker)+r':end',text,re.S)
    assert match,marker
    build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaqfc\\lib -I .\\kitaq-docs\\samples --nes-chr=.\\kitaq-docs\\samples\\sprite_example.chr -o .\\out\\'+Path(program).stem+'.nes --no-cache --no-disasm'
    return dict(program=program,code='\n'.join(line.strip() for line in match[1].splitlines()),build=build,expected=expected)

rows={
 'nes_oam_clear':(['ol_macro','fo_clear'],[],'none',['fo_shadow']),
 'nes_oam_dma':(['ol_dma_dual'],[('page (C)','fo_page_arg')],'none',['ol_headers','ol_c_setup','ol_dma_timing']),
 'nes_sprite_set':(['ol_macro','fo_set'],[('i','fo_index'),('x','sp_x'),('y','sp_y_fc'),('t','sp_tile_arg'),('a','fo_attr_arg')],'none',['fo_shadow']),
 'nes_sprite_move':(['ol_macro','fo_move'],[('i','fo_index'),('x','sp_x'),('y','sp_y_fc')],'none',['fo_shadow']),
 'nes_sprite_hide':(['ol_macro','fo_hide'],[('i','fo_index')],'none',['fo_shadow']),
 'nes_metasprite_draw':(['ol_meta_dual','fo_meta'],[('oam_index / i','fo_index'),('base_x / x','sp_x'),('base_y / y','sp_y_fc'),('metasprite / data','fo_stream_arg')],'fo_meta_return',['ol_headers','ol_c_setup','fo_shadow','fo_meta_limit']),
 'nes_metasprite_hide_from':(['ol_hide_range'],[('oam_index','fo_index'),('sprite_count','ol_count')],'none',['ol_c_setup','fo_shadow']),
 'OAM_FairDraw':(['ol_fair'],[],'ol_fair_returns',['ol_fair_inputs','ol_fair_cursor','ol_fair_setup'])}
contracts={};evidence={}
for name,(purpose,args,returns,notes) in rows.items():
    record=records[name]
    header='oam_fair.h' if name=='OAM_FairDraw' else 'metasprite.h' if name.startswith('nes_metasprite') else 'nes_game.h'
    primary=definitions[header][name]
    for field in ['ret','args','signature','path','line','comment','body']:record[field]=primary[field]
    impl='oam_fair_impl.h' if name=='OAM_FairDraw' else 'metasprite.c' if name.startswith('nes_metasprite') else 'runtime.c' if name=='nes_oam_dma' else None
    record['definition']=definitions[impl][name] if impl else None
    record['implementation_excerpt']=record['definition']['body'] if impl else primary['signature']
    if name=='nes_metasprite_draw':record['implementation_excerpt']+='\n'+definitions['nes_game.h'][name]['signature']
    fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
    if name=='OAM_FairDraw':sample=example('oam_fair.c',name,['ol_fair_example','ol_color_proof'])
    elif name.startswith('nes_metasprite'):
        sample=example('oam_c_helpers.c','c_'+name if name.endswith('_draw') else name,['ol_c_example','ol_color_proof'])
        if name.endswith('_draw'):sample['additional']=[example('oam_aliases.c',name,['fo_scene','ol_alias_example'])]
    else:
        sample=example('oam_aliases.c',name,['fo_scene','ol_alias_example'])
        if name=='nes_oam_dma':sample['additional']=[example('oam_c_helpers.c','c_'+name,['ol_c_example','ol_color_proof'])]
    contract=dict(review='oam-library-source-20260915',purpose=purpose,args=[[arg,[message]] for arg,message in args],returns=[returns],notes=notes,record_sha256=fingerprint,example=sample)
    if name=='nes_oam_dma':contract['syntax']=primary['signature']+'\n\n// C function declared in runtime.h:\n'+definitions['runtime.h'][name]['signature']
    if name=='nes_metasprite_draw':contract['syntax']=primary['signature']+'\n\n// Macro from nes_game.h:\n'+definitions['nes_game.h'][name]['signature']
    contracts['fc:'+name]=contract;evidence[name]=dict(record_sha256=fingerprint,header=header,implementation=impl)
(HERE/'oam_library_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'oam_library_review_sources.json').write_text(json.dumps(dict(source_sha256={name:hashlib.sha256((REPOS/'kitaqfc/lib'/name).read_bytes()).hexdigest() for name in sources},records=evidence),indent=2),encoding='utf-8')
(HERE/'oam-library_modules.json').write_text(json.dumps({'fc:nes_game':['ol_macro','ol_headers'],'fc:metasprite':['ol_meta_dual','ol_c_setup'],'fc:oam_fair':['ol_fair','ol_fair_setup']},indent=2),encoding='utf-8')
inventory.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('8 OAM library contracts bound to source; both forms of two shared names included.')
