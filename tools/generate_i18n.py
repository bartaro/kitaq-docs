"""Render authored translations with unchanged code, API IDs and evidence.

No translation service is used. Prose and reference strings are maintained in
tools/i18n. Missing translations are errors, never silently filled with English.
Requires beautifulsoup4. Pass --inspect to write the outstanding string inventory.
"""
from pathlib import Path
import argparse, html, json, re, sys
try:
    from bs4 import BeautifulSoup, NavigableString, Comment
except ImportError:
    local = Path(__file__).resolve().parents[3] / '_translation_deps'
    sys.path.insert(0, str(local))
    from bs4 import BeautifulSoup, NavigableString, Comment
import generate as g
import generate_en as en

S = Path(__file__).resolve().parents[1]
from languages import LANGUAGES, HTML_LANG, language_nav
BOOKS = ['index','kitaqgb','gb-library','kokura','kitaqfc','fc-library','kurosaki','sarakura','verification']
GENERATED = {'index':'books','verification':'scope','kokura':'commands','kurosaki':'commands','sarakura':'commands'}
BUFFER_NOTE = '. For arrays and pointers, allocate sufficient storage and keep it valid until processing finishes.'
PROVIDER_NOTE = '. Include the providers of any additional functions it calls.'
PURPOSE_NOTE = '. The declaration, original notes and implementation below define exact units, terminators and return conditions.'
ENTRY_NOTE = ' entries. Open an entry for its syntax, arguments, source notes and usage example. Calling fragments require surrounding initialization; they are not standalone ROMs. Argument-passing examples show how prepared values reach the API, and do not establish device-level verification.'
missing = set()

def lookup(key, messages):
    if re.fullmatch(r'[0-9]+|[A-F0-9]{2}|(?:gb|fc)_[a-z_]+|kitaq(?:gb|fc)/lib/[\w.]+|IMM8|IMM16|IMP|REL|ABS|LDH|opcode',key):return key
    if key not in messages:
        missing.add(key)
        return key
    return messages[key]

def translate_text(text, messages):
    stripped = text.strip()
    if not stripped or not re.search('[A-Za-z]{2}',stripped):return text
    def T(s):return lookup(s,messages)
    if stripped in LANGUAGES.values() or stripped in {'KITAQ','KITAQ SERIES','KITAQGB','KITAQFC','KOKURA','KUROSAKI','SARAKURA','2026.09','c','csharp','powershell','help','usage','json','text'}:
        return text
    if stripped.startswith('— '):result='— '+T(stripped[2:])
    elif ' Module: ' in stripped and stripped.endswith(PURPOSE_NOTE):
        verb, mod=stripped[:-len(PURPOSE_NOTE)].split('. Module: ',1)
        result=T('purpose_template').format(action=T(verb),module=T(mod))
    elif stripped.endswith(BUFFER_NOTE):result=stripped[:-len(BUFFER_NOTE)]+T(BUFFER_NOTE)
    elif stripped.endswith(PROVIDER_NOTE):result=stripped[:-len(PROVIDER_NOTE)]+T(PROVIDER_NOTE)
    elif re.match(r'^\d+ entries\.',stripped):result=T(ENTRY_NOTE).format(count=stripped.split(' ',1)[0])
    elif re.match(r'^[\w.-]+\.h — ',stripped):
        name, description=stripped.split(' — ',1);result=name+' — '+T(description)
    elif stripped.startswith(('Source: ','Declaration or identifier source: ')):
        prefix,rest=stripped.split(': ',1);result=T(prefix+': ')+rest
    elif stripped.startswith('Expected result: '):result=T('Expected result: ')+T(stripped[len('Expected result: '):])
    elif stripped.startswith('Build exit code: '):
        m=re.fullmatch(r'Build exit code: (.*?) / Runtime status: (.*)',stripped)
        result=T('build_runtime_template').format(build=m[1],runtime=m[2]) if m else T(stripped)
    elif stripped.startswith('Emulator screenshot for '):result=T('screenshot_template').format(id=stripped[len('Emulator screenshot for '):])
    else:result=T(stripped)
    return text[:len(text)-len(text.lstrip())]+result+text[len(text.rstrip()):]


