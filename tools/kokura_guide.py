"""Render the reviewed JA/EN command guide without rebuilding unrelated API cards."""
from pathlib import Path
import re
SITE=Path(__file__).resolve().parents[1]

def markdown(language):
    return (SITE/'tools'/language/'kokura_commands.md').read_text(encoding='utf-8')

def block(language):
    import generate
    text=generate.md(markdown(language))
    if language=='en':text=text.replace('>コピー</button>','>Copy</button>')
    return '<!-- kokura-guide:start -->'+text+'<!-- kokura-guide:end -->'

def update_existing():
    for language in ('ja','en'):
        path=SITE/('en' if language=='en' else '')/'kokura.html'
        text=path.read_bytes().decode('utf-8')
        text=re.sub(r'<!-- kokura-guide:start -->.*?<!-- kokura-guide:end -->','',text,flags=re.S)
        assert '<h2 id="commands">' in text
        text=text.replace('<h2 id="commands">',block(language)+'<h2 id="commands">',1)
        # Derive the contents from the actual headings; retain the existing navigation label.
        headings=re.findall(r'<h2 id="([^"]+)">(.*?)</h2>',text,re.S)
        links=''.join('<a href="#'+ident+'">'+re.sub('<[^>]+>','',title)+'</a>' for ident,title in headings)
        text=re.sub(r'(<nav class="toc"[^>]*>).*?</nav>',lambda m:m[1]+links+'</nav>',text,count=1,flags=re.S)
        path.write_bytes(text.encode('utf-8'))

if __name__=='__main__':update_existing()
