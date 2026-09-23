"""Bind the wrapped-distance lesson to its complete numeric and image matrix."""
from pathlib import Path
import hashlib,json,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
REVIEW='chain-wrap-source-20260923'
def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
    if not selected:return {}
    assert set(selected)=={'gb:chain_wrap_delta','fc:chain_wrap_delta'}
    for platform,variants,modes in [('gb',['default','O0','stack'],['dmg','cgb']),('fc',['default','O0','no-inline','fastcall'],['ntsc'])]:
        report=read(SITE/f'verification/api-chain-wrap/state/{platform}-results.json')
        assert report['passed'] and report['vector_count']==3496
        assert report['script_sha256']==sha(SITE/'tools/check_chain_wrap.py')
        wanted={(part,variant,mode) for part in range(7) for variant in variants for mode in modes}
        assert len(report['records'])==len(wanted) and {(r['part'],r['variant'],r['mode']) for r in report['records']}==wanted
        for row in report['records']:
            assert row['platform']==platform and row['passed']
            assert row['actual']==row['expected']==[424 if row['part']==6 else 512,0,0,0,0xA55A]
            for key in ['source','rom']:assert sha(SITE/row[key])==row[key+'_sha256']
            for filename,key in [('chain.c','library_sha256'),('chain.h','header_sha256')]:assert sha(REPOS/f'kitaq{platform}/lib'/filename)==row[key]
            assert sha(REPOS/f'kitaq{platform}/kitaq{platform}.exe')==row['compiler_sha256']
            assert sha(REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe'))==row['emulator_sha256']
    visual=read(SITE/'verification/api-chain-wrap/example/results.json')
    assert visual['script_sha256']==sha(SITE/'tools/check_chain_wrap_examples.py')
    assert len(visual['records'])==3 and {(r['platform'],r['mode']) for r in visual['records']}=={('gb','dmg'),('gb','cgb'),('fc','ntsc')}
    for row in visual['records']:
        verify_row(row);assert row['expected']==[2,65534,80,65456,0]
    for c in selected.values():assert c['example']['code'] in (SITE/c['example']['program']).read_text()
    return {key:dict(api='chain_wrap_delta',kind='chain-wrap',runs=[r for r in visual['records'] if r['platform']==key.split(':')[0]]) for key in selected}
def overview(text,platform,language):
    import api_contracts as api
    messages,ui,contracts=api.load();proofs=verified_examples(contracts)
    key=platform+':chain_wrap_delta';selected={key:contracts[key]};api.attach_verified_images(selected,{key:proofs[key]})
    record=next(r for r in read(SITE/f'reference/{platform}-api.json')['records'] if r['name']=='chain_wrap_delta')
    fp=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest();assert fp==selected[key]['record_sha256']
    text=re.sub(r'<!-- chain-wrap:start -->.*?<!-- chain-wrap:end -->','',text,flags=re.S)
    for name,start,end in reversed(api.CardRanges(text).ranges):
        if name=='chain_wrap_delta':text=text[:start]+text[end:]
    anchor=re.search(r'<h3 id="module-chain">.*?</h3>(?:<!-- api-module:start -->.*?<!-- api-module:end -->)?',text,re.S);assert anchor
    text=text[:anchor.end()]+'<!-- chain-wrap:start -->'+api.render(record,selected[key],language,messages,ui)+'<!-- chain-wrap:end -->'+text[anchor.end():]
    return api.refresh_complete_headers(text,platform)
