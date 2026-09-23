"""Bind each documented header alias to its calls, target ROM and runtime screen."""
from pathlib import Path
import hashlib,json,re
from check_header_aliases import CASE_FILE,VARIANTS,dependencies
SITE=Path(__file__).resolve().parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
REVIEW='header-alias-source-20260923'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def verified_examples(contracts):
    selected={k:c for k,c in contracts.items() if c['review']==REVIEW}
    if not selected:return {}
    cases=read(CASE_FILE)
    assert set(selected)=={c['platform']+':'+n for c in cases.values() for n in c['aliases']}
    report=read(SITE/'verification/api-header-aliases/results.json')
    assert report['passed'] and len(report['records'])==22
    assert sha(SITE/'tools/check_header_aliases.py')==report['checker_sha256']
    assert sha(CASE_FILE)==report['cases_sha256']
    specs_path=SITE/'tools/api_descriptions/batch100_examples.json'
    assert sha(specs_path)==report['service_specs_sha256']
    specs={s['platform']:s for s in read(specs_path) if s['group']=='services'}
    site_sources={};repo_sources={};tool_hashes={};wanted=set()
    for key,case in cases.items():
        platform=case['platform'];lib=REPOS/('kitaq'+platform)/'lib'
        for p in [lib.parent/('kitaq'+platform+'.exe'),
                  REPOS/('kokura/kokura-cli.exe' if platform=='gb' else 'kurosaki/kurosaki.exe'),
                  lib.parent/('kitaq'+platform)/'CodeGenerator.cs']:
            tool_hashes[p.relative_to(REPOS).as_posix()]=sha(p)
        libraries=[lib/'input.c'] if case['group']=='input' else [lib/'runtime.c'] if platform=='fc' else []
        a,b=dependencies([SITE/case['source'],SITE/case['canonical'],*libraries]+([SITE/'samples/font.chr'] if platform=='fc' else []),lib)
        site_sources.update(a);repo_sources.update(b)
        for variant,flags in VARIANTS[platform]:
            if key=='gb-system' and variant=='stack':continue
            wanted.update((key,variant,mode) for mode in (['dmg','cgb'] if platform=='gb' else ['nrom']))
    assert report['site_sources']==site_sources and report['repo_sources']==repo_sources and report['tools']==tool_hashes
    assert {(r['case'],r['variant'],r['mode']) for r in report['records']}==wanted
    rejected=report['rejected'];assert len(rejected)==1
    reject=rejected[0]
    assert reject['passed'] and reject['case']=='gb-system' and reject['variant']=='stack'
    assert len(reject['diagnostics'])==2
    assert {d['source'] for d in reject['diagnostics']}=={cases['gb-system'][k] for k in ['source','canonical']}
    assert len({d['count'] for d in reject['diagnostics']})==1
    for d in reject['diagnostics']:
        assert d['count']>0 and d['diagnostic']=='Indirect calls are not supported with --abi=stack yet'
        assert sha(SITE/d['source'])==d['source_sha256']
    for r in report['records']:
        case=cases[r['case']];assert r['platform']==case['platform'] and r['source']==case['source']
        assert r['passed'] and r['frames_requested']==180 and r['pixel_mismatches']==0
        assert r['rom_sha256']==r['canonical_rom_sha256']
        for key in ['source','rom','image']:assert sha(SITE/r[key])==r[key+'_sha256']
        if case['group']=='input':
            assert r['actual']==r['expected']==[]
            values={y:v for x,y,v in r['expected_labels'] if x==16}
            assert values=={2:'001',3:'001',4:'001',5:'016',6:'040',7:'001',8:'005',9:'001',10:'000',11:'016',13:'000'}
        else:
            expected=specs[r['platform']]['expected']
            expected=expected+[0]*(79-len(expected))+[0xA55A]
            assert r['actual']==r['expected']==expected and len(expected)==80
    result={}
    # Extraction markers can be nested around input observations; displayed
    # fragments omit those comments but must retain every actual code line.
    normalize=lambda s:'\n'.join(line.strip() for line in s.strip().splitlines()
                              if not re.fullmatch(r'\s*// example:\w+:(?:start|end)\s*',line))
    for key,case in cases.items():
        source=(SITE/case['source']).read_text(encoding='utf-8')
        for alias,target in case['aliases'].items():
            api_key=case['platform']+':'+alias;contract=selected[api_key];ex=contract['example']
            assert ex['program']==case['source'] and ex['build']==case['build']
            assert re.search(r'\b'+alias+r'\s*\(',ex['code'])
            assert normalize(ex['code']) in normalize(source),(api_key,ex['code'])
            runs=[r for r in report['records'] if r['case']==key and r['variant']=='default']
            assert len(runs)==(2 if case['platform']=='gb' else 1)
            result[api_key]=dict(api=alias,kind='header-alias',runs=runs)
    return result

def ensure_cards(text,platform):
    """Place missing alias cards next to their target in an existing edition."""
    from api_contracts import CardRanges
    cases=read(CASE_FILE)
    aliases={n:t for c in cases.values() if c['platform']==platform for n,t in c['aliases'].items()}
    for alias,target in aliases.items():
        ranges=CardRanges(text).ranges
        if any(n==alias for n,a,b in ranges):continue
        positions=[b for n,a,b in ranges if n==target];assert len(positions)==1,(alias,target)
        pos=positions[0]
        card='<details class="api searchable" id="api-'+alias+'"><summary><code>'+alias+'</code></summary></details>'
        text=text[:pos]+card+text[pos:]
    return text

if __name__=='__main__':
    from api_contracts import load
    assert len(verified_examples(load()[2]))==22
    print('22 aliases: 22 runtime variants, exact target ROM equality and stack diagnostic verified.')
