"""Reject missing, duplicate and unreviewed API cards in actual manual volumes."""
from pathlib import Path
import argparse,json
from api_contracts import CardRanges,validate_rendered_volume

SITE=Path(__file__).resolve().parents[1]


def check(site):
    accepted=0;rejected=[]
    for language in ('ja','en'):
        for platform in ('gb','fc'):
            records=json.loads((SITE/'reference'/(platform+'-api.json')).read_text(encoding='utf-8'))['records']
            for volume in ('kitaq'+platform,platform+'-library'):
                text=(site/('' if language=='ja' else language)/(volume+'.html')).read_text(encoding='utf-8')
                validate_rendered_volume(text,records,volume);accepted+=1
                name,start,end=CardRanges(text).ranges[0]
                card=text[start:end]
                corruptions={
                    'missing':text[:start]+text[end:],
                    'duplicate':text[:end]+card+text[end:],
                    'unreviewed':text[:start]+card.replace('data-api-contract=','data-unreviewed=',1)+text[end:],
                }
                for kind,value in corruptions.items():
                    try:validate_rendered_volume(value,records,volume)
                    except ValueError:rejected.append(dict(language=language,volume=volume,kind=kind,api=name))
                    else:raise AssertionError('Accepted '+kind+' API in '+volume)
    return dict(passed=True,accepted_volumes=accepted,rejected=rejected)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site',type=Path,default=SITE)
    parser.add_argument('--report',type=Path)
    args=parser.parse_args();result=check(args.site)
    if args.report:args.report.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('Accepted',result['accepted_volumes'],'volumes; rejected',len(result['rejected']),'invalid documents.')