def finish_inline_prose(soup,lang):
    """Join translated punctuation and Korean particles to inline identifiers.

    English source whitespace must not introduce a space before a period or
    between a Korean particle and its preceding code token. Code, attributes
    and separately rendered API/module contracts remain untouched.
    """
    if lang not in {'ko','zh-TW','fr','es','de'}:return
    for node in list(soup.find_all(string=True)):
        if isinstance(node,Comment) or node.find_parent(['pre','code','script','style']):continue
        if node.find_parent(attrs={'data-api-contract':True}) or node.find_parent(attrs={'data-module-contract':True}):continue
        previous=node.previous_sibling
        if getattr(previous,'name',None) not in {'code','a','strong','em','span'}:continue
        text=str(node);trimmed=text.lstrip()
        if lang=='zh-TW' and trimmed=='.':trimmed='。'
        join=bool(re.match(r'^[.,，。；：！？]',trimmed))
        if lang=='ko' and re.match(r'^(?:은|는|을|를|에|가|로|의|와|과|도|에서|으로|만으로|입니다|이고)(?:\s|[.,;]|$)',trimmed):join=True
        if join and text!=trimmed:node.replace_with(trimmed)


def kokura_command_prose(lang):
    """Insert authored command lessons with exact source command blocks."""
    path=S/'tools/i18n'/lang/'kokura-commands.md'
    if not path.exists():return ''
    source=(S/'tools/en/kokura_commands.md').read_text(encoding='utf-8')
    blocks=re.findall(r'^```[^\n]*\n.*?^```',source,re.M|re.S)
    text=path.read_text(encoding='utf-8')
    ids=[int(v) for v in re.findall(r'\{\{COMMAND:(\d+)\}\}',text)]
    assert ids==list(range(len(blocks))),(lang,'command lesson blocks')
    return re.sub(r'\{\{COMMAND:(\d+)\}\}',lambda m:blocks[int(m[1])],text)


