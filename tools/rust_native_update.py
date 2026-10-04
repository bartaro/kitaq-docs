"""Maintain native build instructions without changing console C examples or historical evidence."""
from pathlib import Path
import html,json,re
HERE=Path(__file__).resolve().parent;SITE=HERE.parent
T=json.loads((HERE/'rust_public_texts.json').read_text(encoding='utf-8'))
LANGS=['en','ja','ko','zh-CN','zh-TW','fr','es','de','pt']
E=html.escape
def code(text,lang='sh'):
 return '<div class="codebox"><span class="lang">'+lang+'</span><button class="copy" type="button">Copy</button><pre><code>'+E(text)+'</code></pre></div>'
def tables(repo):
 rows=[('Windows x64',repo+'.exe')]
 if repo=='kitaqgb':rows.extend([('Linux x64 (musl)','bin/linux-x86_64/'+repo),('Linux x64 (GNU)','bin/linux-gnu-x86_64/'+repo),('macOS ARM64','bin/macos-arm64/'+repo),('macOS Intel','bin/macos-x86_64/'+repo),('macOS Universal','bin/macos-universal/'+repo)])
 else:rows.extend([('Linux x64','bin/Linux-X64/'+repo),('macOS ARM64','bin/macOS-ARM64/'+repo),('macOS Intel','bin/macOS-X64/'+repo)])
 return '<div class="tablewrap"><table><tr><th>OS</th><th>'+repo+'</th></tr>'+''.join('<tr><td>'+E(k)+'</td><td><code>'+E(v)+'</code></td></tr>' for k,v in rows)+'</table></div>'
def setup(lang,repo):
 t=T[lang]
 return '<p>'+E(t['build'])+'</p>'+code('cd '+repo+'\ncargo test --locked --tests\ncargo build --locked --release')+'<p>'+E(t['files'])+'</p>'+tables(repo)+code('.\\scripts\\build.ps1\n.\\'+repo+'.exe --help','powershell')+code('sh scripts/build.sh')+'<p>'+E(t['examples'])+'</p>'
def section(lang,book):
 t=T[lang];prefix='../' if lang!='ja' else '';repo='kitaqgb' if book in ['kitaqgb','gb-library'] else 'kitaqfc' if book in ['kitaqfc','fc-library'] else None
 title=t['libtitle'] if book.endswith('library') else t['verifytitle'] if book in ['verification','index'] else t['title']
 body='<section id="rust-native-20261004"><h2 id="rust-native-20261004-heading">'+E(title)+'</h2>'
 if repo:
  if book.endswith('library'):body+='<p>'+E(t['library'])+'</p>'
  else:body+='<p>'+E(t['build'])+'</p><p>'+E(t['files'])+'</p>'+tables(repo)
  body+='<p><a href="https://github.com/bartaro/'+repo+'">'+repo+'</a> · <a href="https://github.com/bartaro/'+repo+'/tree/main/tools">'+E(t['title'])+'</a> · <a href="https://github.com/bartaro/'+repo+'/actions">GitHub Actions</a></p>'
 body+='<p>'+E(t['proof'])+'</p><p>'+E(t['scope'])+'</p>'
 body+='<p><a href="'+prefix+'verification/rust-native-20261004/kitaqgb.json">KITAQGB · SHA-256</a> · <a href="'+prefix+'verification/rust-native-20261004/kitaqfc.json">KITAQFC · SHA-256</a></p>'
 if repo and book==repo:
  ext='gb' if repo=='kitaqgb' else 'nes';options='--cart=romonly --romsize=32k' if ext=='gb' else '--mapper=nrom'
  body+='<h3>'+E(t['exampletitle'])+'</h3><p>'+E(t['examples'])+'</p>'+code(repo+' game.c -I lib -o game.'+ext+' '+options)
 return body+'</section>'
