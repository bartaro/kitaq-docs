"""Render source-bound queue and PPU additions without weakening unrelated checks."""
import hashlib,json,re
from pathlib import Path
import api_contracts as api
from api_audio_queue_proofs import verified_examples as verify_queue
from api_ppu_library_proofs import verified_shadow_examples
SITE=Path(__file__).resolve().parents[1]

def overview(text,platform,language):
    messages,ui,contracts=api.load()
    reviews=['audio-queue-source-20260922'] if platform=='gb' else ['ppu-declarations-source-20260915','runtime-ppu-source-20260915','ppu-shadow-source-20260922']
    selected={k:v for k,v in contracts.items() if v['review'] in reviews}
    proofs=verify_queue(contracts) if platform=='gb' else {**api.verified_ppu_declaration_examples(contracts),**api.verified_runtime_ppu_examples(contracts),**verified_shadow_examples(contracts)}
    assert set(selected)==set(proofs)
    api.attach_verified_images(selected,proofs)
    records={r['name']:r for r in json.loads((SITE/f'reference/{platform}-api.json').read_text(encoding='utf-8'))['records']}
    edits=[];found=set()
    for name,start,end in api.CardRanges(text).ranges:
        key=platform+':'+name
        if key not in selected:continue
        c=selected[key];r=records[name]
        fingerprint=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest();assert fingerprint==c['record_sha256']
        edits.append((start,end,api.render(r,c,language,messages,ui)));found.add(key)
    for start,end,content in reversed(edits):text=text[:start]+content+text[end:]
    for key in selected.keys()-found:
        name=key.split(':')[1];r=records[name];c=selected[key]
        anchor='audio_vblank' if platform=='gb' else 'intrinsics' if name.startswith('__') else 'ppu'
        pattern=r'(<h3\b[^>]*id="module-'+anchor+r'"[^>]*>.*?</h3>)'
        if not re.search(pattern,text,re.S):
            # Intrinsic functions belong in the compiler reference, not the C-library volume.
            if anchor=='intrinsics' and '<h2 id="intrinsics">' in text:pattern=r'(<h2 id="intrinsics">.*?</h2>)'
            else:continue
        text,count=re.subn(pattern,lambda m:m[1]+api.render(r,c,language,messages,ui),text,count=1,flags=re.S);assert count==1
    return text

if __name__=='__main__':
    for language in ['ja','en']:
        for platform in ['gb','fc']:
            for name in [('kitaq'+platform),platform+'-library']:
                path=(SITE if language=='ja' else SITE/'en')/(name+'.html')
                path.write_text(overview(path.read_text(encoding='utf-8'),platform,language),encoding='utf-8')
    print('Queue and PPU feature cards refreshed in JA/EN.')
