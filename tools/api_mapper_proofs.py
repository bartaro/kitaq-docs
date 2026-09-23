"""Bind mapper lessons to actual PPU reads, IRQ delivery and captured screens."""
from pathlib import Path
import hashlib,json,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
REVIEW='mapper-source-20260922'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def write_page(path,text):
 # Retain existing line endings so inserting one section does not rewrite a book.
 newline='\r\n' if b'\r\n' in path.read_bytes() else '\n'
 path.write_text(text,encoding='utf-8',newline=newline)

def verified_examples(contracts):
 selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
 if not selected:return {}
 assert len(selected)==14
 review=read(SITE/'tools/api_descriptions/mapper_review_sources.json')
 for path,digest in review['source_sha256'].items():assert sha(REPOS/path)==digest,path
 state=read(SITE/'verification/api-mapper/state/results.json')
 assert state['script_sha256']==sha(SITE/'tools/check_mapper_state.py')
 assert state['compiler_sha256']==sha(REPOS/'kitaqfc/kitaqfc.exe')
 assert state['emulator_sha256']==sha(REPOS/'kurosaki/kurosaki.exe')
 assert state['chr_sha256']==sha(SITE/'verification/api-mapper/state/bank-markers.chr')
 for name,digest in state['header_sha256'].items():assert sha(REPOS/'kitaqfc/lib'/name)==digest
 rows=state['records'];assert len(rows)==48
 assert len({(r['name'],r['variant']) for r in rows})==48
 assert {r['variant'] for r in rows}=={'default','unoptimized'}
 for r in rows:
  assert r['passed'] and r['actual']==r['expected'] and r['done']==165
  for key in ['source','rom']:assert sha(SITE/r[key])==r[key+'_sha256']
  if r['name'].startswith('irq-'):assert r['trace_matches'] and r['trace_exit']==0
 visual=read(SITE/'verification/api-mapper/example/results.json')
 assert visual['script_sha256']==sha(SITE/'tools/check_mapper_examples.py')
 rows=visual['records'];assert len(rows)==14
 expected={('controls','mmc3'),('chr-cnrom','cnrom')}|{('mirroring',m) for m in ['mmc1','mmc3','mmc5','axrom','fme7']}
 assert {(r['family'],r['mode']) for r in rows}=={(f,m+'-'+v) for f,m in expected for v in ['default','unoptimized']}
 for r in rows:verify_row(r);assert r['done']==165
 result={}
 for key,c in selected.items():
  examples=[c['example']]+c['example'].get('additional',[])
  for ex in examples:assert ex['code'] in (SITE/ex['program']).read_text(encoding='utf-8')
  assert any(re.search(r'\b'+key.split(':')[1]+r'\s*\(',ex['code']) for ex in examples)
  programs={e['program'] for e in examples}
  # All default builds are shown; the identical -O0 observations remain private.
  runs=[r for r in rows if r['source'] in programs and r['mode'].endswith('-default')]
  assert len(runs)==(5 if key=='fc:__mirroring_set' else 2 if key.startswith('fc:__chr_bank_set') else 1)
  result[key]=dict(api=key.split(':')[1],kind='mapper',runs=runs)
 return result

def overview(text,language):
 import api_contracts as api
 messages,ui,contracts=api.load();proofs=verified_examples(contracts)
 selected={k:contracts[k] for k in proofs};api.attach_verified_images(selected,proofs)
 records={r['name']:r for r in read(SITE/'reference/fc-api.json')['records']}
 for name,start,end in reversed(api.CardRanges(text).ranges):
  key='fc:'+name
  if key not in selected:continue
  r=records[name];c=selected[key]
  fp=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
  assert fp==c['record_sha256']
  text=text[:start]+api.render(r,c,language,messages,ui)+text[end:]
 return text

def kurosaki_overview(text,language):
 """Keep mapper support boundaries beside the emulator's mapper chapter."""
 text=re.sub(r'<!-- mapper-ciram:start -->.*?<!-- mapper-ciram:end -->','',text,flags=re.S)
 title='画面RAMの割り当て' if language=='ja' else 'Nametable RAM mapping'
 description=('AxROMの下側・上側1画面、FME7の縦・横・下側・上側1画面、MMC5のCIRAMだけを使う16通りの配置をPPUの読み書きと描画へ反映します。MMC5のExRAMと塗りつぶし描画には対応していません。対応範囲の確認には、KITAQFCのマッパー別サンプルを参照してください。' if language=='ja' else 'PPU reads, writes and rendering use AxROM’s lower/upper single-screen selection, FME7’s vertical/horizontal/lower/upper selection and all sixteen CIRAM-only MMC5 layouts. MMC5 ExRAM and fill rendering are not supported. See the KITAQFC board-specific examples for the tested behavior.')
 link='設定値と実行サンプル' if language=='ja' else 'Mode values and executed examples'
 block='<!-- mapper-ciram:start --><h3 id="mapper-nametable-ram">'+title+'</h3><p>'+description+'</p><p><a href="kitaqfc.html#api-__mirroring_set">'+link+'</a></p><!-- mapper-ciram:end -->'
 match=re.search(r'<h2 id="3-[^"]+">.*?</h2>',text,re.S);assert match
 return text[:match.end()]+block+text[match.end():]

if __name__=='__main__':
 import api_contracts as api
 for language in ['ja','en']:
  folder=SITE if language=='ja' else SITE/language
  for name in ['kitaqfc','fc-library']:
   path=folder/(name+'.html');write_page(path,overview(path.read_text(encoding='utf-8'),language))
  path=folder/'kurosaki.html';write_page(path,kurosaki_overview(path.read_text(encoding='utf-8'),language))
 _,_,contracts=api.load()
 keys={p+':'+r['name'] for p in ['gb','fc'] for r in read(SITE/('reference/'+p+'-api.json'))['records']}
 assert set(contracts)<=keys
 report=dict(active_languages=['ja','en'],reviewed=len(contracts),remaining=len(keys-set(contracts)),missing=sorted(keys-set(contracts)))
 (SITE/'tools/api_descriptions/coverage.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print('14 verified mapper cards rendered in JA/EN;',report['remaining'],'API cards remain')
