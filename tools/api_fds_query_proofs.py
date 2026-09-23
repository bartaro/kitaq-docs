"""Bind FDS query explanations to current compiled and executed lessons."""
from pathlib import Path
import hashlib,json,re
from api_physics_proofs import verify_row
from api_mapper_proofs import write_page
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
REVIEW='fds-query-source-20260923'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
    if not selected:return {}
    assert len(selected)==11
    for p,h in read(SITE/'tools/api_descriptions/fds_query_review_sources.json')['source_sha256'].items():assert sha(REPOS/p)==h
    report=read(SITE/'verification/api-fds-query/example/results.json')
    assert report['script_sha256']==sha(SITE/'tools/check_fds_query_examples.py')
    rows=report['records'];assert len(rows)==12
    modes=['available-fds','available-nrom','status-fds','metadata-fds','residency-fds','residency-fds-table-off']
    assert {r['mode'] for r in rows}=={m+'-'+v for m in modes for v in ['default','unoptimized']}
    expected=dict(zip(modes,[[1],[0],[1,0,0,2],[1,1,0,1,2,0,0,0,0],[1,1,0,2],[1,1,0,0]]))
    for r in rows:
        verify_row(r);assert r['actual']==expected[r['mode'].rsplit('-',1)[0]]
    result={}
    for key,c in selected.items():
        ex=c['example'];source=(SITE/ex['program']).read_text(encoding='utf-8')
        assert ex['code'] in source and re.search(r'\b'+key.split(':')[1]+r'\s*\(',ex['code'])
        runs=[r for r in rows if r['source']==ex['program'] and r['mode'].endswith('-default')]
        assert len(runs)==(2 if ex['program'].endswith(('fds_available.c','fds_residency.c')) else 1)
        result[key]=dict(api=key.split(':')[1],kind='fds-query',runs=runs)
    return result

def overview(text,language):
    import api_contracts as api
    messages,ui,contracts=api.load();proofs=verified_examples(contracts)
    selected={k:contracts[k] for k in proofs};api.attach_verified_images(selected,proofs)
    records={r['name']:r for r in read(SITE/'reference/fc-api.json')['records']}
    for name,start,end in reversed(api.CardRanges(text).ranges):
        key='fc:'+name
        if key not in selected:continue
        r=records[name];c=selected[key]
        fp=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest();assert fp==c['record_sha256']
        text=text[:start]+api.render(r,c,language,messages,ui)+text[end:]
    return text

if __name__=='__main__':
    import api_contracts as api
    for language in ['ja','en']:
        for name in ['kitaqfc','fc-library']:
            path=(SITE if language=='ja' else SITE/language)/(name+'.html');write_page(path,overview(path.read_text(encoding='utf-8'),language))
    contracts=api.load()[2];keys={p+':'+r['name'] for p in ['gb','fc'] for r in read(SITE/('reference/'+p+'-api.json'))['records']}
    assert set(contracts)<=keys
    report=dict(active_languages=['ja','en'],reviewed=len(contracts),remaining=len(keys-set(contracts)),missing=sorted(keys-set(contracts)))
    (SITE/'tools/api_descriptions/coverage.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('11 FDS query APIs rendered;',report['reviewed'],'reviewed;',report['remaining'],'remaining')