def make_page(lang,key,messages,inspect=False):
    source=(S/'en'/(key+'.html')).read_text(encoding='utf-8')
    # Prompt navigation is authored separately for each language, after translation.
    source=re.sub(r'<!-- loop-prompts:start -->.*?<!-- loop-prompts:end -->','',source,flags=re.S)
    source=re.sub(r'<!-- api-verification:start -->.*?<!-- api-verification:end -->','',source,flags=re.S)
    soup=BeautifulSoup(source,'html.parser')
    # Replace the source edition's navigation instead of duplicating it.
    for navigation in soup.select('nav.languages'):navigation.decompose()
    main=soup.find('main')
    soup.select_one('nav.toc').clear()
    if key!='verification':
        start=main.select_one('.cover')
        boundary=main.find(id=GENERATED.get(key,'samples'))
        cur=start.next_sibling
        while cur is not None and cur!=boundary:
            nxt=cur.next_sibling;cur.extract();cur=nxt
        prose_path=S/'tools/i18n'/lang/(key+'.md')
        if not prose_path.exists():
            missing.add('MISSING CHAPTER: '+lang+'/'+key)
            prose=''
        else:prose=prose_path.read_text(encoding='utf-8')
        if key=='kokura':prose+='\n\n'+kokura_command_prose(lang)
        source_blocks=re.findall(r'^```[^\n]*\n.*?^```',g.TEXT[key],re.M|re.S)
        prose=re.sub(r'\{\{CODE:(\d+)\}\}',lambda m:source_blocks[int(m[1])],prose)
        prose=prose.replace('{{ORIGIN}}',messages.get('origin','{{ORIGIN}}'))
        prose=prose.replace('.\\kitaqgb.exe','.\\kitaqgb\\kitaqgb.exe')
        g.code=en.code
        section=soup.new_tag('section',attrs={'class':'authored'})
        rendered=BeautifulSoup(g.md(prose),'html.parser')
        for a in rendered.find_all(['a','img']):
            attr='href' if a.name=='a' else 'src'
            value=a.get(attr,'')
            if re.match(r'^(samples|verification|reference|assets)/',value):a[attr]='../'+value
        section.extend(list(rendered.contents));start.insert_after(section)
    # Strings inside original source excerpts, command output and identifiers stay verbatim.
    for node in list(soup.find_all(string=True)):
        if isinstance(node, Comment):continue
        if node.find_parent(attrs={'data-api-contract':True}) or node.find_parent(attrs={'data-module-contract':True}):continue
        if node.find_parent(['pre','code','script','style']):continue
        if node.find_parent(class_='authored'):continue
        if str(node).lower()=='html':continue
        node.replace_with(translate_text(str(node),messages))
    finish_inline_prose(soup,lang)
    # The prose code widgets use the same localized labels as the reference widgets.
    for button in soup.select('button.copy'):button.string=lookup('Copy',messages)
    for node in soup.find_all(True):
        for attr in ('alt','placeholder','aria-label'):
            if node.has_attr(attr):node[attr]=translate_text(node[attr],messages)
    soup.html['lang']=HTML_LANG.get(lang,lang)
    # Keep the game-guide card in the current language when its authored guide exists.
    # This does not enable the edition in the public language navigation.
    if key=='index' and lang in {'ko','zh-TW','fr','es','de'}:
        guide=S/'apps/harapeko_shirohebi'/('guide-'+lang+'.html')
        if guide.is_file():
            for link in soup.select('a.book'):
                if '/harapeko_shirohebi/guide-' in link.get('href',''):
                    link['href']='../apps/harapeko_shirohebi/'+guide.name
    mast=soup.select_one('.mast')
    for a in mast.select('a[hreflang]'):a.decompose()
    mast.insert_after(BeautifulSoup(language_nav(key,lang,lookup('Languages',messages)),'html.parser'))
    toc=soup.select_one('nav.toc');toc.clear()
    for h in main.find_all('h2',id=True):
        a=soup.new_tag('a',href='#'+h['id']);a.string=h.get_text();toc.append(a)
    if not inspect:
        dest=S/lang/(key+'.html');dest.parent.mkdir(exist_ok=True)
        dest.write_text(str(soup),encoding='utf-8')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--language',choices=LANGUAGES,default='ko');parser.add_argument('--inspect',action='store_true')
    parser.add_argument('--local-preview',action='store_true',help='Generate an unpublished edition locally without enabling public navigation')
    args=parser.parse_args();lang=args.language
    from publication_languages import ACTIVE_LANGUAGES
    if not args.inspect and lang not in ACTIVE_LANGUAGES and not args.local_preview:
        parser.error('This edition is unpublished; use --local-preview for local generation.')
    path=S/'tools/i18n'/lang/'messages.json'
    if path.exists():
        messages=json.loads(path.read_text(encoding='utf-8'))
    else:
        messages={}
        catalog=json.loads((S/'tools/i18n/catalog.en.json').read_text(encoding='utf-8'))
        strings=path.with_name('strings.tsv')
        if strings.exists():
            seen=set()
            for line in strings.read_text(encoding='utf-8').splitlines():
                if not line.strip() or line.startswith('#'):continue
                ident,value=line.split('\t',1);idx=int(ident)
                if idx in seen:raise ValueError('Duplicate translation ID: '+ident)
                seen.add(idx);messages[catalog[idx]]=value
        origin=path.with_name('origin.md')
        if origin.exists():messages['origin']=origin.read_text(encoding='utf-8').strip()
    if not messages.get('origin'):missing.add('MISSING ORIGIN: '+lang)
    for key in BOOKS:make_page(lang,key,messages,inspect=True)
    if missing:
        (S/'tools/i18n'/lang).mkdir(exist_ok=True)
        (S/'tools/i18n'/lang/'missing.json').write_text(json.dumps(sorted(missing),ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'{lang}: {len(missing)} missing translations');raise SystemExit(1)
    if not args.inspect:
        for key in BOOKS:make_page(lang,key,messages)
        from generate_prompts import publish
        publish(lang)
        from api_contracts import publish as publish_api_contracts
        publish_api_contracts(lang,require_complete=args.local_preview,local_preview=args.local_preview)
        if lang in {'zh-CN','ko','zh-TW','fr','es','de'}:
            from localize_presentations import publish as localize_presentations
            localize_presentations(lang)
    stale=S/'tools/i18n'/lang/'missing.json'
    if stale.exists():stale.unlink()
    print(f'{lang}: 9 pages '+('ready to generate' if args.inspect else 'generated')+'; all reference prose translated')

if __name__=='__main__':main()
