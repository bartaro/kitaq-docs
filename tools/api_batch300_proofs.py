"""Reject incomplete, stale or mismatched evidence for the 100-item batch."""
from pathlib import Path
import json,hashlib,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def verified_examples(contracts):
    selected={k:c for k,c in contracts.items() if c['review']=='batch300-source-20260916'}
    if not selected:return {}
    if len(selected)!=100:raise ValueError('Third batch requires exactly 100 contracts')
    author=SITE/'tools/api_descriptions';folder=SITE/'verification/api-batch300'
    for path,digest in read(author/'batch300_review_sources.json')['source_sha256'].items():
        if sha(REPOS/path)!=digest:raise ValueError('Third-batch reviewed source changed: '+path)
    specs=read(author/'batch300_examples.json');report=read(folder/'results.json');runs=report['records']
    expected={(s['source'],m) for s in specs for m in s.get('modes',['dmg','cgb'] if s['platform']=='gb' else ['nrom'])}
    if len(runs)!=22 or {(r['source'],r['mode']) for r in runs}!=expected:raise ValueError('Third-batch runtime matrix incomplete')
    if report['checker_sha256']!=sha(SITE/'tools/check_batch300.py'):raise ValueError('Third-batch checker changed')
    edges=read(folder/'edge_checks.json')
    if len(edges['records'])!=20 or edges['script_sha256']!=sha(SITE/'tools/check_batch300_edges.py'):raise ValueError('Third-batch boundaries incomplete')
    for row in runs+edges['records']:verify_row(row)
    for row in runs:
        spec=next(s for s in specs if s['source']==row['source'])
        if row['expected']!=spec['expected']+[0]*(79-len(spec['expected']))+[0xA55A]:raise ValueError('Third-batch expectation changed')
        if spec.get('visual') or spec.get('grid_check'):
            if row.get('geometry_pixel_mismatches',-1)!=0 or row.get('color_mismatches',-1)!=0:raise ValueError('Third-batch geometry/color mismatch')
    output={}
    for key,c in selected.items():
        name=key.split(':')[1];program=c['example']['program'];text=(SITE/program).read_text(encoding='utf-8')
        if not re.search(r'\b'+re.escape(name)+r'\s*\(',text):raise ValueError('Example does not call '+name)
        found=[r for r in runs if r['source']==program]
        if not found:raise ValueError('Missing sample for '+key)
        output[key]={'api':name,'kind':'batch300','runs':found}
    return output
