"""Bind the nine immediate GB VRAM transfer intrinsics to source-reviewed descriptions."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
SITE=HERE.parents[1]
records={r['name']:r for r in json.loads((SITE/'reference/gb-api.json').read_text(encoding='utf-8'))['records']}
messages={};contracts={}
aliases=json.loads((HERE/'vram_memory_alias_templates.json').read_text(encoding='utf-8'))
examples=json.loads((HERE/'vram_memory_example_templates.json').read_text(encoding='utf-8'))
for key in ['vm_no_dma','vm_map_alias']:messages[key]=aliases[key]
for key in ['vm_tiles','vm_example_checks']:messages[key]=examples[key]
# Explicit rows, operations and alias targets mirror the inspected compiler dispatch.
entries=[
 ('__vram_memcpy',2,'copy',None,False),
 ('__vram_copy',3,'copy','__vram_memcpy',False),
 ('__vram_copy_hblank',4,'copy','__vram_memcpy',False),
 ('__vram_copy_dma',5,'copy','__vram_memcpy',False),
 ('__vram_memcpy_unsafe',6,'copy',None,True),
 ('__vram_memset',7,'fill',None,False),
 ('__vram_fill',8,'fill','__vram_memset',False),
 ('__fill_tilemap',9,'fill','__vram_memset',False),
 ('__vram_memset_unsafe',10,'fill',None,True)]
program='samples/api-examples/gb/vram_memory_shapes.c'
source=(SITE/program).read_text(encoding='utf-8')
for name,row,operation,target,unsafe in entries:
 purpose=['vm_'+operation]
 if target:
  key='vm_alias_'+name
  messages[key]=[text.format(name=name,target=target) for text in aliases['vm_named_alias']]
  purpose.insert(0,key)
 notes=['vm_unsafe' if unsafe else 'vm_safe']
 if name in ['__vram_copy_hblank','__vram_copy_dma']:notes.insert(0,'vm_no_dma')
 if name=='__fill_tilemap':notes.insert(0,'vm_map_alias')
 args=[['dst',['vm_dst']]]
 args+=[['src',['vm_src']]] if operation=='copy' else [['value',['vq_fill_value']]]
 args+=[['len',['vq_length']]]
 syntax='void '+name+'(u16 dst, '+('const void* src' if operation=='copy' else 'u8 value')+', u16 len);'
 key='vm_example_'+name
 messages[key]=[text.format(name=name,row=row,y=row*8) for text in examples['vm_example_'+operation]]
 snippet=re.search(r'// example:'+name+r':start\n(.*?)\s*// example:'+name+r':end',source,re.S)[1]
 snippet='\n'.join(line[4:] if line.startswith('    ') else line for line in snippet.strip().splitlines())
 contracts['gb:'+name]={'review':'vram-memory-source-20260915','purpose':purpose,'syntax':syntax,'args':args,'returns':['none'],'notes':notes,
  'record_sha256':hashlib.sha256(json.dumps({k:records[name].get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest(),
  'example':{'code':snippet,'program':program,'expected':[key,'vm_tiles','vm_example_checks','vm_cgb_colors'],
  'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\samples\\api-examples\\gb\\vram_memory_shapes.c -I .\\kitaqgb\\lib -I .\\kitaq-docs\\samples -o .\\out\\vram_memory_shapes.gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --no-cache --no-disasm'}}
(HERE/'vram_memory_generated_texts.json').write_text(json.dumps(messages,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'vram_memory_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
print('Nine immediate VRAM transfer contracts written.')
