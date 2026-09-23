"""Insert the bilingual FC wireframe guide and verified images beside mathematics."""
from pathlib import Path
import hashlib,json,re,shutil
from generate import md
SITE=Path(__file__).resolve().parents[1]
ROOT=SITE.parents[1]
LIB=ROOT/'publish/github_20260912/kitaqfc/lib'
PROOFS=ROOT/'publish/library_docs_20260914/fc-effects/wire3d/proofs'

def overview(value,language):
    records=json.loads((PROOFS/'results.json').read_text())
    assert len(records)==9 and all(r['passed'] for r in records)
    for row in records:
        for path,digest in row['input_sha256'].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest, path+' changed after verification'
    text=(LIB/'wire3d.md').read_text(encoding='utf-8')
    en,ja=text.split('## 日本語',1)
    example=re.search(r'```c.*?```',en,re.S)[0]
    command=re.search(r'```powershell.*?```',en,re.S)[0]
    if language=='ja':
        text=ja.replace('上のサンプルは、',example+'\n\n'+command+'\n\nこのサンプルは、')
        title='8.1　画面サイズを選べるワイヤーフレーム'
    else:
        text=en.split('\n',1)[1];title='8.1  Wireframes with a selectable viewport'
    prefix='' if language=='ja' else '../'
    block='<section id="wire3d-fc-guide"><h3>'+title+'</h3>'+md(text)
    block=re.sub(r'<tr><td><code>(Wire3DFC_\w+)\(',lambda m:'<tr id="guide-'+m[1]+'"><td><code>'+m[1]+'(',block)
    block+='<p><a href="'+prefix+'samples/api-examples/fc/wire3d_cube.c">'+('回転する立方体のサンプル' if language=='ja' else 'Rotating cube sample')+'</a></p>'
    build=r'.\kitaqfc\kitaqfc.exe .\kitaq-docs\samples\api-examples\fc\wire3d_cube.c -I .\kitaqfc\lib --mapper=nrom --nes-chr-ram -o .\wire_cube.nes'
    block+=md('```powershell\n'+build+'\n```')
    for width,height in [(64,48),(96,64),(128,96)]:
        source=PROOFS/f'{width}-cube/screen.png';destination=SITE/f'verification/api-wireframe-fc/cube-{width}.png'
        destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
        caption=(f'{width}×{height}：Y軸を3/32回転した立方体です。12本の辺が連結し、背景に古い線が残らないことを確認します。' if language=='ja' else f'{width}×{height}: a cube rotated 3/32 of a turn about Y. Expect twelve connected edges and no old lines in the background.')
        block+='<figure><img class="screen" width="512" height="480" style="image-rendering:pixelated" src="'+prefix+destination.relative_to(SITE).as_posix()+'" alt="'+caption+'"><figcaption>'+caption+'</figcaption></figure>'
    block+='<p>'+('KUROSAKIで3サイズ×3種類の画像を照合し、線・立方体・消去の9ケースを確認しました。さらに、3サイズと4種類のコンパイラ設定で、投影の境界値・NULLポインター・全32段階の各軸回転・複合回転・無効な辺の除外を確認しています。通常の描画サンプルはNROM、境界条件をまとめた大きなテストROMはMMC3を使います。実機での計測結果ではありません。' if language=='ja' else 'KUROSAKI checked lines, a cube and clearing at each size: nine image checks in total. Additional checks cover projection boundaries, null pointers, all 32 rotation steps on each axis, combined rotations and rejected edges at three viewport sizes with four compiler configurations. The drawing examples use NROM; the larger boundary-test ROM uses MMC3. These are emulator checks, not hardware measurements.')+'</p></section>'
    start='<!-- fc-wire-guide:start -->'
    cards='<!-- fc-wire-cards:start -->'
    end='<!-- fc-wire-guide:end -->'
    if start in value:
        # Preserve the API cards and any separately inserted library module.
        # The guide prefix ends immediately before the card marker.
        begin=value.index(start);finish=value.index(end,begin)
        split=value.find(cards,begin,finish)
        assert split>=0,'Existing wireframe guide has no card boundary'
        assert block.endswith('</section>')
        value=value[:begin]+start+block[:-len('</section>')]+value[split:]
    else:
        block=start+block+end
        value,count=re.subn(r'(?=<h2[^>]*>9[ .　])',lambda m:block,value,count=1)
        assert count==1
    from api_fc_wireframe_proofs import render_cards,ensure_header
    return ensure_header(render_cards(value,language))

def main():
    for language in ['ja','en']:
        file=(SITE if language=='ja' else SITE/'en')/'fc-library.html'
        file.write_text(overview(file.read_text(encoding='utf-8'),language),encoding='utf-8')
    print('FC wireframe guide: 8 individual API entries and 3 labeled images in JA/EN')

if __name__=='__main__':main()
