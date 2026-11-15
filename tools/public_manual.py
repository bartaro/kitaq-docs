"""Apply the reader-facing structure after rendering, in every published language.

Keep source examples, API contracts, expected outputs and operational limits.
Remove authoring-run reports and place supplements beside the relevant lesson.
This final rendering pass is intentionally idempotent.
"""
from pathlib import Path
import argparse, html, json, re
from functools import lru_cache
from languages import language_nav
from publication_languages import ORDER, ACTIVE_LANGUAGES

SITE = Path(__file__).resolve().parents[1]
TEXT = json.loads((SITE/'tools/public_manual_texts.json').read_text(encoding='utf-8'))

def plain(value):
    return html.unescape(re.sub('<[^>]+>', '', value))

def inline(value):
    return ''.join('<code>'+html.escape(p[1:-1])+'</code>' if p.startswith('`') else html.escape(p)
                   for p in re.split(r'(`[^`]+`)', value))

def sentences(value):
    return re.split(r'(?<=[。！？])\s*|(?<=[.!?])\s+(?=[A-ZÀ-Ý0-9])', value)

# Only reviewed authoring-report fields are filtered. Never scan code or API
# contracts for a generic word such as "test", "state" or "verification".
REMOVE_FIELDS = {'flags_proof', 'rng_proof', 'rle_proof', 'tl_proof', 'pi_evidence',
                 'wf_feedback_provenance', 'wf_feedback_validation'}
FIRST_SENTENCE = {'as_status', 'ol_color_proof', 'b100_KITAQGB_TRACE_U16_example',
                  'b100_KITAQGB_TRACE_example', 'b100_system_disable_interrupts_example'}
DROP_TAIL = {'fo_scene', 'oam_example', 'rq_shapes', 'sprite0_split_expected',
             'qi_example_zero', 'vq_sample_geometry'}
PROOF = re.compile(r'verif|検証|検査|검증|验证|驗證|Prüfung|Prüfungen|geprüft|Hardware wurde|Hardware ist|hardware|実機|실제 하드웨어|실기기|实机|實機|matériel réel', re.I)

@lru_cache(maxsize=None)
def replacements(language):
    changes=[]
    for path in (SITE/'tools/api_descriptions').glob('*texts.json'):
        data=json.loads(path.read_text(encoding='utf-8'))
        for key,values in data.items():
            if key not in REMOVE_FIELDS | FIRST_SENTENCE | DROP_TAIL | {'dw_wram_example'}:continue
            if isinstance(values,dict) and language not in values:continue
            old=values[ORDER.index(language)] if isinstance(values,list) else values[language]
            if key in REMOVE_FIELDS:new=''
            elif key in FIRST_SENTENCE:new=sentences(old)[0]
            else:
                parts=sentences(old); kept=[]
                for sentence in parts:
                    if (key=='dw_wram_example' and re.search(r'KQ210[23]',sentence)) or PROOF.search(sentence):break
                    kept.append(sentence)
                new=('' if language in {'ja','zh-CN','zh-TW'} else ' ').join(kept).strip()
            if new!=old:changes.append((old,new))
    return changes

def append_to_chapter(text,number,block):
    if not block:return text
    matches=list(re.finditer(r'<h2\b[^>]*>.*?</h2>',text,re.S))
    for i,m in enumerate(matches):
        if re.match(str(number)+r'(?:\D|$)',plain(m[0])):
            end=matches[i+1].start() if i+1<len(matches) else text.index('<footer')
            return text[:end]+block+text[end:]
    raise ValueError('Missing chapter '+str(number))

def strip_section(text,ident):
    match=re.search(r'<section\b[^>]*id="'+ident+r'"[^>]*>.*?</section>',text,re.S)
    return (text[:match.start()]+text[match.end():],match[0]) if match else (text,'')

