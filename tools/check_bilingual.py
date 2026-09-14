"""Check both complete editions, shared examples, anchors and English UI/prose."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json,re
from datetime import date
from languages import LANGUAGES
S=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,p):
        super().__init__();self.ids=[];self.links=[];self.lang=None;self.h1=0;self.pre=0;self.prose=[]
        self.feed(p.read_text(encoding='utf-8'))
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if t=='html':self.lang=a.get('lang')
        if t=='h1':self.h1+=1
        if t=='pre':self.pre+=1
        if 'id' in a:self.ids.append(a['id'])
        self.links.extend(a[k] for k in ('href','src') if a.get(k))
    def handle_endtag(self,t):
        if t=='pre':self.pre-=1
    def handle_data(self,d):
        # Language selectors deliberately use each language's own spelling.
        if not self.pre and re.search('[\u3040-\u30ff\u3400-\u9fff]',d) and d.strip() not in (*LANGUAGES.values(), '北九 (キタキュー, Kitakyū)'):self.prose.append(d)
def main():
    pages={p.resolve():Page(p) for p in S.rglob('*.html')};errors=[];links=0
    names=['index','kitaqgb','gb-library','kokura','kitaqfc','fc-library','kurosaki','sarakura','verification','loop-engineering']
    for n in names:
        jp=pages.get((S/(n+'.html')).resolve());en=pages.get((S/'en'/(n+'.html')).resolve())
        if not jp or not en:errors.append('Missing edition: '+n);continue
        if jp.lang!='ja' or en.lang!='en' or jp.h1!=1 or en.h1!=1:errors.append('Heading/language: '+n)
        for prefix in ('api-','sample-','cmd-','result-'):
            if {i for i in jp.ids if i.startswith(prefix)}!={i for i in en.ids if i.startswith(prefix)}:errors.append('Coverage mismatch: '+n+' '+prefix)
        if en.prose:errors.append({'page':'en/'+n+'.html','untranslated_prose':en.prose[:20]})
        if 'en/'+n+'.html' not in jp.links or '../'+n+'.html' not in en.links:errors.append('Missing language switch: '+n)
    for p,doc in pages.items():
        if len(doc.ids)!=len(set(doc.ids)):errors.append('Duplicate IDs: '+str(p.relative_to(S)))
        for link in doc.links:
            u=urlsplit(link)
            if u.scheme or u.netloc:continue
            target=(p.parent/unquote(u.path)).resolve() if u.path else p
            links+=1
            if not target.exists():errors.append({'page':str(p.relative_to(S)),'missing':link})
            elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:errors.append({'page':str(p.relative_to(S)),'missing_anchor':link})
    api=sum(len(json.loads((S/'reference'/(p+'-api.json')).read_text(encoding='utf-8'))['records']) for p in ('gb','fc'))
    manifest=json.loads((S/'samples/manifest.json').read_text(encoding='utf-8'))
    report={'checked_on':date.today().isoformat(),'japanese_pages':len(names),'english_pages':len(names),'api_entries_per_language':api,'shared_complete_samples':len(manifest),'local_links_checked':links,'status':'passed' if not errors else 'failed','errors':errors,'original_source_and_recorded_output':'Preserved verbatim, including original-language comments.'}
    (S/'verification/bilingual_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
