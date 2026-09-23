"""Author the normalized wrapped-distance API contract for both machines."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog
catalog.ROOT=REPOS;texts={};contracts={}
def msg(key,ja,en):
    key='chain_wrap_'+key;texts[key]={'ja':ja,'en':en};return key
purpose=msg('purpose','両端がつながった1本の座標軸で、現在位置から目標位置までの最短の符号付き差分を計算します。画面端をまたぐ追従や距離比較に使えます。','Calculate the shortest signed displacement from the current position to a target on an axis whose ends join. Use it for following or distance comparisons across a field edge.')
target=msg('target','目標位置。0～size−1の範囲で指定します。','Target coordinate, in 0..size−1.')
current=msg('current','現在位置。0～size−1の範囲で指定します。','Current coordinate, in 0..size−1.')
size=msg('size','折り返す座標軸の長さ、1～256。X座標なら幅、Y座標なら高さです。256も渡せる16ビット引数です。','Wrapped axis length, 1..256: width for X, height for Y. This is a 16-bit argument so that 256 is representable.')
returns=msg('returns','最短差分をs16で返します。正は座標が増える方向、負は減る方向、0は同じ位置です。有効な入力では−128～+128に収まります。画面の右や下へ向かう差分が正になります。','Return the shortest displacement as s16: positive toward increasing coordinates, negative toward decreasing coordinates, or zero at the same position. Valid inputs produce −128..+128. With screen coordinates, rightward and downward displacements are positive.')
setup=msg('setup','`chain.h`を読み込み、`chain.c`を1回だけコンパイルします。`Chain`や`ChainBody`の初期化は必要ありません。関数は計算だけを行い、座標配列、節数、画面を変更しません。','Include `chain.h` and compile `chain.c` exactly once. No `Chain` or `ChainBody` initialization is required. The function only calculates a displacement; it does not alter coordinate arrays, joint counts or the screen.')
normalized=msg('normalized','入力の範囲検査や正規化は行いません。size=0、size>256、またはsize以上の座標を渡さないでください。広い座標系から値を渡す場合は、呼び出し前に0～size−1へ折り返します。','The function does not validate or normalize inputs. Do not pass size=0, size>256, or coordinates at least as large as size. Wrap coordinates from a larger coordinate system into 0..size−1 before calling.')
ties=msg('ties','左右の経路が同じ長さなら、直接計算したtarget−currentの符号を保ちます。size=160では0→80が+80、80→0が−80です。サイズが1なら有効な座標は0だけで、結果も0です。','If both routes have the same length, retain the sign of the direct target−current displacement. With size=160, 0→80 returns +80 and 80→0 returns −80. With size=1, zero is the only valid coordinate and the result is zero.')
example=msg('example','このサンプルは座標の折り返しを学ぶためのものです。矢印の左が現在位置、右が目標位置です。幅160で画面端をまたぐ+02/−02、半周の+80/−80、幅1の+00を、関数の戻り値から表示します。先頭の0は2桁表示用です。物体を描画・移動する例ではありません。','This lesson demonstrates wrapped coordinates. Each arrow goes from the current position to the target. It displays computed results +02/−02 for crossing a width-160 edge, +80/−80 for half a field, and +00 for width 1. The leading zero is decimal padding. The lesson does not draw or move an object.')
for platform in ['gb','fc']:
    header=REPOS/f'kitaq{platform}/lib/chain.h';library=header.with_suffix('.c');name='chain_wrap_delta'
    r={r['name']:r for r in catalog.definitions(header)}[name];definition={r['name']:r for r in catalog.definitions(library)}[name]
    r.update(module='chain',definition=definition,availability='implementation',arity_only=False)
    fp=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
    sample_path=f'samples/api-examples/{platform}/chain_wrap.c';sample=(SITE/sample_path).read_text()
    snippet=re.search('// example:'+name+':start\s*\n(.*?)\s*// example:'+name+':end',sample,re.S)[1]
    build=f'.\\kitaq{platform}\\kitaq{platform}.exe .\\kitaq-docs\\'+sample_path.replace('/','\\')+f' -I .\\kitaq{platform}\\lib -I .\\kitaq-docs\\samples -o .\\out\\chain_wrap.'+('gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --cart=mbc5 --romsize=128k' if platform=='gb' else 'nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\font.chr')+' --no-cache --no-disasm'
    contracts[platform+':'+name]=dict(review='chain-wrap-source-20260923',record_sha256=fp,purpose=[purpose],args=[['target',[target]],['current',[current]],['size',[size]]],returns=[returns],notes=[setup,normalized,ties],example=dict(program=sample_path,code=snippet,expected=[example],build='New-Item -ItemType Directory -Force .\\out | Out-Null\n'+build))
    inventory=SITE/f'reference/{platform}-api.json';doc=json.loads(inventory.read_text(encoding='utf-8'));doc['records']=[old for old in doc['records'] if old['name']!=name]+[r];doc['records'].sort(key=lambda r:(r['module'],r['name']));inventory.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
for filename,value in [('chain_wrap_contracts.json',contracts),('chain_wrap_texts.json',texts)]:
    (HERE/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
print('Two wrapped-distance API contracts authored')