def normalize_html(text,language,book):
    t=TEXT[language];prefix='' if language=='ja' else '../'
    # Remove publication banners. Chapter 2 already explains native installation.
    for ident in ['rust-native-20261004','binary-update-20261115','source-update-20261114']:
        text,_=strip_section(text,ident)
    text,local=strip_section(text,'local-library-20261003')
    text,fc=strip_section(text,'fc-current-20261004')
    text=re.sub(r'<p class="local-library-note".*?</p>','',text,flags=re.S)
    if book=='gb-library' and local:
        # Preserve this public API entry; the surrounding local/public comparison
        # describes an obsolete workspace and is not an API reference.
        api=re.search(r'<details\b[^>]*id="api-kq3d_overlap_sphere_aabb".*?</details>',local,re.S)
        if api and 'id="api-kq3d_overlap_sphere_aabb"' not in text:
            card=api[0].replace('data-api-contract="local-source-20261003"','data-api-contract="physics3d"')
            card=card.replace(prefix+'verification/local-library-20261003/sources/lib/', 'https://github.com/bartaro/kitaqgb/blob/main/lib/')
            anchor=re.search(r'<h3\b[^>]*id="module-physics3d"[^>]*>.*?</h3>',text,re.S)
            if anchor:text=text[:anchor.end()]+card+text[anchor.end():]
            else:text=text.replace('<h2 id="headers">',card+'<h2 id="headers">',1)
    if book.endswith('library') and 'id="library-language"' not in text:
        text=append_to_chapter(text,1,'<p id="library-language">'+html.escape(t['library'])+'</p>')
    if book=='fc-library' and fc and 'id="library-integration"' not in text:
        notes=json.loads((SITE/'tools/fc_current_texts.json').read_text(encoding='utf-8'))[language]['library']
        text=append_to_chapter(text,1,'<p id="library-integration">'+html.escape(notes)+'</p>')
    if book=='gb-library' and 'id="vblank-gbseq"' not in text:
        text=append_to_chapter(text,7,'<h3 id="vblank-gbseq">'+html.escape(t['audio_title'])+'</h3><p>'+html.escape(t['audio'])+'</p><p><a href="https://github.com/bartaro/kitaqgb/blob/main/lib/AUDIO_VBLANK.md">'+html.escape(t['driver'])+'</a> · <a href="https://github.com/bartaro/kitaqgb/blob/main/tools/gbseq/bin/README.md">GBSEQ — '+html.escape(t['downloads'])+'</a></p>')
    if book=='kokura' and 'id="native-downloads"' not in text:
        text=append_to_chapter(text,2,'<p id="native-downloads"><a href="https://github.com/bartaro/kokura/blob/main/bin/README.md">KOKURA-CLI — '+html.escape(t['downloads'])+'</a></p>')
        text=append_to_chapter(text,6,'<p id="state-compatibility">'+html.escape(t['state'])+'</p>')
    if book=='index' and 'data-reader-index="true"' not in text:
        start=text.index('<main');end=text.index('<footer',start)
        heads=list(re.finditer(r'<h2\b[^>]*id="([^"]+)"[^>]*>.*?</h2>',text[start:end],re.S))
        chunks=[text[start+h.start():start+(heads[i+1].start() if i+1<len(heads) else end-start)] for i,h in enumerate(heads)]
        # Intro, reading guide, volume roles, font, edition, setup, fixes, offline,
        # volume cards, application guide were formerly in append order.
        sections={h[1]:(plain(h[0]),chunk) for h,chunk in zip(heads,chunks)}
        def find_title(pattern):
            return next((chunk for title,chunk in sections.values() if re.search(pattern,title,re.I)), '')
        setup=find_title(r'作業机|working directory|작업 폴더|工作目录|工作目錄|dossier de travail|directorio de trabajo|pasta de trabalho|Arbeitsverzeichnis')
        font=find_title(r'フォント|supplied font|글꼴|字形|police fournie|fuente incluida|fonte incluída|mitgelieferte Schrift')
        books=sections.get('books',('',''))[1]
        apps=sections.get('application-guides',('',''))[1]
        if not setup or not books:raise ValueError(('Missing reader section',language))
        if not font:
            paragraphs=json.loads((SITE/'tools/public_font_paragraphs.json').read_text(encoding='utf-8'))
            font='<h2 id="sample-font">'+('示例字体' if language=='zh-CN' else 'Font')+'</h2>'+paragraphs[ORDER.index(language)].format(prefix=prefix)
        if not apps and language=='pt':
            apps='<h2 id="application-guides">Guias de programação de jogos</h2><div class="books"><a class="book" href="../apps/harapeko_shirohebi/guide-en.html"><span>APP</span><strong>HARAPEKO SHIROHEBI</strong><small>Fluxo do programa, movimento da cobra e biblioteca KITAQGB (em inglês)</small></a></div>'
        offline='<h2 id="offline-reading">'+html.escape(t['offline_title'])+'</h2><p>'+html.escape(t['offline'])+'</p>'
        body=''.join(chunks[:3])+books+setup+font+apps+offline
        text=text[:start+heads[0].start()]+body+text[end:]
        text=text.replace('<main id="main">','<main id="main" data-reader-index="true">',1)
    # Installation belongs after the introduction, beside the build instructions.
    if book in {'kokura','kurosaki','sarakura'}:
        main_start=text.index('<main')
        heads=list(re.finditer(r'<h2\b[^>]*>.*?</h2>',text[main_start:],re.S))
        if heads and not re.match(r'1(?:\D|$)',plain(heads[0][0])):
            a=main_start+heads[0].start();b=main_start+heads[1].start()
            block=text[a:b].replace('<h2','<h3',1).replace('</h2>','</h3>',1)
            text=text[:a]+text[b:]
            heading=next(m for m in re.finditer(r'<h2\b[^>]*>.*?</h2>',text,re.S) if re.match(r'2(?:\D|$)',plain(m[0])))
            text=text[:heading.end()]+block+text[heading.end():]
    if book=='kurosaki':
        # The CLI/API scope is already clear from the introduction.
        text=re.sub(r'<h2\b[^>]*id="10-[^"]+"[^>]*>.*?</h2>\s*<p>.*?</p>\s*','',text,flags=re.S)
        text=re.sub(r'(<h2\b[^>]*id="11-[^"]+"[^>]*>)11',r'\g<1>10',text)
    if book=='gb-library':
        # Also migrate pages exported by the previous editorial pass.
        audio=re.search(r'<h3 id="vblank-gbseq">.*?</h3><p>.*?</p><p>.*?</p>',text,re.S)
        if audio:
            text=text[:audio.start()]+text[audio.end():]
            text=append_to_chapter(text,7,audio[0])
    # Remove per-run metadata in the shell while retaining navigation and assets.
    text=re.sub(r'<div class="edition">.*?</div>','',text,flags=re.S)
    text=text.replace('<b>2026.09</b>','')
    if language=='pt':
        text=text.replace('href="../apps/harapeko_shirohebi/guide-pt.html"','href="../apps/harapeko_shirohebi/guide-en.html"')
        text=text.replace('Fluxo do programa, movimento da cobra e biblioteca KITAQGB</small>','Fluxo do programa, movimento da cobra e biblioteca KITAQGB (em inglês)</small>')
    text=re.sub(r'<a\b[^>]*href="[^\"]*verification/wire3d-feedback-20261009/results.json"[^>]*>.*?</a>\s*·\s*','',text,flags=re.S)
    text=re.sub(r'<footer>.*?</footer>', '<footer><a href="index.html">'+html.escape(t['contents'])+'</a> · <a href="verification.html">'+html.escape(t['gallery'])+'</a></footer>',text,flags=re.S)
    for old,new in replacements(language):
        for escaped_old,escaped_new in [(inline(old),inline(new)),(html.escape(old),html.escape(new))]:
            text=text.replace(escaped_old,escaped_new)
    text=re.sub(r'<p>\s*</p>','',text)
    # Point sample links at the retained screen gallery, with reader-facing labels.
    text=re.sub(r'(<a\b[^>]*href="verification\.html(?:#[^"]*)?"[^>]*>).*?(</a>)',lambda m:m[1]+html.escape(t['gallery'])+m[2],text,flags=re.S)
    text=re.sub(r'(<h2 id="samples">.*?</h2>)\s*<p>.*?</p>',lambda m:m[1]+'<p>'+html.escape(t['samples'])+'</p>',text,count=1,flags=re.S)
    text=re.sub(r'(<h2 id="commands">.*?</h2>)\s*<p>.*?</p>',lambda m:m[1]+'<p>'+html.escape(t['commands'])+'</p>',text,count=1,flags=re.S)
    if book=='verification':
        text=re.sub(r'<h1>.*?</h1>','<h1>'+html.escape(t['gallery'])+'</h1>',text,count=1,flags=re.S)
        text=re.sub(r'<title>.*?</title>','<title>'+html.escape(t['gallery'])+' — KITAQ SERIES</title>',text,count=1,flags=re.S)
        text=re.sub(r'(<h2 id="scope">).*?(</h2>)\s*<p>.*?</p>',lambda m:m[1]+html.escape(t['gallery'])+m[2]+'<p>'+html.escape(t['gallery_intro'])+'</p>',text,count=1,flags=re.S)
    # All dates/hashes removed above describe authoring runs. ROM identity checks
    # used by snapshots/replays and SARAKURA validation remain unchanged.
    text=re.sub(r'<nav\b[^>]*class="languages"[^>]*>.*?</nav>',lambda m:language_nav(book,language),text,flags=re.S)
    main=re.search(r'<main\b[^>]*>(.*?)</main>',text,re.S)[1]
    links=''.join('<a href="#'+html.escape(i,quote=True)+'">'+html.escape(plain(title))+'</a>' for i,title in re.findall(r'<h2\b[^>]*id="([^"]+)"[^>]*>(.*?)</h2>',main,re.S))
    text=re.sub(r'(<nav\b[^>]*class="toc"[^>]*>).*?(</nav>)',lambda m:m[1]+links+m[2],text,flags=re.S)
    return text

