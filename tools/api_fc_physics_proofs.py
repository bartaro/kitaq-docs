"""Bind the 22 FC physics contracts to numeric cases and complete color lessons."""
from pathlib import Path
import hashlib,html,json,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];ROOT=SITE.parents[1];REPOS=ROOT/'publish/github_20260912'
REVIEW='fc-physics-source-20260922';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
    if not selected:return {}
    assert len(selected)==22
    for path,digest in read(SITE/'tools/api_descriptions/fc_physics_review_sources.json')['source_sha256'].items():assert sha(REPOS/path)==digest,path
    report=read(SITE/'verification/api-physics-fc/results.json')
    assert report['script_sha256']==sha(SITE/'tools/check_fc_physics_examples.py')
    assert report['spec_sha256']==sha(SITE/'tools/api_descriptions/physics_examples.json')
    runs=report['records'];assert len(runs)==3 and {r['group'] for r in runs}=={'body2d','surface','body3d'}
    for r in runs:verify_row(r);assert not r['unsafe_ppu_writes']
    folder=ROOT/'publish/library_docs_20260914/fc-effects/physics-worlds/state';state=read(folder/'report.json')
    assert state['passed'] and len(state['records'])==60
    assert state['script_sha256']==sha(SITE/'tools/check_compiler_parity.py')
    assert state['checker_sha256']==sha(SITE/'tools/check_fc_physics_worlds.py')
    assert state['fixture_author_sha256']==sha(SITE/'tools/check_physics_edges.py')
    assert state['fixtures_sha256']==sha(folder.parent/'fixtures.json')
    for path,digest in state['library_sha256'].items():assert sha(REPOS/'kitaqfc/lib'/path)==digest,path
    for r in state['records']:
        assert r['passed'] and r['actual']==r['expected']
        case=folder/'fc'/r['name']/r['variant']
        assert sha(case/'case.c')==r['source_sha256'] and sha(case/'case.nes')==r['rom_sha256']
        assert sha(REPOS/'kitaqfc/kitaqfc.exe')==r['compiler_sha256'] and sha(REPOS/'kurosaki/kurosaki.exe')==r['emulator_sha256']
    result={}
    for key,c in selected.items():
        name=key.split(':')[1];source=(SITE/c['example']['program']).read_text(encoding='utf-8')
        assert c['example']['code'] in source and re.search(r'\b'+name+r'\s*\(',c['example']['code'])
        found=[dict(r,mode='ntsc') for r in runs if r['source']==c['example']['program']];assert len(found)==1
        result[key]=dict(api=name,kind='fc-physics',runs=found)
    return result

def overview(text,language):
    import api_contracts
    messages,ui,contracts=api_contracts.load();selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
    api_contracts.attach_verified_images(selected,verified_examples(selected))
    records={r['name']:r for r in read(SITE/'reference/fc-api.json')['records']};modules=read(SITE/'tools/api_descriptions/fc_physics_modules.json')
    index=api_contracts.ORDER.index(language);block='<!-- fc-physics-worlds:start -->'
    for module in ['physics2d','physics3d']:
        block+='<section data-module-contract="'+REVIEW+'"><h3 id="module-'+module+'">'+module+'</h3>'
        block+=''.join('<p>'+api_contracts.inline(messages[k][index])+'</p>' for k in modules['fc:'+module])
        for key,c in selected.items():
            r=records[key.split(':')[1]]
            if r['module']!=module:continue
            fingerprint=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest();assert fingerprint==c['record_sha256']
            block+=api_contracts.render(r,c,language,messages,ui)
        block+='</section>'
    block+='<!-- fc-physics-worlds:end -->'
    text=re.sub(r'<!-- fc-physics-worlds:start -->.*?<!-- fc-physics-worlds:end -->','',text,flags=re.S)
    anchor='<h3 id="module-ppu">';assert text.count(anchor)==1
    text=text.replace(anchor,block+anchor,1)
    appendix='<h2 id="headers">'
    if appendix in text and 'kitaqfc/lib/physics3d.h</p></details>' not in text:
        header=html.escape((REPOS/'kitaqfc/lib/physics3d.h').read_text(encoding='utf-8').strip())
        entry='<details class="searchable"><summary><code>physics3d.h</code></summary><div class="codebox"><pre><code>'+header+'</code></pre></div><p class="source">kitaqfc/lib/physics3d.h</p></details>'
        pos=text.index('</h2>',text.index(appendix))+5;text=text[:pos]+entry+text[pos:]
    return text

if __name__=='__main__':
    from api_physics_proofs import render_fc_module
    for language in ['ja','en']:
        file=(SITE if language=='ja' else SITE/'en')/'fc-library.html'
        file.write_text(overview(render_fc_module(file.read_text(encoding='utf-8'),language),language),encoding='utf-8')
    print('22 FC physics cards and color proofs integrated in JA/EN.')
