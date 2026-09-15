"""Bind wireframe cards only to current, pixel-exact executable examples."""
from pathlib import Path
import hashlib,json,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']=='wireframe-source-20260915'}
    if not selected:return {}
    if len(selected)!=124:raise ValueError('Wireframe review requires 124 API contracts')
    review=read(SITE/'tools/api_descriptions/wireframe_review_sources.json')
    for path,digest in review['source_sha256'].items():
        if sha(REPOS/path)!=digest:raise ValueError('Wireframe source changed: '+path)
    manifest=SITE/'tools/api_descriptions/wireframe_examples.json';specs=read(manifest)
    report=read(SITE/'verification/api-wireframe/results.json')
    if report['script_sha256']!=sha(SITE/'tools/check_wireframe_examples.py'):raise ValueError('Wireframe checker changed')
    if report['manifest_sha256']!=sha(manifest):raise ValueError('Wireframe expectations changed')
    expected={(name,mode) for name,spec in specs.items() for mode in spec['modes']}
    runs=report['records']
    if len(runs)!=len(expected) or {(r['group'],r['mode']) for r in runs}!=expected:raise ValueError('Wireframe execution matrix incomplete')
    for row in runs:verify_row(row)
    result={}
    for key,contract in selected.items():
        examples=[contract['example']]+contract['example'].get('additional',[])
        selected_runs=[]
        for example in examples:
            name=key.split(':',1)[1];program=SITE/example['program']
            code=program.read_text(encoding='utf-8')
            if '#include "wire_cgb_example.h"' in code:code+=(SITE/'samples/wire_cgb_example.h').read_text(encoding='utf-8')
            if not re.search(r'\b'+re.escape(name)+r'\s*\(',code):raise ValueError('Wireframe example does not call API: '+key)
            found=[r for r in runs if r['source']==example['program']]
            if not found:raise ValueError('Wireframe sample not executed: '+key)
            selected_runs+=found
        result[key]={'api':key.split(':',1)[1],'kind':'wireframe','runs':selected_runs}
    return result
