"""Bind VBlank queue cards to DMG/CGB state, bank and recorded-audio tests."""
from pathlib import Path
import hashlib,json,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']=='audio-queue-source-20260922'}
    if not selected:return {}
    assert len(selected)==3
    report=json.loads((SITE/'verification/api-audio-queue/results.json').read_text())
    assert report['passed'] and report['script_sha256']==sha(SITE/'tools/check_audio_vblank_queue.py')
    rows=report['records'];assert len(rows)==6 and {(r['variant'],r['mode']) for r in rows}=={(v,m) for v in ['default','unoptimized','stack'] for m in ['dmg','cgb']}
    for r in rows:
        verify_row(dict(r,platform='gb'));assert r['done']==[165] and sha(SITE/r['audio'])==r['audio_sha256']
        assert all(m['ac_rms']>100 for m in r['playing']) and all(m['difference_rms']<1 for m in r['stopped'])
    return {k:dict(api=k.split(':')[1],kind='audio-queue',runs=[r for r in rows if r['variant']=='default']) for k in selected}
