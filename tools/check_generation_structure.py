"""Check complete API membership and navigable, illustrated teaching examples."""
import argparse
from collections import Counter
from html import escape
import json
from pathlib import Path
import re
from api_contracts import validate_rendered_volume
from sample_guides import GUIDES

SITE = Path(__file__).resolve().parents[1]


def check(site):
    manifest = json.loads((SITE/'samples/manifest.json').read_text(encoding='utf-8'))
    totals = dict(api_cards=0,sample_cards=0,gallery_entries=0,return_links=0)
    for language in ('ja','en'):
        folder = site if language == 'ja' else site/language
        for platform in ('gb','fc'):
            records = json.loads((SITE/'reference'/(platform+'-api.json')).read_text(encoding='utf-8'))['records']
            expected = {x['id'] for x in manifest if x['platform']==platform}
            for volume in ('kitaq'+platform,platform+'-library'):
                text = (folder/(volume+'.html')).read_text(encoding='utf-8')
                validate_rendered_volume(text,records,volume)
                ids = Counter(re.findall(r'\bid="([^"]+)"',text))
                assert not [k for k,v in ids.items() if v!=1],volume+' contains duplicate anchors'
                totals['api_cards'] += sum(k.startswith('api-') for k in ids)
                samples = {m[1]:m[0] for m in re.finditer(r'<details class="sample searchable" id="sample-([^"]+)">.*?</details>',text,re.S)}
                assert set(samples)==expected,(language,volume,'sample inventory')
                for name,block in samples.items():
                    title,purpose,processing,result = GUIDES[name][language]
                    assert all(escape(t) in block for t in [title,purpose,processing,result]),name
                    assert block.count('class="example-result"')==1,name
                    assert re.search(r'<figcaption>[^<]*'+re.escape(escape(result))+r'</figcaption>',block),name
                    assert 'verification/'+name+'.png' in block,name
                    assert 'verification.html#'+name in block,name
                    totals['sample_cards'] += 1
        text = (folder/'verification.html').read_text(encoding='utf-8')
        for item in manifest:
            name = item['id'];platform = item['platform']
            match = re.search(r'<section id="'+re.escape(name)+r'">.*?</section>',text,re.S)
            assert match,name+' absent from gallery'
            block = match[0]
            assert escape(GUIDES[name][language][3]) in block,name+' missing result explanation'
            assert 'verification/'+name+'.png' in block,name+' missing picture'
            for volume in ('kitaq'+platform,platform+'-library'):
                assert 'href="'+volume+'.html#sample-'+name+'"' in block,name+' missing return link'
                totals['return_links'] += 1
            totals['gallery_entries'] += 1
        assert not re.findall(r'href="[^"]*verification/[^"]*\.(?:txt|json|log|md)"',text),'Private evidence link'
    return dict(passed=True,**totals)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site',type=Path,default=SITE)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    result=check(args.site)
    if args.report:args.report.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))
