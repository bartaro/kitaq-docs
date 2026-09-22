"""Bind the NMI music lessons to state, channel writes, images and actual PCM."""
from pathlib import Path
import hashlib,html,json,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
REVIEW='fc-audio-vblank-source-20260922'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def verified_examples(contracts):
 selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
 if not selected:return {}
 assert len(selected)==13
 folder=SITE/'verification/api-fc-audio-vblank'
 state=read(folder/'state/results.json')
 assert state['script_sha256']==sha(SITE/'tools/check_fc_audio_vblank_state.py')
 for name,path in [('compiler',REPOS/'kitaqfc/kitaqfc.exe'),('emulator',REPOS/'kurosaki/kurosaki.exe'),('library',REPOS/'kitaqfc/lib/audio_vblank.c'),('header',REPOS/'kitaqfc/lib/audio_vblank.h')]:
  assert state[name+'_sha256']==sha(path),name+' changed'
 rows=state['records'];assert len(rows)==4
 assert {(r['name'],r['variant']) for r in rows}=={(n,v) for n in ['boundary','channels'] for v in ['default','unoptimized']}
 for row in rows:
  assert row['passed'] and row['actual']==([54,0,165] if row['name']=='boundary' else [2,0,165])
  for key in ['source','rom']:assert sha(SITE/row[key])==row[key+'_sha256']
  if row['name']=='channels':assert row['channel_write_count']==576 and row['channel_writes']==row['expected_writes']
 visual=read(folder/'example/results.json')
 assert visual['script_sha256']==sha(SITE/'tools/check_fc_audio_vblank.py')
 assert len(visual['records'])==3 and {r['mode'] for r in visual['records']}=={'nrom','mmc3','nrom-O0'}
 for row in visual['records']:
  verify_row(row)
  assert row['actual']==[1,7,0,1,0,1,1,0,165]
  assert sha(SITE/row['audio'])==row['audio_sha256']
  assert row['audio_segments']['during_busy']['rms']>100 and row['audio_segments']['after_refill']['rms']>100
  assert row['audio_segments']['after_end']['peak']==0
 for key,c in selected.items():
  sample=(SITE/c['example']['program']).read_text(encoding='utf-8')
  assert c['example']['code'] in sample
  if key!='fc:__nes_audio_vblank_tick':assert re.search(r'\b'+key.split(':')[1]+r'\s*\(',c['example']['code'])
 # Present one capture rather than repeat the same screen/audio for each build mode.
 return {key:dict(api=key.split(':')[1],kind='fc-audio-vblank',runs=[visual['records'][0]]) for key in selected}

