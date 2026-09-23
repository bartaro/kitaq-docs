"""Bind wave examples to the exact tested sources and complete pixel matrix."""
from pathlib import Path
import hashlib,json
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']=='raster-wave-source-20260922'}
    if not selected:return {}
    assert len(selected)==6
    report=json.loads((SITE/'verification/api-raster-wave/results.json').read_text(encoding='utf-8'))
    assert report['passed'] and report['animation_passed']
    assert report['rom_sha256']==sha(SITE/'verification/api-raster-wave/raster_wave.gb')
    assert report['title_rom_sha256']==sha(SITE/'verification/api-raster-wave/raster_title_entry.gb')
    for field,path in [('compiler_sha256',REPOS/'kitaqgb/kitaqgb.exe'),('emulator_sha256',REPOS/'kokura/kokura-cli.exe'),('source_sha256',SITE/'samples/api-examples/gb/raster_wave.c'),('title_source_sha256',SITE/'samples/api-examples/gb/raster_title_entry.c'),('script_sha256',SITE/'tools/check_raster_wave.py')]:
        assert report[field]==sha(path),path
    for path,digest in report['library_sha256'].items():assert sha(REPOS/'kitaqgb/lib'/path)==digest,path
    for path,digest in report['support_sha256'].items():assert sha(SITE/'samples'/path)==digest,path
    # Image success does not establish divider, wrapping, or LCD-off behavior.
    edge=json.loads((SITE/'verification/api-raster-wave/state/results.json').read_text(encoding='utf-8'))
    assert edge['passed'] and edge['script_sha256']==sha(SITE/'tools/check_raster_wave_edges.py')
    assert sha(SITE/edge['source'])==edge['source_sha256']
    assert edge['compiler_sha256']==report['compiler_sha256'] and edge['emulator_sha256']==report['emulator_sha256']
    assert edge['library_sha256']==report['library_sha256'] and edge['support_sha256']==report['support_sha256']
    states=edge['records']
    assert len(states)==6 and {(r['variant'],r['mode']) for r in states}=={(v,m) for v in ['default','unoptimized','stack'] for m in ['dmg','cgb']}
    expected_state=[0,1,1,11,8,1,0,246,253,3,246,250,23,2,0,3,3,6,6,0xA55A]
    for r in states:
        assert r['passed'] and r['actual']==r['expected']==expected_state
        assert sha(SITE/r['rom'])==r['rom_sha256']
    expected={(m,f,'wave') for m in ['dmg','cgb'] for f in [60,61,68,76,84,92,100,108,116]}
    expected|={(m,f,'title') for m in ['dmg','cgb'] for f in [16,40,60,84,120,176]}
    rows=report['records']
    assert len(rows)==30 and {(r['mode'],r['frames'],r.get('lesson','wave')) for r in rows}==expected
    for r in rows:
        assert r['passed'] and r['pixel_mismatches']==0
        assert sha(SITE/r['image'])==r['image_sha256']
    output={}
    for key,c in selected.items():
        e=c['example'];title='title_entry' in e['program']
        assert e['code'] in (SITE/e['snippet_source']).read_text(encoding='utf-8')
        runs=[]
        for r in rows:
            if (r.get('lesson')=='title')!=title:continue
            if r['frames'] not in ([16,60,120] if title else [60]):continue
            runs.append(dict(r,source=e['program']))
        output[key]=dict(api=key.split(':')[1],kind='raster-wave',runs=runs)
    return output
