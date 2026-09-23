"""Require exact source bindings, complete link runs and independent edge checks."""
from pathlib import Path
import hashlib,json,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def verified_examples(contracts):
    selected={k:c for k,c in contracts.items() if c['review']=='link-source-20260917'}
    if not selected:return {}
    if len(selected)!=37:raise ValueError('Link review requires all 37 declarations')
    author=SITE/'tools/api_descriptions';folder=SITE/'verification/api-link'
    for path,digest in read(author/'link_review_sources.json')['source_sha256'].items():
        if sha(REPOS/path)!=digest:raise ValueError('Reviewed link source changed: '+path)
    specs=read(author/'link_examples.json');report=read(folder/'results.json');runs=report['records']
    matrix={(s['source'],m) for s in specs for m in ['dmg','cgb']}
    if len(runs)!=20 or {(r['source'],r['mode']) for r in runs}!=matrix:raise ValueError('Link runtime matrix incomplete')
    if report['script_sha256']!=sha(SITE/'tools/check_link_examples.py') or report['manifest_sha256']!=sha(author/'link_examples.json'):raise ValueError('Link checker/expectations changed')
    edges=read(folder/'edge_checks.json')
    if len(edges['records'])!=14 or edges['script_sha256']!=sha(SITE/'tools/check_link_edges.py'):raise ValueError('Link boundaries incomplete')
    edge_groups={'topology-validation','send-validation-copy','parser-checksum-length','maximum-parser-mailbox','nak-retry-limit','ack-deadline-90','external-clock-stall'}
    if {(r['mode'],r['group']) for r in edges['records']}!={(m,g) for m in ['dmg','cgb'] for g in edge_groups}:raise ValueError('Link boundary variants missing or duplicated')
    for row in runs+edges['records']:verify_row(row)
    for row in runs:
        spec=next(s for s in specs if s['source']==row['source'])
        expected=spec['expected']+[0]*(79-len(spec['expected']))+[0xA55A]
        if row['expected']!=expected or row['linked_actual']!=expected or row['pixel_mismatches']!=0:raise ValueError('Link RAM or screen mismatch')
    links=report['links']
    if len(links)!=6 or {(r['mode'],r['group']) for r in links}!={(m,g) for m in ['dmg','cgb'] for g in ['raw','packet','four']}:raise ValueError('Missing linked sessions')
    for link in links:
        s=link['summary'];count=4 if link['group']=='four' else 2
        if s['halted_on_unsupported_opcode'] or s['stopped_session'] is not None or s['session_count']!=count or s['frame_advances']!=[360]*count:raise ValueError('Incomplete linked session')
        if s['exchange_count']<({'raw':2,'packet':8,'four':27}[link['group']]):raise ValueError('Missing serial exchanges')
        if count==4 and not (s['dynamic_peer_selection_observed'] and s['peer_switch_count']>=3):raise ValueError('Four-peer routing not exercised')
    output={}
    for key,c in selected.items():
        examples=[c['example']]+c['example'].get('additional',[]);programs={e['program'] for e in examples};name=key.split(':')[1]
        for example in examples:
            text=(SITE/example['program']).read_text(encoding='utf-8')
            if example['code'] not in text:raise ValueError('Snippet mismatch: '+key)
        if not re.search(r'\b'+re.escape(name)+r'\s*\(',(SITE/c['example']['program']).read_text(encoding='utf-8')):raise ValueError('Missing API call: '+key)
        output[key]={'api':name,'kind':'link','runs':[r for r in runs if r['source'] in programs]}
    return output
