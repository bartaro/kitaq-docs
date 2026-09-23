"""Bind seven load/call lessons to current CPU and full-pixel evidence."""
from pathlib import Path
import hashlib,html,json,re
from api_physics_proofs import verify_row
from api_mapper_proofs import write_page
SITE=Path(__file__).resolve().parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.is_dir():REPOS=SITE.parent
REVIEW='fds-load-source-20260923'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
    if not selected:return {}
    assert len(selected)==7
    for p,h in read(SITE/'tools/api_descriptions/fds_load_review_sources.json')['source_sha256'].items():assert sha(REPOS/p)==h
    report=read(SITE/'verification/api-fds-load/example/results.json')
    assert report['script_sha256']==sha(SITE/'tools/check_fds_load_examples.py')
    rows=report['records'];assert len(rows)==10
    values=dict(overlay_call=[42,1,1,2,1],farcall=[42,1,1,2,1],call_alias=[42,1,1,2,1],
                bank_load=[0,2,0,11,44,0,1,0,255,255],raw_overlay=[0,255,0,11,44,0,1])
    assert {r['mode'] for r in rows}=={m+'-'+v for m in values for v in ['default','unoptimized']}
    for r in rows:
        verify_row(r);assert r['actual']==values[r['mode'].rsplit('-',1)[0]]+[165,0]
        assert r['load_ids']==r['expected_load_ids']==[32,0]
    result={}
    for key,c in selected.items():
        ex=c['example'];source=(SITE/ex['program']).read_text(encoding='utf-8')
        assert ex['code'] in source and re.search(r'\b'+key.split(':')[1]+r'\s*\(',ex['code'])
        runs=[r for r in rows if r['source']==ex['program'] and r['mode'].endswith('-default')]
        assert len(runs)==1
        result[key]=dict(api=key.split(':')[1],kind='fds-load',runs=runs)
    return result
def overview(text,language):
    import api_contracts as api
    messages,ui,contracts=api.load();proofs=verified_examples(contracts)
    selected={k:contracts[k] for k in proofs};api.attach_verified_images(selected,proofs)
    # Keep complete header listings in the library volume in sync as well.
    for name,guard in [('fds_overlay.h','FDS_OVERLAY_H'),('intrinsics.h','INTRINSICS_H')]:
        source=(REPOS/'kitaqfc/lib'/name).read_text(encoding='utf-8').strip()
        def replace_header(match):
            content=html.unescape(match.group(1)).strip()
            if content.startswith('#ifndef '+guard+'\n'):
                return '<pre><code>'+html.escape(source)+'</code></pre>'
            return match.group(0)
        text=re.sub(r'<pre><code>(.*?)</code></pre>',replace_header,text,flags=re.S)
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
    print('Seven FDS load/call APIs rendered;',report['reviewed'],'reviewed;',report['remaining'],'remaining')