def refresh_language_links(root=SITE):
    asset=root/'assets/draft-language-links.js'
    s=asset.read_text(encoding='utf-8')
    data={}
    for book in ['index','kitaqgb','gb-library','kokura','kitaqfc','fc-library','kurosaki','sarakura','verification','loop-engineering']:
     ids=[];chapters={}
     for lang in ACTIVE_LANGUAGES:
      text=(root/('' if lang=='ja' else lang)/(book+'.html')).read_text(encoding='utf-8')
      ids.append(set(re.findall(r'\bid="([^"]+)"',text)))
      mapping={}
      main=re.search(r'<main\b[^>]*>(.*?)</main>',text,re.S)[1]
      for index,(ident,title) in enumerate(re.findall(r'<h2\b[^>]*id="([^"]+)"[^>]*>(.*?)</h2>',main,re.S)):
       label=html.unescape(re.sub('<[^>]+>','',title));n=re.match(r'^(\d+)',label)
       if book=='index':mapping['section-'+str(index)]=ident
       elif n:mapping['chapter-'+n[1]]=ident
      chapters['pt-BR' if lang=='pt' else lang]=mapping
     data[book]={'shared':sorted(set.intersection(*ids)),'chapters':chapters}
    s=re.sub(r'const data = .*?\[book\];','const data = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+'[book];',s,flags=re.S)
    asset.write_bytes(s.encode('utf-8'))

def publish(language,root=SITE,refresh=True):
    folder=root if language=='ja' else root/language
    for path in folder.glob('*.html'):
        before=path.read_bytes();text=before.decode('utf-8')
        after=normalize_html(text,language,path.stem).encode('utf-8')
        if after!=before:path.write_bytes(after)
    if refresh:refresh_language_links(root)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--language',choices=ORDER);p.add_argument('--site',type=Path,default=SITE)
    args=p.parse_args()
    for language in [args.language] if args.language else ACTIVE_LANGUAGES:publish(language,args.site,refresh=False)
    refresh_language_links(args.site)
