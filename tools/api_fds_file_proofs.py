"""Publish the two file-I/O contracts only with current CPU and image evidence."""
from pathlib import Path
import hashlib,html,json,re
from api_physics_proofs import verify_row
from api_mapper_proofs import write_page
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
REVIEW='fds-file-source-20260923';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def verified_examples(contracts):
 selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
 if not selected:return {}
 assert set(selected)=={'fc:__fds_load_file','fc:__fds_save_file'}
 for p,h in read(SITE/'tools/api_descriptions/fds_file_review_sources.json')['source_sha256'].items():assert sha(REPOS/p)==h
 report=read(SITE/'verification/api-fds-file/example/results.json');assert report['script_sha256']==sha(SITE/'tools/check_fds_file_examples.py')
 rows=report['records'];assert len(rows)==2 and {r['mode'] for r in rows}=={'default','unoptimized'}
 for r in rows:
  verify_row(r);assert r['actual']==[0,11,44,0,0,7,28,0,165,2,3,1]
  assert r['pixel_mismatches']==0
 state=read(SITE/'verification/api-fds-file/state/file_io.json')
 assert state['test_sha256']==sha(REPOS/'kitaqfc/scripts/test-fds-file-io.py') and state['fixture_sha256']==sha(REPOS/'kitaqfc/scripts/fds_fileio_fixture.py')
 assert state['compiler_sha256']==sha(REPOS/'kitaqfc/kitaqfc.exe') and state['emulator_sha256']==sha(REPOS/'kurosaki/kurosaki.exe')
 assert len(state['records'])==40 and all(r['passed'] for r in state['records'])
 names={'relocate','forward-overlap','backward-overlap','native-null','same-address','zero-size','load-error','missing-count','save-error','unknown-id','boot-id','id-255','not-last','bad-size','bad-destination','wrap-destination','bad-source','table-page','side-1','side-2'}
 assert {r['name'] for r in state['records']}=={n+'-'+v for n in names for v in ['default','O0']}
 for r in state['records']:
  name=r['name'].rsplit('-',1)[0];actual=r['actual']
  assert r['build_exit']==0 and actual[5]==165
  invalid_id=name in {'unknown-id','boot-id','id-255'}
  invalid_dst=name in {'bad-destination','wrap-destination'}
  invalid_save=invalid_id or name in {'not-last','bad-size','bad-source'}
  transfer_error=39 if name=='load-error' else 64 if name=='missing-count' else 0
  assert actual[0]==(255 if invalid_id or invalid_dst else transfer_error)
  assert actual[1]==(255 if invalid_save else 3 if name=='save-error' else 0)
  assert actual[4]==(255 if invalid_id else transfer_error)
  assert r['load_calls']==(0 if invalid_id else 1 if invalid_dst else 2)
  assert r['save_calls']==(0 if invalid_save else 1)
  if not invalid_save:assert r['ordinal']==r['expected_ordinal']==(12 if name=='table-page' else 0 if name.startswith('side-') else 3)
 result={}
 for key,c in selected.items():
  ex=c['example'];source=(SITE/ex['program']).read_text(encoding='utf-8')
  assert ex['code'] in source and re.search(r'\b'+key.split(':')[1]+r'\s*\(',ex['code'])
  result[key]=dict(api=key.split(':')[1],kind='fds-file',runs=[r for r in rows if r['mode']=='default'])
 return result

def overview(text,language,library=False):
 import api_contracts as api
 messages,ui,contracts=api.load();proofs=verified_examples(contracts);selected={k:contracts[k] for k in proofs};api.attach_verified_images(selected,proofs)
 for name,guard in [('fds_file.h','FDS_FILE_H'),('intrinsics.h','INTRINSICS_H')]:
  source=(REPOS/'kitaqfc/lib'/name).read_text(encoding='utf-8').strip()
  def replace_header(m):
   return '<pre><code>'+html.escape(source)+'</code></pre>' if html.unescape(m.group(1)).strip().startswith('#ifndef '+guard+'\n') else m.group(0)
  text=re.sub(r'<pre><code>(.*?)</code></pre>',replace_header,text,flags=re.S)
 records={r['name']:r for r in read(SITE/'reference/fc-api.json')['records']}
 for name,start,end in reversed(api.CardRanges(text).ranges):
  key='fc:'+name
  if key not in selected:continue
  r=records[name];c=selected[key];fp=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest();assert fp==c['record_sha256']
  text=text[:start]+api.render(r,c,language,messages,ui)+text[end:]
 if library:
  prefix='' if language=='ja' else '../';text=re.sub(r'<!-- fds-file-overview:start -->.*?<!-- fds-file-overview:end -->','',text,flags=re.S)
  title='FDSファイルと固定長セーブ領域' if language=='ja' else 'FDS files and fixed-size save slots'
  prose='fds_file.hは、ファイルをゲーム用バッファへ読む処理と、ディスクに確保したセーブ領域へ書く処理を提供します。fds_save.hは同じ宣言を読み込むためのヘッダーです。オーバーレイの関数呼び出しにはfds_overlay.hを使います。' if language=='ja' else 'fds_file.h provides file loading into game buffers and writing to a reserved disk save slot. fds_save.h includes the same declarations. Use fds_overlay.h for calls into overlay code.'
  block='<!-- fds-file-overview:start --><section><h3 id="module-fds-file">'+title+'</h3><p>'+prose+'</p><p><a href="kitaqfc.html#api-__fds_load_file">__fds_load_file()</a> / <a href="kitaqfc.html#api-__fds_save_file">__fds_save_file()</a></p><p>'
  for file in ['fds_file_io.c','fds_file_io_manifest.json','fds_file_io_payload.bin']:
   block+='<a href="'+prefix+'samples/api-examples/fc/'+file+'">'+file+'</a> '
  block+='</p></section><!-- fds-file-overview:end -->'
  anchor='<h3 id="module-fds_sound">';assert anchor in text;text=text.replace(anchor,block+anchor,1)
 return text
if __name__=='__main__':
 import api_contracts as api
 for language in ['ja','en']:
  for name in ['kitaqfc','fc-library']:
   path=(SITE if language=='ja' else SITE/language)/(name+'.html');write_page(path,overview(path.read_text(encoding='utf-8'),language,library=name=='fc-library'))
 contracts=api.load()[2];keys={p+':'+r['name'] for p in ['gb','fc'] for r in read(SITE/('reference/'+p+'-api.json'))['records']};assert set(contracts)<=keys
 report=dict(active_languages=['ja','en'],reviewed=len(contracts),remaining=len(keys-set(contracts)),missing=sorted(keys-set(contracts)))
 (SITE/'tools/api_descriptions/coverage.json').write_text(json.dumps(report,indent=2));print('Two FDS file-I/O APIs rendered;',report)
