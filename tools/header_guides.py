"""Render authored, source-bound introductions for declaration-only headers."""
from pathlib import Path
import hashlib,html,json,re

SITE=Path(__file__).resolve().parents[1]
SOURCE=Path(__file__).with_name('api_descriptions')

def remove_guides(text):
    return re.sub(r'<!-- header-guide:start -->.*?<!-- header-guide:end -->','',text,flags=re.S)

def render(text,platform,language):
    """Explain header roles without creating duplicate function-reference cards."""
    if language not in ('ja','en'):return text
    from api_contracts import inline
    text=remove_guides(text)
    repos=SITE.parents[1]/'publish/github_20260912'
    if not repos.exists():repos=SITE.parent
    bindings=json.loads((SOURCE/'header_guide_sources.json').read_text(encoding='utf-8'))
    for name,digest in bindings.items():
        if hashlib.sha256((repos/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Header guide source changed: '+name)
    guides=json.loads((SOURCE/'header_guides.json').read_text(encoding='utf-8'))
    for key,guide in guides.items():
        owner,name=key.split(':')
        if owner!=platform:continue
        pattern=r'(<details class="searchable"(?: id="[^"]+")?><summary><code>'+re.escape(name)+r'\.h</code>.*?</summary>)'
        block='<!-- header-guide:start --><div class="header-guide" data-header-contract="'+key+'">'
        block+=''.join('<p>'+inline(p)+'</p>' for p in guide[language])
        if guide['links']:
            label='関数の使い方とサンプル' if language=='ja' else 'Function details and examples'
            block+='<p>'+label+': '+', '.join('<a href="'+html.escape(target,quote=True)+'"><code>'+html.escape(label)+'</code></a>' for target,label in guide['links'])+'</p>'
        block+='</div><!-- header-guide:end -->'
        def insert(match):
            opening=match[1]
            if ' id=' not in opening.split('><summary>',1)[0]:
                opening=opening.replace('<details class="searchable">','<details class="searchable" id="header-'+key.replace(':','-')+'">',1)
            return opening+block
        text,count=re.subn(pattern,insert,text,count=1,flags=re.S)
        if count!=1:raise ValueError('Header guide target missing: '+key)
    if platform=='gb':
        title='ROMの正弦波テーブル：math.c' if language=='ja' else 'ROM sine table: math.c'
        paragraphs=(['`math.c`は256個のROMデータ`MATH_SIN`を用意します。値は`128 + round(127*sin(2*pi*phase/256))`で、添字0～255を1周期として使います。角度0・64・128・192の値は128・255・128・1です。',
            '使うソースで`#include "math.c"`を一度だけ行います。`u8 phase`を増やすと255の次は0に戻ります。たとえば`s16 offset = (s16)MATH_SIN[phase] - 128;`は、左右や上下へ揺らすための−127～127の変位を得る例です。必要な振幅へ縮小してから座標へ加え、位相はゲームのフレーム更新に合わせて進めます。ROMバンクを切り替える場合はテーブルが見える配置を保ってください。'] if language=='ja' else
            ['`math.c` supplies the 256-byte ROM table `MATH_SIN`. Samples follow `128 + round(127*sin(2*pi*phase/256))`, with indices 0..255 spanning one cycle. Phases 0, 64, 128 and 192 yield 128, 255, 128 and 1.',
            'Include `#include "math.c"` once in the program. An incrementing `u8 phase` wraps from 255 to zero. For example, `s16 offset = (s16)MATH_SIN[phase] - 128;` obtains a displacement from −127 to 127 for horizontal or vertical motion. Scale it to the desired amplitude before adding it to a coordinate, and advance phase with the game frame update. Keep the table visible when changing ROM banks.'])
        block='<!-- header-guide:start --><section id="sine-table" data-header-contract="gb:math"><h3>'+title+'</h3>'+''.join('<p>'+inline(p)+'</p>' for p in paragraphs)+'</section><!-- header-guide:end -->'
        assert text.count('<h2 id="headers">')==1
        text=text.replace('<h2 id="headers">',block+'<h2 id="headers">',1)
    return text
