"""Require current codec behavior and visible teaching results before rendering."""
from pathlib import Path
import hashlib,html,json,re
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912';PRIVATE=SITE.parents[1]/'publish/library_docs_20260914/fc-effects'
REVIEW='zx0-source-20260922';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def check_tools(row):
 p=row['platform'];repo=REPOS/('kitaq'+p)
 assert sha(repo/('kitaq'+p+'.exe'))==row['compiler_sha256'],'compiler changed'
 assert sha(REPOS/('kokura/kokura-cli.exe' if p=='gb' else 'kurosaki/kurosaki.exe'))==row['emulator_sha256'],'emulator changed'
 for name,digest in row['library_sha256'].items():assert sha(repo/'lib'/name)==digest,name
 assert row['passed']
def verified_examples(contracts):
 selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
 if not selected:return {}
 assert len(selected)==6
 for family,count in [('targets',48),('edges',6),('vram',6)]:
  report=read(PRIVATE/'zx0'/family/'results.json')
  assert report['script_sha256']==sha(PRIVATE/('check_zx0_'+family+'.py'))
  assert len(report['cases'])==count
  for row in report['cases']:
   check_tools(row)
   p=row['platform'];v=row['variant']
   if family=='targets':folder=PRIVATE/'zx0/targets'/row['name']/(row['producer']+'-'+p+'-'+v)
   elif family=='edges':
    assert row['case_count']==41 and not row['failures'] and row['done']==165
    folder=PRIVATE/'zx0/edges'/(p+'-'+v)
   else:folder=PRIVATE/'zx0/vram'/(p+'-'+row['mode']+'-'+v)
   assert sha(folder/'test.c')==row['source_sha256']
   assert sha(folder/('test.gb' if p=='gb' else 'test.nes'))==row['rom_sha256']
 host=read(PRIVATE/'zx0/host-results.json');assert len(host['cases'])==21 and all(r['passed'] for r in host['cases'])
 assert host['script_sha256']==sha(PRIVATE/'check_zx0_host.py')
 assert host['tool_sha256']==sha(REPOS/'kitaqgb/kitaqgb-zx0.exe')
 edges=read(PRIVATE/'zx0/host-edges/results.json');assert len(edges['cases'])==68 and all(r['passed'] for r in edges['cases'])
 assert edges['script_sha256']==sha(PRIVATE/'check_zx0_host_edges.py')
 for row in edges['cases']:
  name='kitaq'+row['platform'];assert row['tool_sha256']==sha(REPOS/name/(name+'-zx0.exe'))
 report=read(SITE/'verification/api-zx0/results.json');assert report['script_sha256']==sha(SITE/'tools/check_zx0_examples.py')
 runs=report['records'];assert {(r['platform'],r['mode']) for r in runs}=={('gb','dmg'),('gb','cgb'),('fc','ntsc')} and len(runs)==3
 for row in runs:
  check_tools(row);assert row['pixel_mismatches']==0 and row['colors_passed']
  for name in ['source','image']:assert sha(SITE/row[name])==row[name+'_sha256']
  folder=SITE/'verification/api-zx0'/(row['platform']+'-'+row['mode'])
  assert sha(folder/('example.gb' if row['platform']=='gb' else 'example.nes'))==row['rom_sha256']
  for path,digest in row['support_sha256'].items():assert sha(SITE/path)==digest,path
 for key,contract in selected.items():
  code=contract['example']['code'];assert code in (SITE/contract['example']['program']).read_text(encoding='utf-8')
  assert re.search(r'\b'+key.split(':')[1]+r'\s*\(',code)
 return {k:dict(api=k.split(':')[1],kind='zx0',runs=[r for r in runs if r['platform']==k.split(':')[0]]) for k in selected}

def overview(text,platform,language):
 import api_contracts as api
 messages,ui,contracts=api.load();proofs=verified_examples(contracts)
 chosen={k:v for k,v in contracts.items() if k.startswith(platform+':') and v['review']==REVIEW}
 api.attach_verified_images(chosen,{k:v for k,v in proofs.items() if k in chosen})
 records={r['name']:r for r in read(SITE/f'reference/{platform}-api.json')['records']};index=api.ORDER.index(language)
 modules=read(SITE/'tools/api_descriptions/zx0_modules.json')
 block='<!-- zx0-module:start --><section data-module-contract="'+REVIEW+'"><h3 id="module-zx0">zx0</h3>'
 block+=''.join('<p>'+api.inline(messages[k][index])+'</p>' for k in modules[platform+':zx0'])
 tool='kitaq'+platform+'-zx0.exe'
 commands='.\\'+tool+' tiles.bin tiles.zx0\n.\\'+tool+' tiles.bin tiles.h --header=tiles\n.\\'+tool+' map.bin map.kqa --format=auto\n.\\'+tool+' tiles.zx0 restored.bin --decompress'
 block+='<p>'+('リポジトリ直下で実行するPC側のコマンド例です。ツールは`tools/zx0/build.ps1`でビルドできます。' if language=='ja' else 'Run these host commands from the repository root. Build the tool with tools/zx0/build.ps1.')+'</p><pre><code>'+html.escape(commands)+'</code></pre>'
 for key,c in chosen.items():
  r=records[key.split(':')[1]];fp=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest();assert fp==c['record_sha256']
  block+=api.render(r,c,language,messages,ui)
 block+='</section><!-- zx0-module:end -->'
 text=re.sub(r'<!-- zx0-module:start -->.*?<!-- zx0-module:end -->','',text,flags=re.S)
 anchor=re.search(r'<h3 id="module-[^"]+">',text);assert anchor
 text=text[:anchor.start()]+block+text[anchor.start():]
 # The appendix includes the exact public header, not a declaration-only stub.
 text=re.sub(r'<!-- zx0-header:start -->.*?<!-- zx0-header:end -->','',text,flags=re.S)
 source_path='kitaq'+platform+'/lib/zx0.h'
 header='<details class="searchable"><summary><code>zx0.h</code></summary><div class="codebox"><pre><code>'+html.escape((REPOS/source_path).read_text(encoding='utf-8'))+'</code></pre></div><p class="source">'+source_path+'</p></details>'
 if '<h2 id="headers">' in text:
  pos=text.index('</h2>',text.index('<h2 id="headers">'))+5
  text=text[:pos]+'<!-- zx0-header:start -->'+header+'<!-- zx0-header:end -->'+text[pos:]
 return text
if __name__=='__main__':
 for language in ['ja','en']:
  for platform in ['gb','fc']:
   p=(SITE if language=='ja' else SITE/'en')/(platform+'-library.html');p.write_text(overview(p.read_text(encoding='utf-8'),platform,language),encoding='utf-8')
 print('Six ZX0 API cards, module guides and captured results rendered in JA/EN.')
