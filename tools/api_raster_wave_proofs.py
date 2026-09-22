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
    for field,path in [('compiler_sha256',REPOS/'kitaqgb/kitaqgb.exe'),('emulator_sha256',REPOS/'kokura/kokura-cli.exe'),('source_sha256',SITE/'samples/api-examples/gb/raster_wave.c'),('title_source_sha256',SITE/'samples/api-examples/gb/raster_title_entry.c'),('script_sha256',SITE/'tools/check_raster_wave.py')]:
        assert report[field]==sha(path),path
    for path,digest in report['library_sha256'].items():assert sha(REPOS/'kitaqgb/lib'/path)==digest,path
    for path,digest in report['support_sha256'].items():assert sha(SITE/'samples'/path)==digest,path
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
