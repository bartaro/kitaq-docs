"""Bind the eight DMA/WRAM intrinsics to inspected behavior and verified programs."""
from pathlib import Path
import hashlib,json,re

HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1]
records={row['name']:row for row in json.loads((SITE/'reference/gb-api.json').read_text(encoding='utf-8'))['records']}
contracts={}
bindings=[('__cgb_safe_set_hdma'+str(i),'dw_hdma'+str(i),'cgb_dma_shapes','cgb','void','value') for i in range(1,6)]
bindings += [('__cgb_safe_set_svbk','dw_svbk_raw','cgb_wram_banks','cgb_only','void','value'),
             ('__svbk_get','dw_svbk_get','cgb_wram_banks','cgb_only','u8',''),
             ('__svbk_set','dw_svbk_set','cgb_wram_banks','cgb_only','u8','bank')]
for name,purpose,program,target,ret,arg in bindings:
    path='samples/api-examples/gb/'+program+'.c';source=(SITE/path).read_text(encoding='utf-8')
    match=re.search(r'// example:'+re.escape(name)+r':start\n(.*?)\s*// example:'+re.escape(name)+r':end',source,re.S)
    assert match,name
    snippet='\n'.join(line[4:] if line.startswith('    ') else line for line in match[1].strip().splitlines())
    dma=program=='cgb_dma_shapes'
    notes=['dw_guard','dw_transfer','dw_timing','dw_status','dw_vs_copy'] if dma else ['dw_bank_live']
    if name=='__cgb_safe_set_svbk':notes.insert(0,'dw_guard')
    if name in ['__svbk_get','__svbk_set']:notes.insert(0,'dw_only')
    returns=['dw_bank_result'] if name=='__svbk_get' else ['dw_previous_result'] if name=='__svbk_set' else ['none']
    record=records[name]
    contracts['gb:'+name]={'review':'cgb-dma-wram-source-20260915','purpose':[purpose],
        'syntax':ret+' '+name+'('+('u8 '+arg if arg else '')+');',
        'args':[[arg,['dw_bank_arg' if arg=='bank' else 'dw_byte']]] if arg else [],
        'returns':returns,'notes':notes,
        'record_sha256':hashlib.sha256(json.dumps({key:record.get(key) for key in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest(),
        'example':{'program':path,'code':snippet,'expected':['dw_dma_example','dw_cancel_example'] if dma else ['dw_wram_example'],
        'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\samples\\api-examples\\gb\\'+program+'.c -I .\\kitaqgb\\lib -I .\\kitaq-docs\\samples -o .\\out\\'+program+'.gb --profile=dev --rst-disable --stack-bank=fixed --cgb='+target+' --no-cache --no-disasm'}}
assert len(contracts)==8
(HERE/'cgb_dma_wram_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
print('Eight CGB DMA/WRAM contracts written.')
