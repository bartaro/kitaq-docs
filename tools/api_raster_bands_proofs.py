"""Require current table/state and full-screen evidence for all sixteen band APIs."""
from pathlib import Path
import hashlib,json,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
REVIEW='raster-bands-source-20260922';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def verified_examples(contracts):
 selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
 if not selected:return {}
 assert len(selected)==16
 folder=SITE/'verification/api-raster-bands';state=read(folder/'state/results.json')
 assert state['script_sha256']==sha(SITE/'tools/check_raster_bands_state.py')
 rows=state['records'];assert len(rows)==6 and {(r['variant'],r['mode']) for r in rows}=={(v,m) for v in ['default','unoptimized','stack'] for m in ['dmg','cgb']}
 for row in rows:
  assert row['passed'] and row['actual']==row['expected'] and len(row['checks'])==53
  assert row['table']==row['expected_table'] and len(row['table'])==48
  assert sha(SITE/row['source'])==row['source_sha256'] and sha(SITE/row['rom'])==row['rom_sha256']
  assert sha(REPOS/'kitaqgb/kitaqgb.exe')==row['compiler_sha256'] and sha(REPOS/'kokura/kokura-cli.exe')==row['emulator_sha256']
  for p,digest in row['input_sha256'].items():assert sha((REPOS if p.startswith('kitaqgb/') else SITE)/p)==digest,p
 visual=read(folder/'results.json');assert visual['script_sha256']==sha(SITE/'tools/check_raster_bands_examples.py')
 spec=SITE/'tools/api_descriptions/raster_bands_examples.json';assert visual['spec_sha256']==sha(spec)
 expected={(s['group'],m) for s in read(spec) for m in s['modes']};runs=visual['records']
 assert len(runs)==17 and {(r['group'],r['mode']) for r in runs}==expected
 for row in runs:verify_row(row);assert row['actual']==row['expected'] and row['pixel_mismatches']==0
 proofs={}
 for key,contract in selected.items():
  source=(SITE/contract['example']['program']).read_text(encoding='utf-8');snippet=contract['example']['code']
  assert snippet in source and re.search(r'\b'+key.split(':')[1]+r'\s*\(',snippet)
  found=[r for r in runs if r['source']==contract['example']['program']];assert found
  proofs[key]=dict(api=key.split(':')[1],kind='raster-bands',runs=found)
 return proofs

def overview(text,language):
 import api_contracts as api
 from api_raster_wave_proofs import verified_examples as wave_proofs
 messages,ui,contracts=api.load();proofs={**verified_examples(contracts),**wave_proofs(contracts)}
 selected={k:contracts[k] for k in proofs};api.attach_verified_images(selected,proofs)
 records={r['name']:r for r in read(SITE/'reference/gb-api.json')['records']};edits=[];found=set()
 for name,start,end in api.CardRanges(text).ranges:
  key='gb:'+name
  if key not in selected:continue
  record=records[name];contract=selected[key]
  fp=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest();assert fp==contract['record_sha256']
  edits.append((start,end,api.render(record,contract,language,messages,ui)));found.add(key)
 for start,end,content in reversed(edits):text=text[:start]+content+text[end:]
 match=re.search(r'<h3\b[^>]*id="module-raster"[^>]*>.*?</h3>',text,re.S);assert match
 anchor=match.group(0)
 for key in selected.keys()-found:text=text.replace(anchor,anchor+api.render(records[key.split(':')[1]],selected[key],language,messages,ui),1)
 text=re.sub(r'<!-- raster-bands-module:start -->.*?<!-- raster-bands-module:end -->','',text,flags=re.S)
 index=api.ORDER.index(language);keys=read(SITE/'tools/api_descriptions/raster_bands_modules.json')['gb:raster']
 block='<!-- raster-bands-module:start -->'+''.join('<p>'+api.inline(messages[k][index])+'</p>' for k in keys)+'<!-- raster-bands-module:end -->'
 text=text.replace(anchor,anchor+block,1)
 return api.refresh_complete_headers(text,'gb')

if __name__=='__main__':
 for language in ['ja','en']:
  p=(SITE if language=='ja' else SITE/'en')/'gb-library.html';p.write_text(overview(p.read_text(encoding='utf-8'),language),encoding='utf-8')
 print('Sixteen band cards and six wave cards verified and rendered in JA/EN.')
