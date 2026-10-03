"""Maintain the authored FC distribution notes in all nine manual editions."""
from pathlib import Path
import html,json,re
SITE=Path(__file__).resolve().parents[1]
SECTION='fc-current-20261004'
LANGS=['ja','en','ko','zh-CN','zh-TW','fr','es','de','pt']
BUILD='.\\kitaqfc\\scripts\\build.ps1\n.\\kitaqfc\\kitaqfc.exe --help'

def texts():
    data=json.loads((SITE/'tools/fc_current_texts.json').read_text(encoding='utf-8'))
    assert set(data)==set(LANGS)
    assert all(set(v)==set(data['en']) and all(s.strip() for s in v.values()) for v in data.values())
    return data

def render(language,book):
    t=texts()[language]
    proof=('' if language=='ja'else '../')+'verification/'+SECTION+'/report.json'
    keys=['compiler','verification'] if book=='kitaqfc'else ['library','verification']
    parts=[f'<section id="{SECTION}"><h2 id="{SECTION}-heading">{html.escape(t["title"])}</h2>']
    parts.extend('<p>'+html.escape(t[k])+'</p>' for k in keys)
    if book=='kitaqfc':parts.append('<pre><code>'+html.escape(BUILD)+'</code></pre>')
    parts.append('<p><a href="'+proof+'">'+html.escape(t['proof'])+'</a></p></section>')
    return ''.join(parts)

def publish(language):
    root=SITE if language=='ja'else SITE/language
    for book in ['kitaqfc','fc-library']:
        p=root/(book+'.html');s=p.read_bytes().decode('utf-8')
        s=re.sub(r'<section id="'+SECTION+r'".*?</section>','',s,flags=re.S)
        s=re.sub(r'<a href="#'+SECTION+r'-heading"[^>]*>.*?</a>','',s,flags=re.S)
        # Commands in these manuals run from the parent of the sibling repositories.
        s=s.replace('.\\kitaqfc\\bin\\Release\\kitaqfc.exe','.\\kitaqfc\\kitaqfc.exe')
        start=s.index('<main');position=s.index('<h2',start)
        s=s[:position]+render(language,book)+s[position:]
        nav='<a href="#'+SECTION+'-heading">'+html.escape(texts()[language]['title'])+'</a>'
        s=re.sub(r'<nav\b(?=[^>]*\bclass="toc")[^>]*>',lambda m:m[0]+nav,s,count=1)
        p.write_bytes(s.encode('utf-8'))

def readme(language,source,book):
    t=texts()[language]
    marker=SECTION+':'+language
    source=re.sub(r'<!-- '+marker+r':start -->.*?<!-- '+marker+r':end -->\s*','',source,flags=re.S)
    keys=['compiler','verification'] if book=='kitaqfc'else ['library','verification']
    body=['<!-- '+marker+':start -->','### '+t['title'],'']
    body.extend(t[k]+'\n' for k in keys)
    if book=='kitaqfc':body.extend(['```powershell',BUILD,'```',''])
    prefix=''if language=='ja'else language+'/'
    body.extend(['['+t['proof']+'](https://bartaro.github.io/kitaq-docs/'+prefix+book+'.html#'+SECTION+'-heading)','<!-- '+marker+':end -->',''])
    anchor='<!-- development-prompt:'+language+':start -->' if book=='kitaqfc'else '<!-- readme-language-links:end -->'
    if anchor in source:
        at=source.index(anchor)
        if book=='fc-library':at+=len(anchor)
    else:at=source.find('\n')
    return source[:at]+'\n\n'+'\n'.join(body)+source[at:]

if __name__=='__main__':
    for language in LANGS:publish(language)
