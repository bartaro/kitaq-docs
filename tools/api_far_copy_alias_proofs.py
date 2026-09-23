"""Require actual FC alias calls, byte sentinels and colored transfer images."""
from pathlib import Path
import hashlib,json
from check_far_copy_alias import SOURCE,SUPPORT,LIBRARIES,VARIANTS
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
REVIEW='far-copy-alias-source-20260923'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def verified_examples(contracts):
 selected={k:c for k,c in contracts.items() if c['review']==REVIEW}
 if not selected:return {}
 assert set(selected)=={'fc:__farmemcpy'}
 report=json.loads((SITE/'verification/api-far-copy-alias/results.json').read_text(encoding='utf-8'))
 assert report['passed'] and len(report['records'])==4
 assert {r['variant'] for r in report['records']}=={n for n,f in VARIANTS}
 assert set(report['support_sha256'])=={SOURCE,*SUPPORT}
 assert set(report['library_sha256'])==set(LIBRARIES)
 for n,h in report['support_sha256'].items():assert sha(SITE/n)==h
 for n,h in report['library_sha256'].items():assert sha(REPOS/'kitaqfc/lib'/n)==h
 for p,key in [(REPOS/'kitaqfc/kitaqfc.exe','compiler_sha256'),
               (REPOS/'kurosaki/kurosaki.exe','emulator_sha256'),
               (REPOS/'kitaqfc/kitaqfc/CodeGenerator.cs','compiler_source_sha256'),
               (SITE/'tools/check_far_copy_alias.py','checker_sha256')]:
  assert sha(p)==report[key],str(p)
 ex=selected['fc:__farmemcpy']['example']
 assert ex['program']==SOURCE and ex['code'].count('__farmemcpy(')==2
 normalize=lambda s:'\n'.join(line.strip() for line in s.strip().splitlines())
 assert normalize(ex['code']) in normalize((SITE/SOURCE).read_text(encoding='utf-8'))
 for r in report['records']:
  assert r['passed'] and r['frames']==300 and r['platform']=='fc' and r['mode']=='surom512'
  assert r['label_pixel_mismatches']==r['geometry_pixel_mismatches']==r['geometry_color_mismatches']==0
  assert r['geometry_pixels_checked']==832 and r['source']==SOURCE
  for k in ['source','rom','image']:assert sha(SITE/r[k])==r[k+'_sha256']
 return {'fc:__farmemcpy':dict(api='__farmemcpy',kind='far-copy-alias',runs=[r for r in report['records'] if r['variant']=='default'])}

def ensure_card(text):
 """Insert into an existing edition; a fresh generation uses the inventory."""
 if 'id="api-__farmemcpy"' in text:return text
 from api_contracts import CardRanges
 matches=[(start,end) for name,start,end in CardRanges(text).ranges if name=='__far_memcpy']
 assert len(matches)==1
 pos=matches[0][1]
 card='<details class="api searchable" id="api-__farmemcpy"><summary><code>__farmemcpy</code></summary></details>'
 return text[:pos]+card+text[pos:]

if __name__=='__main__':
 from api_contracts import load
 assert set(verified_examples(load()[2]))=={'fc:__farmemcpy'}
 print('FC far-copy alias: four runtime variants and exact source/image bindings pass.')
