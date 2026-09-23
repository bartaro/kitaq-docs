"""Require matching numeric and visible evidence for the six FC bullet APIs."""
from pathlib import Path
import hashlib,json,re
from api_physics_proofs import verify_row
SITE=Path(__file__).resolve().parents[1];ROOT=SITE.parents[1];REPOS=ROOT/'publish/github_20260912'
REVIEW='fc-danmaku-source-20260922'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def verified_examples(contracts):
    selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
    if not selected:return {}
    assert len(selected)==6
    reviewed=json.loads((SITE/'tools/api_descriptions/fc_danmaku_review_sources.json').read_text())
    for path,digest in reviewed['source_sha256'].items():assert sha(REPOS/path)==digest,path
    report=json.loads((SITE/'verification/api-fc-danmaku/results.json').read_text())
    assert report['script_sha256']==sha(SITE/'tools/check_fc_danmaku_visual.py')
    runs=report['records'];assert len(runs)==4 and {r['mode'] for r in runs}=={'default','O0','no-inline','fastcall'}
    for row in runs:
        verify_row(row)
        assert row['oam_matches_expected'] and not row['unsafe_vram_writes'] and not row['unsafe_address_writes']
    folder=ROOT/'publish/library_docs_20260914/fc-effects/danmaku/state'
    state=json.loads((folder/'report.json').read_text())
    assert state['passed'] and len(state['records'])==4
    assert {r['variant'] for r in state['records']}=={'default','unoptimized','no-inline','fastcall'}
    assert state['danmaku_checker_sha256']==sha(SITE/'tools/check_fc_danmaku.py')
    assert state['script_sha256']==sha(SITE/'tools/check_compiler_parity.py')
    assert state['fixtures_sha256']==sha(folder.parent/'fixtures.json')
    for path,digest in state['library_sha256'].items():assert sha(REPOS/path)==digest,path
    for row in state['records']:
        assert row['passed'] and row['actual']==row['expected']
        case=folder/'fc'/row['name']/row['variant']
        assert sha(case/'case.c')==row['source_sha256'] and sha(case/'case.nes')==row['rom_sha256']
        assert sha(REPOS/'kitaqfc/kitaqfc.exe')==row['compiler_sha256'] and sha(REPOS/'kurosaki/kurosaki.exe')==row['emulator_sha256']
    result={}
    for key,contract in selected.items():
        source=(SITE/contract['example']['program']).read_text(encoding='utf-8');name=key.split(':')[1]
        assert re.search(r'\b'+name+r'\s*\(',source) and contract['example']['code'] in source
        result[key]={'api':name,'kind':'fc-danmaku','runs':[r for r in runs if r['mode']=='default']}
    return result

def overview(text,language):
    import api_contracts
    messages,ui,contracts=api_contracts.load();selected={k:v for k,v in contracts.items() if v['review']==REVIEW}
    api_contracts.attach_verified_images(selected,verified_examples(selected))
    records={r['name']:r for r in json.loads((SITE/'reference/fc-api.json').read_text(encoding='utf-8'))['records']}
    modules=json.loads((SITE/'tools/api_descriptions/fc_danmaku_modules.json').read_text())
    title='64発の弾プール' if language=='ja' else 'A 64-bullet pool'
    index=api_contracts.ORDER.index(language)
    block='<!-- fc-danmaku:start --><section data-module-contract="'+REVIEW+'"><h3 id="module-danmaku">danmaku — '+title+'</h3>'
    block+=''.join('<p>'+api_contracts.inline(messages[k][index])+'</p>' for k in modules['fc:danmaku'])
    for key,contract in selected.items():
        record=records[key.split(':')[1]]
        fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
        assert fingerprint==contract['record_sha256']
        block+=api_contracts.render(record,contract,language,messages,ui)
    block+='</section><!-- fc-danmaku:end -->'
    text=re.sub(r'<!-- fc-danmaku:start -->.*?<!-- fc-danmaku:end -->','',text,flags=re.S)
    anchor='<h3 id="module-debug">';assert text.count(anchor)==1
    from api_fc_wireframe_proofs import ensure_header
    return ensure_header(text.replace(anchor,block+anchor))

def main():
    for language in ['ja','en']:
        file=(SITE if language=='ja' else SITE/'en')/'fc-library.html'
        file.write_text(overview(file.read_text(encoding='utf-8'),language),encoding='utf-8')
    print('6 individual FC danmaku entries with captured color images in JA/EN')

if __name__=='__main__':main()
