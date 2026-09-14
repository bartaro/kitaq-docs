"""Bind individually reviewed input operations to their authored prose and replay examples."""
import hashlib
import json
from pathlib import Path
import re

SITE=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
contracts={}
records={p:{r['name']:r for r in json.loads((SITE/'reference'/(p+'-api.json')).read_text(encoding='utf-8'))['records']} for p in ['gb','fc']}

def add(platform,name,purpose,args,returns,notes,program,expected,syntax=None):
    relative='samples/api-examples/'+platform+'/'+program+'.c'
    source=(SITE/relative).read_text(encoding='utf-8')
    match=re.search(r'// example:'+re.escape(name)+r':start\n(.*?)\s*// example:'+re.escape(name)+r':end',source,re.S)
    if not match:raise ValueError('Missing sample fragment: '+platform+':'+name)
    snippet=re.sub(r'^\s*// example:.*\n','',match[1],flags=re.M)
    snippet='\n'.join(line[4:] if line.startswith('    ') else line for line in snippet.strip('\n').splitlines())
    root='kitaq'+platform
    libraries=['input'] if program=='input_edges' else ['pad','input_repeat'] if program=='pad_repeat' else []
    build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\'+root+'\\'+root+'.exe '
    build+=''.join('.\\'+root+'\\lib\\'+lib+'.c ' for lib in libraries)
    build+='.\\kitaq-docs\\'+relative.replace('/','\\')+' -I .\\'+root+'\\lib -I .\\kitaq-docs\\samples -o .\\out\\'+program
    build+=('.gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb' if platform=='gb' else '.nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\font.chr')+' --no-disasm --no-cache'
    record=records[platform][name]
    contract={'review':'input-source-20260915','purpose':purpose,'args':args,'returns':returns,'notes':notes,
              'record_sha256':hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest(),
              'example':{'code':snippet,'program':relative,'build':build,'expected':[expected]}}
    if syntax:contract['syntax']=syntax
    contracts[platform+':'+name]=contract

for platform in ['gb','fc']:
    for name in ['input_init','input_update','input_down','input_pressed','input_released','input_repeat','input_current','input_previous']:
        purpose=[{'input_init':'input_init_detail','input_update':'input_update_'+platform}.get(name,name)]
        args=[['mask',['input_mask_argument']]] if name in ['input_down','input_pressed','input_released','input_repeat'] else []
        returns=['none'] if name in ['input_init','input_update'] else ['input_boolean_result'] if args else ['input_mask_result']
        notes=['input_logical_layout']
        if name not in ['input_init','input_update']:notes+=['input_cached_state']
        if name in ['input_init','input_update','input_repeat']:notes+=['input_repeat_timing']
        if name=='input_update' and platform=='fc':notes+=['pad_safe_retry']
        add(platform,name,purpose,args,returns,notes,'input_edges','input_edges_example')

for name,purpose,returns,notes in [
    ('__readpad','gb_pad_read','input_mask_result',['input_logical_layout','pad_snapshot_note']),
    ('__readpaddir','gb_pad_dir','pad_nibble_result',['pad_snapshot_note']),
    ('__readpadbtn','gb_pad_btn','pad_nibble_result',['pad_snapshot_note']),
    ('__readpadex','gb_pad_ex','gb_pad_ex_result',['input_logical_layout'])]:
    args=[['prev_keys',['gb_pad_previous_arg']]] if name=='__readpadex' else []
    syntax='u16 __readpadex(u8 prev_keys);' if args else 'u8 '+name+'();'
    add('gb',name,[purpose],args,[returns],notes,'input_raw','gb_raw_example',syntax)

# Only the explicitly reviewed D0 port matrix shares prose templates.
templates=json.loads((HERE/'input_port_templates.json').read_text(encoding='utf-8'))
messages={}
for port,address in [(1,'$4016'),(2,'$4017')]:
    for name,template in [('__pad_read'+str(port),'pad_read'),('__pad_read'+str(port)+'_safe','pad_read_safe'),('nes_pad'+str(port),'pad_alias')]:
        key='input_port_'+name
        messages[key]=[text.format(port=port,address=address) for text in templates[template]]
        notes=['pad_raw_layout','pad_snapshot_note']
        if template!='pad_read':notes+=['pad_safe_retry']
        add('fc',name,[key],[],['pad_raw_result'],notes,'input_raw','fc_raw_example')
for name,purpose,result in [('__pad_buttons','pad_buttons_purpose','pad_nibble_result'),('__pad_dirs','pad_dirs_purpose','pad_dirs_result')]:
    add('fc',name,[purpose],[['pad',['pad_snapshot_argument']]],[result],['pad_raw_layout'],'input_raw','fc_raw_example')

add('fc','nes_pad_poll',['pad_poll_purpose'],[],['none'],['pad_raw_layout','pad_poll_state'],'pad_repeat','fc_repeat_example')
add('fc','nes_pad_repeat_config',['pad_repeat_config_purpose'],[['delay',['pad_repeat_delay_arg']],['interval',['pad_repeat_interval_arg']]],['none'],['pad_raw_layout'],'pad_repeat','fc_repeat_example')
add('fc','nes_pad_repeat_step',['pad_repeat_step_purpose'],[],['none'],['pad_raw_layout','pad_poll_state'],'pad_repeat','fc_repeat_example')
for name,purpose in [('nes_pad_trigger','nes_trigger_purpose'),('nes_pad_repeat','nes_repeat_purpose'),('nes_pad_release','nes_release_purpose'),('nes_pad_held','nes_held_purpose')]:
    add('fc',name,[purpose],[['mask',['pad_raw_mask_arg']]],['pad_masked_result'],['pad_raw_layout','pad_poll_state'],'pad_repeat','fc_repeat_example')

(HERE/'input_port_texts.json').write_text(json.dumps(messages,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'input_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
modules={'gb:input':['input_module_intro','input_logical_layout','input_repeat_timing'],
         'fc:input':['input_module_intro','input_update_fc','input_logical_layout','input_repeat_timing'],
         'fc:pad':['pad_module_intro','pad_raw_layout','pad_poll_state'],
         'fc:input_repeat':['input_repeat_module_intro','pad_repeat_delay_arg','pad_repeat_interval_arg']}
(HERE/'input_modules.json').write_text(json.dumps(modules,indent=2),encoding='utf-8')
print(str(len(contracts))+' reviewed input contracts and four module summaries written.')
