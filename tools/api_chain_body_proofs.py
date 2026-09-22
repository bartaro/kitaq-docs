"""Bind articulated-chain lessons to exact state and sprite-image checks."""
from pathlib import Path
import hashlib,json,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
REVIEW='chain-body-source-20260922'
def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
    if not selected:return {}
    assert len(selected)==10
    state=read(SITE/'verification/api-chain-body/state-matrix.json')
    assert state['passed'] and state['script_sha256']==sha(SITE/'tools/check_chain_body.py')
    assert state['fixtures_sha256']==sha(SITE/'tools/chain_body_fixtures.json')
    for path,digest in state['library_sha256'].items():assert sha(REPOS/path)==digest
    fixtures={r['name']:r for r in read(SITE/'tools/chain_body_fixtures.json')}
    variants={'gb':['default','unoptimized','stack'],'fc':['default','unoptimized','no-inline','fastcall']}
    wanted={(p,f,v,m) for p in variants for f in fixtures for v in variants[p] for m in (['dmg','cgb'] if p=='gb' else ['ntsc'])}
    assert len(state['records'])==20
    assert {(r['platform'],r['name'],r['variant'],r['mode']) for r in state['records']}==wanted
    for row in state['records']:
        p=row['platform'];assert row['passed'] and row['actual']==row['expected']==fixtures[row['name']]['expected']
        for field in ['source','rom']:assert sha(SITE/row[field])==row[field+'_sha256']
        expected_source=fixtures[row['name']]['source'].replace('0xC600','0x0600') if p=='fc' else fixtures[row['name']]['source']
        assert (SITE/row['source']).read_text(encoding='utf-8')==expected_source
        assert sha(REPOS/f'kitaq{p}/kitaq{p}.exe')==row['compiler_sha256']
        assert sha(REPOS/('kokura/kokura-cli.exe' if p=='gb' else 'kurosaki/kurosaki.exe'))==row['emulator_sha256']
    visual=read(SITE/'verification/api-chain-body/example/results.json')
    assert visual['script_sha256']==sha(SITE/'tools/check_chain_body_examples.py')
    assert len(visual['records'])==3 and {(r['platform'],r['mode']) for r in visual['records']}=={('gb','dmg'),('gb','cgb'),('fc','ntsc')}
    for row in visual['records']:
        verify_row(row);assert row['diagram_pixels']==6400
    for c in selected.values():assert c['example']['code'] in (SITE/c['example']['program']).read_text(encoding='utf-8')
    return {key:dict(api=key.split(':')[1],kind='chain-body',runs=[r for r in visual['records'] if r['platform']==key.split(':')[0]]) for key in selected}

def overview(text,platform,language):
    import api_contracts as api
    messages,ui,contracts=api.load();proofs=verified_examples(contracts)
    selected={k:contracts[k] for k in proofs if k.startswith(platform+':')};api.attach_verified_images(selected,{k:proofs[k] for k in selected})
    records={r['name']:r for r in read(SITE/f'reference/{platform}-api.json')['records']}
    # Remove our explicit block or standalone cards, then insert once after the module introduction.
    text=re.sub(r'<!-- chain-body:start -->.*?<!-- chain-body:end -->','',text,flags=re.S)
    for name,start,end in reversed(api.CardRanges(text).ranges):
        if platform+':'+name in selected:text=text[:start]+text[end:]
    cards=[]
    for suffix in ['init','reset','step','grow','clear']:
        name='chain_body_'+suffix;r=records[name];c=selected[platform+':'+name]
        fp=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
        assert fp==c['record_sha256'];cards.append(api.render(r,c,language,messages,ui))
    anchor=re.search(r'<h3 id="module-chain">.*?</h3>(?:<!-- api-module:start -->.*?<!-- api-module:end -->)?',text,re.S);assert anchor
    text=text[:anchor.end()]+'<!-- chain-body:start -->'+''.join(cards)+'<!-- chain-body:end -->'+text[anchor.end():]
    return api.refresh_complete_headers(text,platform)

if __name__=='__main__':
    for lang in ['ja','en']:
        for platform in ['gb','fc']:
            p=(SITE if lang=='ja' else SITE/lang)/f'{platform}-library.html'
            p.write_text(overview(p.read_text(encoding='utf-8'),platform,lang),encoding='utf-8')
    print('Ten API cards rendered in Japanese and English with current images')
