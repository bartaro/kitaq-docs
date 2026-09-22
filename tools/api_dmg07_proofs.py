"""Bind the 25 adapter APIs to linked execution and separate port-injection tests."""
from pathlib import Path
import hashlib,json,re
from api_physics_proofs import verify_row
from check_dmg07_examples import expectation

SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def verified_examples(contracts):
    selected={k:c for k,c in contracts.items() if c['review']=='dmg07-source-20260922'}
    if not selected:return {}
    if len(selected)!=25:raise ValueError('DMG07 requires all 25 API descriptions')
    author=SITE/'tools/api_descriptions';folder=SITE/'verification/api-dmg07'
    for path,digest in read(author/'dmg07_review_sources.json')['source_sha256'].items():
        if sha(REPOS/path)!=digest:raise ValueError('Reviewed DMG07 source changed: '+path)
    report=read(folder/'results.json');runs=report['records']
    matrix={(mode,lesson,slot) for mode in ['dmg','cgb'] for lesson in ['exchange','absent','restart','overflow'] for slot in ([1] if lesson=='absent' else range(1,5))}
    if len(runs)!=26 or {(r['mode'],r['lesson'],r['slot']) for r in runs}!=matrix:raise ValueError('DMG07 teaching matrix incomplete')
    if report['script_sha256']!=sha(SITE/'tools/check_dmg07_examples.py'):raise ValueError('DMG07 teaching checker changed')
    edges=read(folder/'edge_checks.json')
    if len(edges['records'])!=16 or edges['script_sha256']!=sha(SITE/'tools/check_dmg07_edges.py'):raise ValueError('DMG07 boundary matrix incomplete')
    if len({(r['mode'],r['group']) for r in edges['records']})!=16:raise ValueError('Duplicate DMG07 boundary runs')
    for row in runs+edges['records']:verify_row(row)
    for row in runs:
        want=expectation(row['lesson'],row['slot']);want += [0]*(79-len(want))+[0xA55A]
        if row['actual']!=want or row['linked_actual']!=want or row['expected']!=want or row['pixel_mismatches']!=0:raise ValueError('DMG07 data or display differs')
        if (row['colored_pixels']>0)!=(row['mode']=='cgb'):raise ValueError('DMG07 color-mode evidence differs')
    links=report['links']
    if len(links)!=6 or {(r['mode'],r['lesson']) for r in links}!={(m,l) for m in ['dmg','cgb'] for l in ['exchange','restart','overflow']}:raise ValueError('DMG07 linked runs missing')
    for link in links:
        s=link['summary']
        if s['halted_on_unsupported_opcode'] or s['stopped_session'] is not None or s['session_count']!=4 or s['frame_advances']!=[90]*4 or s['exchange_count']<16:raise ValueError('DMG07 linked execution incomplete')
    output={}
    for key,c in selected.items():
        example=c['example'];name=key.split(':')[1];program=(SITE/example['program']).read_text(encoding='utf-8')
        snippet_file=SITE/example.get('snippet_source',example['program']);snippet=snippet_file.read_text(encoding='utf-8')
        if example['code'] not in snippet or not re.search(r'\b'+re.escape(name)+r'\s*\(',snippet):raise ValueError('DMG07 snippet/call missing: '+key)
        if 'snippet_source' in example and ('gb_dmg07_example.h' not in program or 'd_poll(' not in program):raise ValueError('DMG07 helper not used')
        matching=[r for r in runs if r['source']==example['program'] and r['slot']==example.get('player',1)]
        if len(matching)!=2:raise ValueError('Missing DMG07 player evidence: '+key)
        output[key]={'api':name,'kind':'dmg07','runs':matching}
    return output
