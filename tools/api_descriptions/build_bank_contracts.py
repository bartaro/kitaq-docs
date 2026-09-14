"""Bind 32 source-reviewed bank APIs to authored contracts and executable examples."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1]
templates=json.loads((HERE/'bank_example_templates.json').read_text(encoding='utf-8'))
shared=(SITE/'samples/bank_example_checks.h').read_text(encoding='utf-8')
contracts={};messages={}
def fragment(name,platform):
    match=re.search(r'// example:'+re.escape(name)+r':start\s*\n(.*?)\s*// example:'+re.escape(name)+r':end',shared,re.S)
    assert match,name
    # Resolve only the sample's explicit two-platform preprocessor branch.
    lines=[];active=True;parent=[]
    for line in match[1].splitlines():
        stripped=line.strip()
        if stripped=='#ifdef MANUAL_BANK_FC':parent.append(active);active=active and platform=='fc'
        elif stripped=='#else':active=parent[-1] and platform!='fc'
        elif stripped=='#endif':active=parent.pop()
        elif active:lines.append(line[4:] if line.startswith('    ') else line)
    return '\n'.join(lines).strip()
def demo(kind,name,platform,**values):
    key='bk_demo_'+platform+'_'+name.lstrip('_')
    messages[key]=[text.format(api=name,**values) for text in templates[kind]]
    return key
for platform in ['gb','fc']:
    records={r['name']:r for r in json.loads((SITE/'reference'/(platform+'-api.json')).read_text(encoding='utf-8'))['records']}
    limits='bk_'+platform+'_limits'
    source_arg='as_far_src_gb'
    rows={
      'bank_switch':('bk_switch_'+platform,[('bank','bk_bank_arg')],'none',['bk_fixed_note','bk_shadow_note',limits],'bk_demo_switch'),
      'bank_get_current':('bk_get',[],'bk_record_return',['bk_shadow_note'],'bk_demo_switch'),
      '__bankswitch':('bk_intrinsic_'+platform,[('bank','bk_bank_arg')],'none',['bk_fixed_note','bk_shadow_note',limits],'bk_demo_switch'),
      '__bankof':('bk_bankof',[('symbol','bk_symbol_arg')],'bk_bank_return',[],'bk_demo_bankof'),
      'farptr_make':('bk_make',[('out','bk_out_arg'),('bank','bk_bank_arg'),('ptr','bk_stored_pointer')],'none',[],'bk_demo_make')
    }
    for name,purpose,source,value,word,pointer in [
        ('far_data_read8','bk_read8','payload','D3',False,False),
        ('far_data_read16','bk_read16','payload+1','5C7A',True,False),
        ('farptr_read8','bk_ptr8','pointer.ptr','7A',False,True),
        ('farptr_read16','bk_ptr16','pointer.ptr','5C7A',True,True),
        ('__farpeek8','bk_peek8','payload','D3',False,False),
        ('__farpeek16','bk_peek16','payload+1','5C7A',True,False)]:
        args=[('ptr','bk_value_arg')] if pointer else [('bank','bk_bank_arg'),('addr','as_far_src_fc' if name.startswith('__') and platform=='fc' else source_arg)]
        rows[name]=(purpose,args,'bk_word_return' if word else 'bk_byte_return',
                    ['bk_read_bounds','bk_transfer_context',limits],demo('read',name,platform,source=source,value=value))
    for name,purpose,pointer,count,values in [
        ('far_data_read','bk_read_copy',False,4,'D3 7A 5C 96'),('farptr_read','bk_ptr_copy',True,3,'7A 5C 96')]:
        args=([('ptr','bk_value_arg')] if pointer else [('bank','bk_bank_arg'),('addr',source_arg)])+[('dst','as_dst'),('len','as_far_len')]
        rows[name]=(purpose,args,'none',['as_copy_bounds','bk_transfer_context',limits],demo('copy',name,platform,count=count,bytes=values))
    for name,purpose,count,pointer in [
        ('far_call','bk_call_'+platform,1,platform=='gb'),('__farcall','bk_named_'+platform,2,False)]+([('__farcall_ptr','bk_pointer_call',3,True)] if platform=='gb' else []):
        rows[name]=(purpose,[('bank','bk_bank_arg'),('func','bk_callback_pointer_arg' if pointer else 'bk_callback_name_arg')],
                    'none' if pointer else 'bk_call_return',['bk_call_context',limits],demo('call',name,platform,count=count))
    if platform=='fc':
        rows['__prg_bank_set']=('bk_prg_alias',[('bank','bk_bank_arg')],'none',['bk_fixed_note','bk_shadow_note',limits],'bk_demo_switch')
    assert len(rows)==16
    program='samples/api-examples/'+platform+'/banked_data_calls.c'
    build='New-Item -ItemType Directory -Force .\\out | Out-Null\n'
    build+='.\\kitaq'+platform+'\\kitaq'+platform+'.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaq'+platform+'\\lib -I .\\kitaq-docs\\samples -o .\\out\\banked_data_calls.'
    build+='gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --cart=mbc5 --romsize=64k' if platform=='gb' else 'nes --mapper=mmc3 --nes-chr=.\\kitaq-docs\\samples\\font.chr'
    build+=' --no-cache --no-disasm'
    for name,(purpose,args,returns,notes,example_text) in rows.items():
        record=records[name]
        fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
        contract={'review':'bank-source-20260915','purpose':[purpose],'args':[(arg,[key]) for arg,key in args],
                  'returns':[returns],'notes':notes,'record_sha256':fingerprint,
                  'example':{'program':program,'code':fragment(name,platform),'build':build,
                             'expected':[example_text,'bk_demo_program','bk_demo_calls_'+platform]}}
        if name=='__bankof':contract['syntax']='u8 bank = __bankof(symbol);'
        if name=='__farcall':contract['syntax']='__farcall(bank, function_name);'
        contracts[platform+':'+name]=contract
assert len(contracts)==32
(HERE/'bank_generated_texts.json').write_text(json.dumps(messages,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'bank_contracts.json').write_text(json.dumps(contracts,indent=2),encoding='utf-8')
print('32 exact-name bank API contracts and localized example explanations generated.')
