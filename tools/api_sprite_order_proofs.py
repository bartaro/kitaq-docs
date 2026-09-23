"""Bind four ordering APIs to numeric, ABI, hardware-mode and image evidence."""
from pathlib import Path
import hashlib,html,json,re
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
REVIEW='sprite-order-source-20260923'
NAMES=['sprite_order_init','sprite_order_begin','sprite_order_push','sprite_order_build']
CASES=['empty','one','four-priority-bands','rotated-bands','phase-normalization',
       'zero-limit','one-output','limit-clamped-to-40','capacity-full','maximum-255-items',
       'clip-8-pixels','clip-16-pixels','zero-capacity','bad-height','null-item-storage',
       'count-exceeds-capacity','begin-preserves-phase']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def verify_reports(state,visual):
    assert state['passed'] and visual['passed']
    assert state['script_sha256']==sha(SITE/'tools/check_sprite_order_state.py')
    assert visual['script_sha256']==sha(SITE/'tools/check_sprite_order_examples.py')
    for p,h in state['library_sha256'].items():assert sha(REPOS/'kitaqgb/lib'/p)==h
    assert set(state['library_sha256'])=={'sprite_order.c','sprite_order.h'}
    assert len(state['records'])==6
    assert {(r['variant'],r['mode']) for r in state['records']}=={(v,m) for v in ['default','O0','stack'] for m in ['dmg','cgb']}
    for r in state['records']:
        assert r['passed'] and r['frames']==600 and r['status']==[5,4,0,0,0,0,3,165]
        assert [c['name'] for c in r['cases']]==CASES
        for case in r['cases']:
            assert case['passed'] and case['actual']==case['expected'] and len(case['actual'])==174
            assert case['actual'][:4]==case['actual'][164:168]==[204]*4
            assert case['actual'][-1]==165
        folder=SITE/'verification/api-sprite-order/state'/r['variant']
        for filename,key in [('case.c','source_sha256'),('case.gb','rom_sha256')]:assert sha(folder/filename)==r[key]
        assert sha(REPOS/'kitaqgb/kitaqgb.exe')==r['compiler_sha256']
        assert sha(REPOS/'kokura/kokura-cli.exe')==r['emulator_sha256']
    wanted={(v,m,120) for v in ['phase0','phase4','phase8','O0-phase4'] for m in ['dmg','cgb']}
    wanted|={('animated',m,f) for m in ['dmg','cgb'] for f in [120,240]}
    assert len(visual['records'])==12
    assert {(r['variant'],r['mode'],r['frames']) for r in visual['records']}==wanted
    for r in visual['records']:
        assert r['passed'] and r['label_pixel_mismatches']==r['sprite_pixel_mismatches']==0
        assert r['sprite_pixels_checked']==1280 and not r['first_mismatches']
        phase=r['state'][0];assert 0<=phase<14 and r['state'][1:]==[14,14,165]
        if r['variant']!='animated':assert phase==int(r['variant'][-1])
        cyclic=list(range(phase,14))+list(range(phase))
        assert r['selected_squares']==[n for n in cyclic if n<12][:8]
        for key in ['source','wrapper','rom','image']:assert sha(SITE/r[key])==r[key+'_sha256']
        assert set(r['support_sha256'])=={'samples/gb_tile_example.h','samples/gb_common.h','samples/font_gb.h'}
        assert set(r['library_sha256'])=={'sprite_order.c','sprite_order.h','sprite.c','sprite.h'}
        for p,h in r['support_sha256'].items():assert sha(SITE/p)==h
        for p,h in r['library_sha256'].items():assert sha(REPOS/'kitaqgb/lib'/p)==h
        assert sha(REPOS/'kitaqgb/kitaqgb.exe')==r['compiler_sha256']
        assert sha(REPOS/'kokura/kokura-cli.exe')==r['emulator_sha256']
    for mode in ['dmg','cgb']:
        moving=sorted([r for r in visual['records'] if r['variant']=='animated' and r['mode']==mode],key=lambda r:r['frames'])
        assert moving[0]['state'][0]!=moving[1]['state'][0]
        assert moving[0]['selected_squares']!=moving[1]['selected_squares']

def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
    if not selected:return {}
    assert set(selected)=={'gb:'+name for name in NAMES}
    state=read(SITE/'verification/api-sprite-order/state/results.json')
    visual=read(SITE/'verification/api-sprite-order/example/results.json')
    verify_reports(state,visual)
    runs=[r for r in visual['records'] if (r['variant'],r['mode']) in [('phase4','dmg'),('phase4','cgb'),('phase8','cgb')]]
    for key,c in selected.items():
        ex=c['example'];source=(SITE/ex['program']).read_text(encoding='utf-8')
        assert ex['code'] in source and re.search(r'\b'+key.split(':')[1]+r'\s*\(',ex['code'])
        assert all(r['source']==ex['program'] for r in runs)
    return {key:dict(api=key.split(':')[1],kind='sprite-order',runs=runs) for key in selected}

def ensure_cards(text,language):
    """Add the module to existing editions; fresh generation already includes it."""
    if '<h2 id="headers">' in text and 'kitaqgb/lib/sprite_order.h</p></details>' not in text:
        header=html.escape((REPOS/'kitaqgb/lib/sprite_order.h').read_text(encoding='utf-8').strip())
        block='<details class="searchable"><summary><code>sprite_order.h</code></summary><div class="codebox"><pre><code>'+header+'</code></pre></div><p class="source">kitaqgb/lib/sprite_order.h</p></details>'
        pos=text.index('</h2>',text.index('<h2 id="headers">'))+5
        text=text[:pos]+block+text[pos:]
    if 'id="module-sprite_order"' in text:return text
    title='スプライトの表示順' if language=='ja' else 'Sprite selection order'
    block='<h3 id="module-sprite_order">sprite_order.h — '+title+'</h3>'
    block+=''.join('<details class="api searchable" id="api-'+name+'"><summary><code>'+name+'</code></summary></details>' for name in NAMES)
    start=re.search(r'<h2\b[^>]*id="api"[^>]*>',text);assert start
    after=re.search(r'<h2\b',text[start.end():]);assert after
    pos=start.end()+after.start()
    return text[:pos]+block+text[pos:]

if __name__=='__main__':
    import api_contracts as api
    result=verified_examples(api.load()[2]);assert len(result)==4
    print('Four sprite-order APIs: six numeric runs, twelve image runs verified')
