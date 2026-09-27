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

def publish(language):
    messages=json.loads((SITE/'tools/i18n'/language/'messages.json').read_text(encoding='utf-8'))
    def translated(value):
        key=value.strip()
        if key in messages:
            return value[:len(value)-len(value.lstrip())]+messages[key]+value[len(value.rstrip()):]
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
        path.write_text(str(soup),encoding='utf-8')

if __name__=='__main__':
    publish(sys.argv[1] if len(sys.argv)>1 else 'zh-CN')