def update_page(path,lang,book):
 text=path.read_text(encoding='utf-8');before=text
 if lang=='pt':
  labels={'en':'English','ja':'日本語','ko':'한국어','zh-CN':'简体中文','zh-TW':'繁體中文','fr':'Français','es':'Español','de':'Deutsch'}
  nav='<nav class="languages" aria-label="Languages">'+''.join('<a href="../'+('' if l=='ja' else l+'/')+book+'.html" lang="'+l+'" hreflang="'+l+'">'+label+'</a> ' for l,label in labels.items())+'</nav>'
  text=re.sub(r'<nav\b[^>]*class="languages"[^>]*>.*?</nav>',nav,text,count=1,flags=re.S)
 if book in ['kitaqgb','kitaqfc']:
  # The stable chapter ID is preserved to keep incoming links working.
  pattern=r'(<h2 id="2[^\"]*">.*?</h2>).*?(?=<h2\b)'
  text,count=re.subn(pattern,lambda m:m[1]+setup(lang,book),text,flags=re.S);assert count==1,(path,count)
 text=re.sub(r'<section id="rust-native-20261004">.*?</section>','',text,flags=re.S)
 text=re.sub(r'<a data-rust-native="true" href="#rust-native-20261004-heading">.*?</a>','',text,flags=re.S)
 text=text.replace('<main id="main">','<main id="main">'+section(lang,book),1)
 if '<nav class="toc"' in text:
  text=re.sub(r'(<nav class="toc"[^>]*>)',lambda m:m[1]+'<a data-rust-native="true" href="#rust-native-20261004-heading">'+E(T[lang]['title'])+'</a>',text,count=1)
 if text!=before:path.write_text(text,encoding='utf-8',newline='\n')
def positive_runtime(p):
 # Only obsolete positive Framework requirements; statements that .NET is unnecessary remain valid.
 return bool(re.search(r'MSBuild|\.csproj|\.NET Framework 4\.',p,re.I))
def update_sources(root):
 for lang in LANGS:
  base=root/'tools/en' if lang=='en' else root/'tools/i18n'/lang
  for repo in ['kitaqgb','kitaqfc']:
   path=base/(repo+'.md')
   if not path.exists():continue
   text=path.read_text(encoding='utf-8')
   pattern=r'(^## 2[^\n]*\n).*?(?=^## 3)'
   text,count=re.subn(pattern,lambda m:m[1]+T[lang]['build']+'\n\n{{CODE:0}}\n\n'+T[lang]['files']+'\n\n'+T[lang]['examples']+'\n\n',text,flags=re.M|re.S);assert count==1,path
   path.write_text(text,encoding='utf-8',newline='\n')
 # Guide translations and their rendered pages keep sample C/code untouched.
 for path in (root/'tools').rglob('*.py'):
  if path.name in ['rust_native_update.py','collect.py']:continue
  text=path.read_text(encoding='utf-8-sig')
  # Requirements represented as a single literal prose line in language tables.
  if path.name in ['sample_guides.py','sample_guide_translations.py']:
   # Rendering is handled by update_all; source-specific tables are preserved rather than guessed.
   continue
def update_all(root=SITE):
 for lang in LANGS:
  prefix=Path() if lang=='ja' else Path(lang)
  for book in ['kitaqgb','gb-library','kitaqfc','fc-library','verification','index']:
   path=root/prefix/(book+'.html')
   if path.exists():update_page(path,lang,book)
 # The supplied game guide used the old Framework requirement in each locale.
 for path in (root/'apps/harapeko_shirohebi').glob('guide-*.html'):
  lang=path.stem.removeprefix('guide-')
  if lang not in T:continue
  text=path.read_text(encoding='utf-8')
  text=re.sub(r'<p>[^<]*(?:\.NET Framework 4\.|MSBuild)[^<]*(?:<code>.*?</code>[^<]*)*</p>',lambda m:'<p>'+E(T[lang]['build'])+'</p><p>'+E(T[lang]['examples'])+'</p>',text,flags=re.S)
  path.write_text(text,encoding='utf-8',newline='\n')
def publish(lang):
 prefix=Path() if lang=='ja' else Path(lang)
 for book in ['kitaqgb','gb-library','kitaqfc','fc-library','verification','index']:
  path=SITE/prefix/(book+'.html')
  if path.exists():update_page(path,lang,book)
if __name__=='__main__':update_all();update_sources(SITE)
