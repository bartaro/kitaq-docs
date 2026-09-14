"""Bind individually authored asset contracts to reviewed source records and samples."""
from pathlib import Path
import hashlib,json,re
site=Path(__file__).resolve().parents[2]
out=site/'tools/api_descriptions'
contracts={}
properties={
 'asset_set_table':('as_set',[('bank','as_table_bank'),('table','as_table_arg'),('count','as_count')],'none','as_demo_set'),
 'asset_get':('as_get',[('asset_id','as_id'),('out_desc','as_out')],'as_get_ret','as_demo_get'),
 'asset_load_raw':('as_raw',[('asset_id','as_id'),('dst','as_dst'),('max_len','as_max')],'as_raw_ret','as_demo_raw'),
 'asset_load_tiles':('as_tiles_', [('asset_id','as_id'),('vram_dst','as_vram_')],'as_tiles_ret','as_demo_tiles'),
 'asset_get_bank':('as_bank',[('asset_id','as_id')],'as_bank_ret','as_demo_bank'),
 'asset_get_ptr':('as_ptr',[('asset_id','as_id')],'as_ptr_ret','as_demo_ptr'),
 'asset_get_len':('as_len',[('asset_id','as_id')],'as_len_ret','as_demo_len')}
shared=(site/'samples/asset_example_checks.h').read_text(encoding='utf-8')
def fragment(source,name):
    match=re.search(r'// example:'+re.escape(name)+r':start\s*\n(.*?)\s*// example:'+re.escape(name)+r':end',source,re.S)
    assert match,name
    return '\n'.join(line[4:] if line.startswith('    ') else line for line in match[1].splitlines()).strip()
for platform in ('gb','fc'):
    records={r['name']:r for r in json.loads((site/'reference'/f'{platform}-api.json').read_text(encoding='utf-8'))['records']}
    program=f'samples/api-examples/{platform}/asset_banks.c'
    program_text=(site/program).read_text(encoding='utf-8')
    build='New-Item -ItemType Directory -Force .\\out | Out-Null\n'
    build+=f'.\\kitaq{platform}\\kitaq{platform}.exe .\\kitaq-docs\\samples\\api-examples\\{platform}\\asset_banks.c -I .\\kitaq{platform}\\lib -I .\\kitaq-docs\\samples -o .\\out\\asset_banks.'+('gb' if platform=='gb' else 'nes')
    build+=' --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --cart=mbc5 --romsize=64k' if platform=='gb' else ' --mapper=mmc1 --board=surom512'
    build+=' --no-cache --no-disasm'
    for name in list(properties)+(['__farmemcpy','__far_memcpy'] if platform=='gb' else ['__far_memcpy']):
        record=records[name]
        if name.startswith('__'):
            purpose='as_far';params=[('dst','as_dst'),('bank','as_far_bank'),('src','as_far_src_'+platform),('len','as_far_len')]
            returns='none';demo='as_demo_far';notes=['as_copy_bounds','as_fixed_code']
            if platform=='gb':notes+=['as_gb_bank_state']
            sample=fragment(program_text,name)
        else:
            purpose,params,returns,demo=properties[name]
            purpose+=platform if purpose.endswith('_') else ''
            params=[(arg,key+platform if key.endswith('_') else key) for arg,key in params]
            notes=['as_registration']
            if name=='asset_load_raw':notes+=['as_copy_bounds','as_fixed_code']
            if name=='asset_get':notes+=['as_fixed_code']
            if name.startswith('asset_get_'):notes+=['as_lookup_cost','as_fixed_code']
            if name=='asset_load_tiles':notes+=['as_fixed_code','as_tile_timing']+(['as_gb_bank_state'] if platform=='gb' else ['as_fc_bank_state','as_fc_timing'])
            sample=fragment(program_text if name=='asset_load_tiles' else shared,name)
        fingerprint={k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']}
        contracts[platform+':'+name]={'review':'asset-source-20260915','purpose':[purpose],'args':[(arg,[key]) for arg,key in params],
            'returns':[returns],'notes':notes,'record_sha256':hashlib.sha256(json.dumps(fingerprint,sort_keys=True).encode()).hexdigest(),
            'example':{'program':program,'code':sample,'build':build,'expected':[demo,'as_red_geometry','as_pairs_'+platform,'as_status']}}
assert len(contracts)==17
(out/'asset_contracts.json').write_text(json.dumps(contracts,indent=2),encoding='utf-8')
(out/'asset_modules.json').write_text(json.dumps({'gb:asset':['as_module','as_registration','as_tiles_gb'],
 'fc:asset':['as_module','as_registration','as_tiles_fc','as_fc_timing']},indent=2),encoding='utf-8')
print('17 source-bound contracts and two asset module summaries written.')
