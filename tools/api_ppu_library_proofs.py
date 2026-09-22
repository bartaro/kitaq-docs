"""Require successful library execution and matching color capture for PPU cards."""
from pathlib import Path
import hashlib,json
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']=='ppu-declarations-source-20260915'}
    if not selected:return {}
    assert len(selected)==4
    folder=SITE/'verification/api-ppu-declarations';report=read(folder/'results.json');state=read(folder/'state_checks.json')
    assert report['script_sha256']==sha(SITE/'tools/check_ppu_declaration_examples.py')
    assert len(report['records'])==1 and state['passed'] and len(state['cases'])==40
    assert state['script_sha256']==sha(REPOS/'kitaqfc/scripts/test-ppu-library.py')
    for row in state['cases']:
        assert row['passed'] and row['actual']==row['expected'] and row['ppu']==row['expected_ppu'] and not row['unsafe_ppu_writes']
    for name,digest in state['library_sha256'].items():assert sha(REPOS/'kitaqfc/lib'/name)==digest,name
    assert sha(REPOS/'kitaqfc/kitaqfc.exe')==state['compiler_sha256'] and sha(REPOS/'kurosaki/kurosaki.exe')==state['emulator_sha256']
    run=report['records'][0]
    assert run['passed'] and run['frames']==240 and run['geometry_pixels_checked']==34816
    assert not any(run[k] for k in ['label_pixel_mismatches','geometry_pixel_mismatches','geometry_color_mismatches','ppu_writes_while_rendering'])
    assert run['compiler_sha256']==state['compiler_sha256'] and run['emulator_sha256']==state['emulator_sha256'] and run['library_sha256']==state['library_sha256']
    for path,digest in {run['source']:run['source_sha256'],run['image']:run['image_sha256'],**run['support_sha256']}.items():assert sha(SITE/path)==digest,path
    return {key:dict(api=key.split(':')[1],kind='ppu-library',runs=[run]) for key in selected}

def verified_shadow_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']=='ppu-shadow-source-20260922'}
    if not selected:return {}
    assert len(selected)==2
    proof=verified_examples(contracts);assert len(proof)==4
    runs=next(iter(proof.values()))['runs']
    for c in selected.values():
        source=(SITE/c['example']['program']).read_text(encoding='utf-8')
        assert c['example']['code'] in source
    return {key:dict(api=key.split(':')[1],kind='ppu-shadow',runs=runs) for key in selected}
