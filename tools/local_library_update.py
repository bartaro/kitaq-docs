"""Render a dated local-source supplement without rebinding historical proofs."""
from pathlib import Path
import html,json,re

SITE=Path(__file__).resolve().parents[1]
SECTION='local-library-20261003'
LANGS=['ja','en','ko','zh-CN','zh-TW','fr','es','pt','de']
FIELDS=['intro','physics2d','physics3d','kinematic','bank','palette','sprite','vram','wire','audio']
AFFECTED={'kq3d_step','kq3d_integrate_body','bank_switch','metasprite_draw','vram_get_queue_capacity','Wire3DDMG_DrawIndexedEdges','AudioVBlank_QueueReset','AudioVBlank_QueueRefill','AudioVBlank_QueuePlay','cgb_bg_color','cgb_obj_color','cgb_bg_rgb','cgb_obj_rgb','kq2d_body_limit_speed','kq2d_body_resolve_surface','kq2d_scale_q8'}

def texts():
    result=json.loads((SITE/'tools/local_library_texts.json').read_text(encoding='utf-8'))
    if set(result)!=set(LANGS):raise ValueError('All nine authored editions are required')
    keys=set(result['en'])
    if any(set(v)!=keys or not all(isinstance(t,str)and t.strip()for t in v.values())for v in result.values()):raise ValueError('Missing authored translation')
    return result

def render(language):
    t=texts()[language];prefix=''if language=='ja'else'../'
    evidence=prefix+'verification/'+SECTION+'/'
    body=[f'<section id="{SECTION}" data-local-library="2026-10-03"><h2 id="{SECTION}-heading">{html.escape(t["title"])}</h2>']
    for key in FIELDS:body.append('<p>'+html.escape(t[key])+'</p>')
    signature='u8 kq3d_overlap_sphere_aabb(const KQBody3D* sphere, const KQBody3D* box);'
    body.append('<details class="api searchable" id="api-kq3d_overlap_sphere_aabb" data-api-contract="local-source-20261003"><summary><code>kq3d_overlap_sphere_aabb</code></summary><pre><code>'+html.escape(signature)+'</code></pre><p>'+html.escape(t['physics3d'])+'</p><p><a href="'+evidence+'sources/lib/physics3d.c">physics3d.c</a> / <a href="'+evidence+'sources/lib/physics3d.h">physics3d.h</a></p></details>')
    body.append('<h3>'+html.escape(t['verification'])+'</h3>')
    for key in ['surface','edges','scope']:body.append('<p>'+html.escape(t[key])+'</p>')
    body.append('<p><a href="'+evidence+'manifest.json">'+html.escape(t['evidence'])+'</a> · <a href="'+evidence+'evidence.tar.gz">evidence.tar.gz</a> · <a href="'+evidence+'verify_rom_cases.py">verify_rom_cases.py</a> · <a href="'+evidence+'verify_surface.py">verify_surface.py</a></p></section>')
    return ''.join(body)

def publish(language):
    t=texts()[language];root=SITE if language=='ja'else SITE/language
    for name in ['gb-library','verification']:
        path=root/(name+'.html');s=path.read_bytes().decode('utf-8')
        s=re.sub(r'<section id="'+SECTION+r'".*?</section>','',s,flags=re.S)
        s=re.sub(r'<p class="local-library-note".*?</p>','',s,flags=re.S)
        s=re.sub(r'<a href="#'+SECTION+r'-heading"[^>]*>.*?</a>','',s,flags=re.S)
        start=s.index('<main');p=s.index('<h2',start)
        s=s[:p]+render(language)+s[p:]
        if name=='gb-library':
            def add_note(m):
                return m[0]+('<p class="local-library-note"><a href="#'+SECTION+'-heading">'+html.escape(t['note'])+'</a></p>'if m[1]in AFFECTED else'')
            s=re.sub(r'<details\b[^>]*\bid="api-([^" ]+)"[^>]*><summary>.*?</summary>',add_note,s,flags=re.S)
        link='<a href="#'+SECTION+'-heading">'+html.escape(t['title'])+'</a>'
        s=re.sub(r'<nav\b(?=[^>]*\bclass="toc")[^>]*>',lambda m:m[0]+link,s,count=1)
        path.write_bytes(s.encode('utf-8'))

def readme(language,source):
    t=texts()[language];body=['<!-- local-library-20261003:start -->','## '+t['title'],'']
    body += [t[k]+'\n'for k in FIELDS]
    body += ['### '+t['verification'],'']+[t[k]+'\n'for k in ['surface','edges','scope']]
    url='https://bartaro.github.io/kitaq-docs/'+(''if language=='ja'else language+'/')+'gb-library.html#'+SECTION+'-heading'
    body+=['['+t['evidence']+']('+url+')','<!-- local-library-20261003:end -->','']
    source=re.sub(r'<!-- local-library-20261003:start -->.*?<!-- local-library-20261003:end -->\s*','',source,flags=re.S)
    p=source.find('<!-- readme-language-links:end -->')
    if p>=0:p+=len('<!-- readme-language-links:end -->')
    else:p=source.find('\n')
    return source[:p]+'\n\n'+'\n'.join(body)+source[p:]

if __name__=='__main__':
    for language in LANGS:publish(language)
