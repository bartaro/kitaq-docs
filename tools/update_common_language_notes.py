"""Keep active compiler chapters and their HTML expression guidance in agreement."""
from pathlib import Path
import html,json,re
from generate import md

SITE=Path(__file__).resolve().parents[1]
NOTES=json.loads((SITE/'tools/common_language_notes.json').read_text(encoding='utf-8'))

def insert(text,block,anchor,key):
    start='<!-- '+key+':start -->';end='<!-- '+key+':end -->'
    text=re.sub(re.escape(start)+'.*?'+re.escape(end)+r'\s*','',text,flags=re.S)
    assert anchor in text,anchor
    return text.replace(anchor,start+'\n'+block+'\n'+end+'\n'+anchor,1)

def main():
    chapters=SITE/'tools/chapters.py';text=chapters.read_text(encoding='utf-8')
    for book,number in [('kitaqgb',6),('kitaqfc',5)]:
        key='common-language-'+book
        anchor='## 6　条件分岐と繰り返し' if book=='kitaqgb' else '## 5　ループと状態による分岐'
        text=insert(text,NOTES['ja'],anchor,key)
        en=SITE/'tools/en'/(book+'.md');content=en.read_text(encoding='utf-8')
        anchor_en='## 6. Branches and loops' if book=='kitaqgb' else '## 5. Loops and state dispatch'
        en.write_text(insert(content,NOTES['en'],anchor_en,key),encoding='utf-8')
        for lang,prefix in [('ja',''),('en','en/')]:
            page=SITE/prefix/(book+'.html');markup=page.read_text(encoding='utf-8')
            anchor_html=re.search(r'<h2 id="'+str(number)+r'-[^\"]+">',markup).group(0)
            markup=insert(markup,md(NOTES[lang]),anchor_html,key)
            if book=='kitaqfc':
                replacements={
                    'switchは未対応なので、状態による分岐にはif/elseを使います。':'switchでは0～255のcase定数で分岐し、caseに一致しなければdefaultを実行します。判定式は1回だけ評価します。breakは最も内側のループまたはswitchを抜け、switch内のcontinueは外側のループへ進みます。',
                    'switch is unsupported, so use if/else for state dispatch.':'A switch selects a case constant in 0..255 or the default body when no case matches. Its selector is evaluated once. break exits the innermost loop or switch; continue inside a switch advances the enclosing loop.'}
                for before,after in replacements.items():markup=markup.replace(before,after)
            page.write_text(markup,encoding='utf-8')
    chapters.write_text(text,encoding='utf-8')
    print('Updated JA/EN compiler chapters and four HTML pages')

if __name__=='__main__':main()
