"""Apply reviewed prose translations after language-neutral feature renderers.

Code, source excerpts, command output and internal HTML markers stay unchanged.
This pass uses only authored exact-match translations, not a translation service.
"""
from pathlib import Path
import json,re,sys
try:
    from bs4 import BeautifulSoup,Comment
except ImportError:
    sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'_translation_deps'))
    from bs4 import BeautifulSoup,Comment
SITE=Path(__file__).resolve().parents[1]

def caption_headers(messages):
    """Reuse reviewed labels, without guessing translations of identifiers."""
    names=set()
    for platform in ('gb','fc'):
        names.update(row['name'] for row in json.loads((SITE/'reference'/f'{platform}-api.json').read_text(encoding='utf-8'))['records'])
    candidates={}
    for source,target in messages.items():
        if ': ' not in source:continue
        name,tail=source.split(': ',1)
        if name not in names or not target.startswith(name+': '):continue
        source_head=tail.split(' — ',1)[0]
        target_head=target[len(name)+2:].split(' — ',1)[0]
        candidates.setdefault(source_head,set()).add(target_head)
    ambiguous={k:v for k,v in candidates.items() if len(v)>1}
    if ambiguous:raise ValueError('Conflicting reviewed caption labels: '+repr(ambiguous))
    return {key:next(iter(values)) for key,values in candidates.items()}

def publish(language):
    messages=json.loads((SITE/'tools/i18n'/language/'messages.json').read_text(encoding='utf-8'))
    headers=caption_headers(messages) if language in {'ko','zh-TW','fr','es','de'} else {}
    if headers:
        audio={value.rsplit(' — ',1)[1] for key,value in messages.items() if key.endswith(' — Captured audio') and ' — ' in value}
        if len(audio)!=1:raise ValueError('Missing or inconsistent reviewed audio label: '+language)
        messages.setdefault('Captured audio',next(iter(audio)))
    def translated(value):
        key=value.strip()
        if key not in messages:
            key=re.sub(r'\s+',' ',key)
        if key in messages:
            return value[:len(value)-len(value.lstrip())]+messages[key]+value[len(value.rstrip()):]
        # Captions may already contain localized expected-result prose, while
        # their hardware/frame/player prefix is emitted by a shared renderer.
        head,separator,body=key.partition(' — ')
        if head in headers:
            result=headers[head]+(separator+messages.get(body,body) if separator else '')
            return value[:len(value)-len(value.lstrip())]+result+value[len(value.rstrip()):]
        if ': ' in head:
            name,label=head.split(': ',1)
            if label in headers and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',name):
                result=name+': '+headers[label]+(separator+messages.get(body,body) if separator else '')
                return value[:len(value)-len(value.lstrip())]+result+value[len(value.rstrip()):]
        if language=='zh-CN':
            value=value.replace(' — Captured audio',' — 已捕获的音频')
            value=re.sub(r' / player (\d+)',r' / 玩家 \1',value)
            value=re.sub(r' / frame (\d+)',r' / 第 \1 帧',value)
            value=re.sub(r' / PHASE (\d+)',r' / 相位 \1',value)
        return value
    for path in (SITE/language).glob('*.html'):
        if 'preview' in path.name:continue
        soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
        for node in list(soup.find_all(string=True)):
            if isinstance(node,Comment) or node.find_parent(['pre','code','script','style']):continue
            before=str(node);after=translated(before)
            if before!=after:node.replace_with(after)
        for node in soup.find_all(True):
            for attr in ('alt','aria-label','placeholder','title'):
                if node.has_attr(attr):node[attr]=translated(node[attr])
        if language=='zh-CN':
            for paragraph in soup.select('#wire3d-fc-guide > p'):
                if paragraph.find('code',string='wire3d_uploaded_tiles'):
                    paragraph.clear()
                    prose='调用 <code>EndFrame</code> 后，<code>wire3d_uploaded_tiles</code> 表示上传的图块数，<code>wire3d_transfer_frames</code> 表示上传批数加上最终交换所等待的次数。后者不等于绘制的总耗时：变换、光栅化和 CPU 侧的状态维护也需要时间。透视投影采用量化倒数表；128 像素宽视口在最近深度处的比例值从 256 饱和为 255。'
                    paragraph.extend(list(BeautifulSoup(prose,'html.parser').contents))
        if language in {'ko','zh-TW','fr','es','de'}:
            from generate_i18n import finish_inline_prose
            finish_inline_prose(soup,language)
        path.write_text(str(soup),encoding='utf-8')

if __name__=='__main__':
    publish(sys.argv[1] if len(sys.argv)>1 else 'zh-CN')
