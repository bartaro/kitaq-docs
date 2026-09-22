"""Bind FC wireframe documentation to the complete executed teaching program."""
from pathlib import Path
import hashlib,html,json,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
REVIEW='fc-wireframe-source-20260922'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
    if not selected:return {}
    assert len(selected)==8
    reviewed=json.loads((SITE/'tools/api_descriptions/fc_wireframe_review_sources.json').read_text(encoding='utf-8'))
    for path,digest in reviewed['source_sha256'].items():
        if sha(REPOS/path)!=digest:raise ValueError('FC wireframe source changed: '+path)
    report=json.loads((SITE/'verification/api-wireframe-fc/projection/results.json').read_text())
    assert report['script_sha256']==sha(SITE/'tools/check_fc_wireframe_projection.py')
    runs=report['records'];assert len(runs)==3 and {r['mode'] for r in runs}=={'64x48','96x64','128x96'}
    for row in runs:
        verify_row(row)
        assert row['pixel_mismatches']==0 and row['unsafe_vram_writes']==0 and row['unsafe_address_writes']==0
    result={}
    for key,contract in selected.items():
        source=SITE/contract['example']['program'];text=source.read_text(encoding='utf-8');name=key.split(':')[1]
        assert re.search(r'\b'+re.escape(name)+r'\s*\(',text),key
        assert contract['example']['code'] in text,key
        assert all(r['source']==contract['example']['program'] for r in runs)
        result[key]={'api':name,'kind':'fc-wireframe','runs':runs}
    return result

def render_cards(text,language):
    import api_contracts
    messages,ui,contracts=api_contracts.load()
    selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
    proofs=verified_examples(selected);api_contracts.attach_verified_images(selected,proofs)
    records={r['name']:r for r in json.loads((SITE/'reference/fc-api.json').read_text(encoding='utf-8'))['records']}
    title='各関数の使い方' if language=='ja' else 'Individual function reference'
    block='<!-- fc-wire-cards:start --><section data-module-contract="'+REVIEW+'"><h3 id="module-wire3d">wire3d — '+title+'</h3>'
    for key,contract in selected.items():
        record=records[key.split(':')[1]]
        fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
        assert fingerprint==contract['record_sha256'],key
        block+=api_contracts.render(record,contract,language,messages,ui)
    block+='</section><!-- fc-wire-cards:end -->'
    text=re.sub(r'<!-- fc-wire-cards:start -->.*?<!-- fc-wire-cards:end -->','',text,flags=re.S)
    anchor='</section><!-- fc-wire-guide:end -->';assert text.count(anchor)==1
    return text.replace(anchor,block+anchor)

def ensure_header(text):
    # Keep the complete-header appendix consistent with inventory membership.
    anchor='<h2 id="headers">'
    if anchor not in text:return text
    block=''
    for name in ['danmaku.h','wire3d.h','wire3d_tables.h']:
        if 'kitaqfc/lib/'+name+'</p></details>' in text:continue
        header=html.escape((REPOS/'kitaqfc/lib'/name).read_text(encoding='utf-8').strip())
        block+='<details class="searchable"><summary><code>'+name+'</code></summary><div class="codebox"><pre><code>'+header+'</code></pre></div><p class="source">kitaqfc/lib/'+name+'</p></details>'
    position=text.index('</h2>',text.index(anchor))+5
    return text[:position]+block+text[position:]
