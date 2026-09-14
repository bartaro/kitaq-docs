"""Bind all ten FC intrinsic queue operations to their inspected implementation."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
SITE=HERE.parents[1]
records={r['name']:r for r in json.loads((SITE/'reference/fc-api.json').read_text(encoding='utf-8'))['records']}
program='samples/api-examples/fc/vramq_intrinsics.c'
source=(SITE/program).read_text(encoding='utf-8')
purposes={'__vramq_clear':'qi_clear','__vramq_put':'qi_put','__vramq_copy':'qi_copy',
 '__vramq_fill':'qi_fill','__vramq_commit':'qi_commit','__vramq_exec':'qi_exec',
 '__vramq_len':'vq_used','__vramq_capacity':'vq_capacity',
 '__vramq_overflow':'vram_get_overflowed','__vramq_clear_overflow':'qi_clear_overflow'}
contracts={}
for name,purpose in purposes.items():
 args=[];notes=['vq_units_fc','qi_surface','vq_serialize'];returns=['none']
 if name in ['__vramq_put','__vramq_copy','__vramq_fill']:
  args=[['ppu_addr',['vq_dst_fc']]]
  args += [['src',['vq_source']]] if name=='__vramq_copy' else [['value',['vq_fill_value']]]
  if name!='__vramq_put':args += [['len',['qi_length']]]
  notes.insert(0,'qi_append')
 if name in ['__vramq_len','__vramq_capacity']:returns=['vq_count_result']
 if name=='__vramq_overflow':returns=['vq_overflow_result']
 if name=='__vramq_exec':notes.insert(0,'vq_dst_fc')
 snippet=re.search(r'// example:'+name+r':start\n(.*?)\s*// example:'+name+r':end',source,re.S)[1]
 snippet='\n'.join(line[4:] if line.startswith('    ') else line for line in snippet.strip().splitlines())
 contracts['fc:'+name]={'review':'vramq-source-20260915','purpose':[purpose],'args':args,'returns':returns,'notes':notes,
  'record_sha256':hashlib.sha256(json.dumps({k:records[name].get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest(),
  'example':{'code':snippet,'program':program,'expected':['qi_example_counts','qi_example_shapes','qi_example_zero'],
  'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\samples\\api-examples\\fc\\vramq_intrinsics.c -I .\\kitaqfc\\lib -I .\\kitaq-docs\\samples -o .\\out\\vramq_intrinsics.nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\api-examples\\fc\\vram_shapes.chr --no-cache --no-disasm'}}
(HERE/'vramq_contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')
print('Ten FC intrinsic queue contracts written.')
