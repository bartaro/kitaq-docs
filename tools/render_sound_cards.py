"""Render sound and queue contracts only after all current sound proofs pass."""
from pathlib import Path
import hashlib,json,re
import api_contracts as api
from api_sound_proofs import verified_examples as verify_sound
from api_audio_queue_proofs import verified_examples as verify_queue
SITE=Path(__file__).resolve().parents[1]

def main():
 messages,ui,contracts=api.load();proofs={**verify_sound(contracts),**verify_queue(contracts)}
 selected={k:contracts[k] for k in proofs};api.attach_verified_images(selected,proofs)
 for language in ['ja','en']:
  for platform in ['gb','fc']:
   records={r['name']:r for r in json.loads((SITE/f'reference/{platform}-api.json').read_text(encoding='utf-8'))['records']}
   for name in ['kitaq'+platform,platform+'-library']:
    path=(SITE if language=='ja' else SITE/'en')/(name+'.html');text=path.read_text(encoding='utf-8');edits=[]
    for func,start,end in api.CardRanges(text).ranges:
     key=platform+':'+func
     if key not in selected:continue
     r=records[func];c=selected[key]
     digest=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
     assert digest==c['record_sha256'],key
     edits.append((start,end,api.render(r,c,language,messages,ui)))
    for start,end,content in reversed(edits):text=text[:start]+content+text[end:]
    if name.endswith('-library'):
     # Update only the sound module introductions, preserving other reviewed modules.
     modules=json.loads((SITE/'tools/api_descriptions/sound_modules.json').read_text(encoding='utf-8'))
     for key,keys in modules.items():
      owner,module=key.split(':')
      if owner!=platform:continue
      pattern=r'(<h3\b[^>]*id="module-'+module+r'"[^>]*>.*?</h3>)(?:<!-- api-module:start -->.*?<!-- api-module:end -->)?'
      block='<!-- api-module:start --><div data-module-contract="sound-source-20260916">'+''.join('<p>'+api.inline(messages[k][api.ORDER.index(language)])+'</p>' for k in keys)+'</div><!-- api-module:end -->'
      text=re.sub(pattern,lambda m:m[1]+block,text,count=1,flags=re.S)
     text=api.refresh_complete_headers(text,platform)
    path.write_text(text,encoding='utf-8')
    print(language,name,len(edits),'current sound cards')

if __name__=='__main__':main()
