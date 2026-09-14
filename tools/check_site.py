"""Validate the portable manual's HTML, local links and recorded sample coverage."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,hashlib
from languages import LANGUAGES, HTML_LANG
S=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.ids=[];self.links=[];self.h1=0;self.lang=None;self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if tag=='html':self.lang=a.get('lang')
  for k in ('href','src'):
   if a.get(k):self.links.append(a[k])
def main():
 pages={p:Page(p.read_text(encoding='utf-8')) for p in S.rglob('*.html')}
 errors=[];n=0
 # Require every volume in every published language, including the root Japanese edition.
 names=('index','kitaqgb','gb-library','kokura','kitaqfc','fc-library','kurosaki','sarakura','verification','loop-engineering')
 editions={language: S if language=='ja' else S/language for language in LANGUAGES}
 for language,folder in editions.items():
  for name in names:
   path=folder/(name+'.html');doc=pages.get(path)
   if doc is None:errors.append('missing volume '+path.relative_to(S).as_posix())
   elif doc.h1!=1 or doc.lang!=HTML_LANG.get(language,language):errors.append(path.relative_to(S).as_posix()+': heading/lang')
 for p,doc in pages.items():
  if p.parent==S and (doc.h1!=1 or doc.lang!='ja'):errors.append(str(p.relative_to(S))+': heading/lang')
  duplicates=sorted({x for x in doc.ids if doc.ids.count(x)>1})
  if duplicates:errors.append({'page':p.relative_to(S).as_posix(),'duplicate_ids':duplicates})
  for url in doc.links:
   u=urlsplit(url)
   if u.scheme or u.netloc:continue
   target=(p.parent/unquote(u.path)).resolve() if u.path else p
   n+=1
   if not target.exists():errors.append({'page':p.relative_to(S).as_posix(),'missing':url})
   elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:errors.append({'page':p.relative_to(S).as_posix(),'missing_anchor':url})
 manifest=json.loads((S/'samples/manifest.json').read_text(encoding='utf-8'))
 results=json.loads((S/'verification/samples.json').read_text(encoding='utf-8'))
 result_by_id={r['id']:r for r in results}
 for sample in manifest:
  if not (S/'samples'/sample['file']).exists():errors.append('missing source '+sample['id'])
  if sample['id'] not in result_by_id:errors.append('missing build result '+sample['id'])
 records={p:json.loads((S/'reference'/(p+'-api.json')).read_text(encoding='utf-8'))['records'] for p in ['gb','fc']}
 total=sum(len(r) for r in records.values())
 for p,items in records.items():
  for r in items:
   page=S/((('kitaq'+p) if r['name'].startswith('__') else (p+'-library'))+'.html')
   if 'api-'+r['name'] not in pages[page].ids:errors.append('missing API '+p+':'+r['name'])
 report={'pages_per_language':{HTML_LANG.get(language,language):sum(p.parent==folder for p in pages) for language,folder in editions.items()},'other_html_pages':sum(p.parent not in editions.values() for p in pages),'local_links_checked':n,'api_entries':total,'sample_programs':len(manifest),'historical_successful_builds':sum(r.get('build_exit')==0 for r in results),'historical_emulator_runs':sum(r.get('runtime')=='executed' for r in results),'errors':errors,'status':'passed' if not errors else 'failed'}
 (S/'verification/site_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=True))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
