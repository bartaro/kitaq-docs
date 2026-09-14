"""Bind explicitly inspected CGB APIs to authored prose and executable examples."""
from pathlib import Path
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
SITE=HERE.parents[1]
templates=json.loads((HERE/'cgb_palette_templates.json').read_text(encoding='utf-8'))
records={r['name']:r for r in json.loads((SITE/'reference/gb-api.json').read_text(encoding='utf-8'))['records']}
stores={
    'bg':['background/window','背景・ウィンドウ用','배경·윈도우','背景/窗口','背景/視窗','fondo/ventana','fundo/janela','fond/fenêtre','Hintergrund/Fenster'],
    'obj':['sprite (OBJ)','スプライト（OBJ）用','스프라이트(OBJ)','精灵（OBJ）','精靈（OBJ）','sprites (OBJ)','sprites (OBJ)','sprites (OBJ)','Sprites (OBJ)']
}
messages={}
contracts={}
program='samples/api-examples/gb/cgb_palette_attributes.c'
source=(SITE/program).read_text(encoding='utf-8')
build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\samples\\api-examples\\gb\\cgb_palette_attributes.c -I .\\kitaqgb\\lib -I .\\kitaq-docs\\samples -o .\\out\\cgb_palette_attributes.gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --no-cache --no-disasm'

def expand(key,template,store,**fields):
    messages[key]=[text.format(store=stores[store][index],**fields) for index,text in enumerate(templates[template])]
    return key

def bind(name,purpose,args=(),returns=('none',),notes=()):
    record=records[name]
    match=re.search(r'// example:'+re.escape(name)+r':start\n(.*?)\s*// example:'+re.escape(name)+r':end',source,re.S)
    assert match,name
    snippet='\n'.join(line[4:] if line.startswith('    ') else line for line in match[1].strip().splitlines())
    contracts['gb:'+name]={
        'review':'cgb-palette-source-20260915','purpose':[purpose],
        'args':[[argument,list(keys)] for argument,keys in args],
        'returns':list(returns),'notes':list(notes),
        'record_sha256':hashlib.sha256(json.dumps({key:record.get(key) for key in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest(),
        'example':{'program':program,'code':snippet,'build':build,'expected':['cp_example_palettes','cp_example_attributes','cp_example_checks']}
    }

for store in ['bg','obj']:
    for suffix,template in [('color','cp_single'),('rgb','cp_components'),('colors','cp_range'),('palette','cp_palette'),('colors_raw','cp_raw')]:
        name='cgb_'+store+'_'+suffix
        purpose=expand('cp_purpose_'+name,template,store)
        args=[('palette_index',['cp_palette_index'])]
        if suffix in ['color','rgb']:args+=[('color_index',['cp_color_index'])]
        if suffix=='color':args+=[('rgb15',['cp_word'])]
        if suffix=='rgb':args+=[('r5, g5, b5',['cp_components_arg'])]
        if suffix=='colors':args+=[('start_color_index',['cp_color_index'])]
        if suffix=='colors_raw':args=[('start_color_slot',['cp_slot'])]
        if suffix in ['colors','colors_raw','palette']:args+=[('colors',['cp_array'])]
        if suffix in ['colors','colors_raw']:args+=[('color_count',['cp_count'])]
        bind(name,purpose,args,notes=['cp_guard','cp_palette_state'])

# Exact register/address bindings, including both public names of each register.
for store,register,address,kind,pair in [
    ('bg','BCPS/BGPI','$FF68','index',('bcps','bgpi')),
    ('bg','BCPD/BGPD','$FF69','data',('bcpd','bgpd')),
    ('obj','OCPS/OBPI','$FF6A','index',('ocps','obpi')),
    ('obj','OCPD/OBPD','$FF6B','data',('ocpd','obpd'))
]:
    for short,alias in [pair,pair[::-1]]:
        name='__cgb_safe_set_'+short
        purpose=expand('cp_purpose_'+name,'cp_'+kind+'_register',store,register=register,address=address,alias='__cgb_safe_set_'+alias)
        bind(name,purpose,[('value',['cp_index_value' if kind=='index' else 'cp_byte_value'])],notes=['cp_guard'])

bind('__cgb_is_cgb','cp_mode',returns=['cp_bool_result'])
bind('__cgb_safe_set_vbk','cp_vbk',[('value',['cp_vbk'])],notes=['cp_guard'])
for name in ['CGB_RGB15','cgb_rgb15']:
    bind(name,'cp_rgb',[('r5, g5, b5',['cp_components_arg'])],returns=['cp_rgb_result'])
for name,purpose,args in [
    ('KQ_CGB_ATTR_PAL','ca_pal',[('n',['cp_palette_index'])]),
    ('KQ_CGB_ATTR_BANK','ca_bank',[('bank',['ca_boolean'])]),
    ('KQ_CGB_ATTR_XFLIP_IF','ca_x',[('enabled',['ca_boolean'])]),
    ('KQ_CGB_ATTR_YFLIP_IF','ca_y',[('enabled',['ca_boolean'])]),
    ('KQ_CGB_ATTR_PRIORITY_IF','ca_priority',[('enabled',['ca_boolean'])]),
    ('KQ_CGB_ATTR','ca_combined',[('palette',['cp_palette_index']),('bank, xflip, yflip, priority',['ca_boolean'])])
]:
    notes=['ca_pure']
    if name=='KQ_CGB_ATTR':notes+=['ca_bank','ca_x','ca_y','ca_priority']
    bind(name,purpose,args,returns=['ca_result'],notes=notes)
assert len(contracts)==28,len(contracts)
(HERE/'cgb_palette_expanded_texts.json').write_text(json.dumps(messages,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'cgb_palette_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'cgb-palette_modules.json').write_text(json.dumps({'gb:cgb_palette':['cp_module','cp_guard','cp_palette_state']},indent=2),encoding='utf-8')
print('28 CGB palette/attribute contracts and one module overview written.')
