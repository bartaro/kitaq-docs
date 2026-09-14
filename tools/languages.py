"""Language order and same-volume links for this nine-language publication."""
import html

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
        prefix='../' if current!='ja' else ''
        folder='' if language=='ja' else language+'/'
        href=prefix+folder+key+'.html'
        code=HTML_LANG.get(language,language)
        selected=' aria-current="page"' if current==language else ''
        links.append(f'<a href="{html.escape(href,quote=True)}" lang="{code}" hreflang="{code}"{selected}>{label}</a>')
    return '<nav class="languages" aria-label="'+html.escape(nav_label,quote=True)+'">'+' '.join(links)+'</nav>'
