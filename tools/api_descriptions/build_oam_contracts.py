"""Bind the GB OAM intrinsic to its compiler implementation and tested sample."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
source=REPOS/'kitaqgb/kitaqgb/CodeGenerator.cs';text=source.read_text(encoding='utf-8')
start=text.index('            // Copy one 160-byte, page-aligned OAM source')
end=text.index('            // __vram_memcpy',start)
inventory=SITE/'reference/gb-api.json';data=json.loads(inventory.read_text(encoding='utf-8'))
record=next(r for r in data['records'] if r['name']=='__oam_dma')
record['implementation_excerpt']=text[start:end].strip()
fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
contract={'review':'oam-source-20260915','purpose':['oam_purpose'],'args':[['src_ptr',['oam_pointer']]],'returns':['none'],
    'notes':['oam_layout','oam_timing','oam_hram'],'record_sha256':fingerprint,
    'example':{'program':'samples/api-examples/gb/oam_dma.c',
      'code':'// raw_oam is a 160-byte array at address 0xC400.\nm_wait();\n__oam_dma((u16)raw_oam);',
      'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\samples\\api-examples\\gb\\oam_dma.c -I .\\kitaqgb\\lib -I .\\kitaq-docs\\samples -o .\\out\\oam_dma.gb --cgb=cgb --profile=dev --rst-disable --stack-bank=fixed --no-cache --no-disasm',
      'expected':['oam_example']}}
(HERE/'oam_contracts.json').write_text(json.dumps({'gb:__oam_dma':contract},ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'oam_review_sources.json').write_text(json.dumps({'path':source.relative_to(REPOS).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'record_sha256':fingerprint},indent=2),encoding='utf-8')
inventory.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('1 OAM intrinsic contract bound to compiler source.')
