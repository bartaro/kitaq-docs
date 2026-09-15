"""Language order and same-volume links for this nine-language publication."""
import html
import re
from publication_languages import ORDER, VISIBLE_LANGUAGES
from urllib.parse import urlsplit, unquote

LANGUAGES = {
    'en': 'English', 'ja': '日本語', 'ko': '한국어', 'zh-CN': '简体中文',
    'zh-TW': '繁體中文', 'es': 'Español', 'pt': 'Português (Brasil)',
    'fr': 'Français', 'de': 'Deutsch',
}
HTML_LANG = {'pt': 'pt-BR'}

def language_nav(key, current, nav_label='Languages'):
    """Link to the same volume in each published language, preserving root Japanese paths."""
    links=[]
    for language,label in LANGUAGES.items():
        if language not in VISIBLE_LANGUAGES:
            continue
        prefix='../' if current!='ja' else ''
        folder='' if language=='ja' else language+'/'
        href=prefix+folder+key+'.html'
        code=HTML_LANG.get(language,language)
        selected=' aria-current="page"' if current==language else ''
        links.append(f'<a href="{html.escape(href,quote=True)}" lang="{code}" hreflang="{code}"{selected}>{label}</a>')
    return '<nav class="languages" aria-label="'+html.escape(nav_label,quote=True)+'">'+' '.join(links)+'</nav>'


def refresh_language_navigation(path, current):
    """Change navigation only; preserve the translated body of paused editions."""
    original=path.read_bytes();text=original.decode('utf-8')
    pattern=r'<nav\b[^>]*class="languages"[^>]*>.*?</nav>'
    def replace(match):
        label=re.search(r'aria-label="([^"]*)"',match[0])
        return language_nav(path.stem,current,html.unescape(label[1]) if label else 'Languages')
    updated=re.sub(pattern,replace,text,flags=re.S)
    if updated!=text:path.write_bytes(updated.encode('utf-8'))
    return updated!=text


def check_readme_language_links(path):
    """Reject stale README navigation before it can restore hidden editions."""
    hidden=set(ORDER)-set(VISIBLE_LANGUAGES)
    hidden_readmes={'README.'+HTML_LANG.get(code,code)+'.md' for code in hidden}
    text=path.read_text(encoding='utf-8')
    urls=re.findall(r'\]\(([^\s)]+)',text)+re.findall(r'href="([^"]+)"',text)
    for url in urls:
        parsed=urlsplit(html.unescape(url));parts=unquote(parsed.path).split('/')
        if (not parsed.netloc and set(parts)&hidden_readmes) or (parsed.netloc=='bartaro.github.io' and parts[:2]==['','kitaq-docs'] and set(parts[2:])&hidden):
            raise ValueError('README links to a hidden language edition: '+str(path)+' -> '+url)
