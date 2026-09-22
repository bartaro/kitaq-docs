"""Bind optical-mask documentation to complete instruction traces and the diagram."""
from pathlib import Path
import hashlib,json,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
REVIEW='rob-source-20260922'

def verified_examples(contracts):
 selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
 if not selected:return {}
 assert set(selected)=={'fc:__rob_flash','fc:__rob_pulse','fc:__rob_send_byte'}
 report=read(SITE/'verification/api-rob/state/results.json')
 assert report['script_sha256']==sha(SITE/'tools/check_rob_primitives.py')
 assert report['compiler_sha256']==sha(REPOS/'kitaqfc/kitaqfc.exe')
 assert report['emulator_sha256']==sha(REPOS/'kurosaki/kurosaki.exe')
 assert report['header_sha256']==sha(REPOS/'kitaqfc/lib/intrinsics.h')
 names={*(f'flash-{n}' for n in [0,1,255]),*(f'pulse-{a}-{b}' for a,b in [(0,0),(0,3),(3,0),(2,4),(4,2),(1,255),(255,1)]),*(f'byte-{n}' for n in [0,255,128,64,32,16,8,4,2,1,85,170])}
 rows=report['records'];assert len(rows)==44
 assert {(r['variant'],r['name']) for r in rows}=={(v,n) for v in ['default','unoptimized'] for n in names}
 for r in rows:
  assert r['passed'] and r['actual']==r['expected'] and r['mask_writes']==r['expected_masks']
  assert all(b-a==1 for a,b in zip(r['write_frames'],r['write_frames'][1:]))
  for key in ['source','rom']:assert sha(SITE/r[key])==r[key+'_sha256']
  if r['name'].startswith('byte-'):
   value=int(r['name'].split('-')[1]);want=[]
   for bit in range(7,-1,-1):want+=([30]*4+[0]*2) if value&(1<<bit) else ([30]*2+[0]*4)
   assert r['actual']==[165,48,0,0] and r['mask_writes']==want
 visual=read(SITE/'verification/api-rob/example/results.json')
 assert visual['script_sha256']==sha(SITE/'tools/check_rob_example.py')
 row=visual['record'];verify_row(row)
 assert row['actual']==[1,5,48,0,165] and row['diagram_pixels']==3072
 for key,c in selected.items():
  source=(SITE/c['example']['program']).read_text(encoding='utf-8')
  assert c['example']['code'] in source
  assert re.search(r'\b'+key.split(':')[1]+r'\s*\(',c['example']['code'])
 return {k:dict(api=k.split(':')[1],kind='rob',runs=[row]) for k in selected}

def overview(text,language):
 import api_contracts as api
 messages,ui,contracts=api.load();proofs=verified_examples(contracts)
 selected={k:contracts[k] for k in proofs};api.attach_verified_images(selected,proofs)
 records={r['name']:r for r in read(SITE/'reference/fc-api.json')['records']};edits=[]
 for name,start,end in api.CardRanges(text).ranges:
  key='fc:'+name
  if key not in selected:continue
  r=records[name];c=selected[key]
  fp=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
  assert fp==c['record_sha256']
  edits.append((start,end,api.render(r,c,language,messages,ui)))
 assert len(edits)==3
 for start,end,content in reversed(edits):text=text[:start]+content+text[end:]
 return text

if __name__=='__main__':
 for lang in ['ja','en']:
  path=(SITE if lang=='ja' else SITE/lang)/'kitaqfc.html'
  path.write_text(overview(path.read_text(encoding='utf-8'),lang),encoding='utf-8')
 print('Three optical-mask API cards verified and rendered in JA/EN.')