def overview(text,language):
 import api_contracts as api
 messages,ui,contracts=api.load();proofs=verified_examples(contracts)
 selected={k:contracts[k] for k in proofs};api.attach_verified_images(selected,proofs)
 doc=read(SITE/'reference/fc-api.json');records={r['name']:r for r in doc['records']}
 index=api.ORDER.index(language);title='NMIによる4音源の音楽再生' if language=='ja' else 'Four-channel music driven by NMI'
 modules=read(SITE/'tools/api_descriptions/fc_audio_vblank_modules.json')['fc:audio_vblank']
 block='<!-- fc-audio-vblank:start --><section data-module-contract="'+REVIEW+'"><h3 id="module-audio_vblank">audio_vblank.h — '+title+'</h3>'
 block+=''.join('<p>'+api.inline(messages[k][index])+'</p>' for k in modules)
 labels=['待機時間','CH1: パルス1','CH2: パルス2','CH3: 三角波','CH4: ノイズ'] if language=='ja' else ['Delay','CH1: pulse 1','CH2: pulse 2','CH3: triangle','CH4: noise']
 block+='<table><thead><tr>'+''.join('<th>'+label+'</th>' for label in labels)+'</tr></thead><tbody><tr><td>24</td><td>24 (C4)</td><td>12 (C3)</td><td>0 (C2)</td><td>2</td></tr></tbody></table>'
 block+='<p><a href="kitaqfc.html#api-__nes_audio_vblank_tick">'+('コンパイラが接続するNMIフック' if language=='ja' else 'NMI hook connected by the compiler')+'</a></p>'
 for key,c in selected.items():
  if key=='fc:__nes_audio_vblank_tick':continue
  r=records[key.split(':')[1]]
  fp=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
  assert fp==c['record_sha256'];block+=api.render(r,c,language,messages,ui)
 block+='</section><!-- fc-audio-vblank:end -->'
 text=re.sub(r'<!-- fc-audio-vblank:start -->.*?<!-- fc-audio-vblank:end -->','',text,flags=re.S)
 # A full catalog regeneration can already have created this module; remove
 # its cards and heading before placing the reviewed section at the same location.
 for name,start,end in reversed(api.CardRanges(text).ranges):
  if 'fc:'+name in selected:text=text[:start]+text[end:]
 text=re.sub(r'<h3 id="module-audio_vblank">.*?</h3>(?:<!-- api-module:start -->.*?<!-- api-module:end -->)?','',text,flags=re.S)
 anchor='<h3 id="module-bank">';assert text.count(anchor)==1
 text=text.replace(anchor,block+anchor)
 # Make the driver discoverable from the beginner sound chapter as well as
 # the alphabetic API dictionary and the repository README.
 text=re.sub(r'<!-- fc-audio-vblank-guide:start -->.*?<!-- fc-audio-vblank-guide:end -->','',text,flags=re.S)
 guide=('NMIで4音源の音楽を進めるには、<a href="#module-audio_vblank">audio_vblank.h</a>を使います。RAMキューの補充、音の維持・停止、反復再生の説明と、実際に録音したサンプル音声を掲載しています。' if language=='ja' else 'Use <a href="#module-audio_vblank">audio_vblank.h</a> for four-channel music driven by NMI. Its reference explains RAM-queue refill, held and stopped notes, looping playback, and includes captured audio from the complete sample.')
 text=re.sub(r'(<h2 id="6-[^"]+">.*?</h2>)',lambda m:m[1]+'<!-- fc-audio-vblank-guide:start --><p>'+guide+'</p><!-- fc-audio-vblank-guide:end -->',text,count=1,flags=re.S)
 # Ensure the complete-header appendix gains the actual new public header.
 path='kitaqfc/lib/audio_vblank.h'
 if '<summary><code>audio_vblank.h</code>' not in text:
  entry='<details class="searchable"><summary><code>audio_vblank.h</code> — '+title+'</summary><div class="codebox"><pre><code>'+html.escape((REPOS/path).read_text(encoding='utf-8').strip())+'</code></pre></div><p class="source">'+path+'</p></details>'
  match=re.search(r'<h2 id="headers">.*?</h2>',text,re.S);assert match
  text=text[:match.end()]+entry+text[match.end():]
 return api.refresh_complete_headers(text,'fc')

def hook_overview(text,language):
 import api_contracts as api
 messages,ui,contracts=api.load();key='fc:__nes_audio_vblank_tick'
 proof=verified_examples(contracts)[key];selected={key:contracts[key]}
 api.attach_verified_images(selected,{key:proof})
 record=next(r for r in read(SITE/'reference/fc-api.json')['records'] if r['name']=='__nes_audio_vblank_tick')
 for name,start,end in reversed(api.CardRanges(text).ranges):
  if name==record['name']:text=text[:start]+text[end:]
 anchor=re.search(r'<h3 id="module-intrinsics">.*?</h3>',text,re.S);assert anchor
 return text[:anchor.end()]+api.render(record,selected[key],language,messages,ui)+text[anchor.end():]

if __name__=='__main__':
 for lang in ['ja','en']:
  path=(SITE if lang=='ja' else SITE/'en')/'fc-library.html'
  path.write_text(overview(path.read_text(encoding='utf-8'),lang),encoding='utf-8')
  path=path.with_name('kitaqfc.html')
  path.write_text(hook_overview(path.read_text(encoding='utf-8'),lang),encoding='utf-8')
 print('13 NMI music APIs rendered in JA/EN with the captured phrase')
