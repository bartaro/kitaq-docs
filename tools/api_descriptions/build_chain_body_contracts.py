"""Describe articulated bodies separately from position-history rings."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
sys.path.insert(0,str(SITE/'tools'));import catalog
catalog.ROOT=REPOS;texts={};contracts={}
def msg(key,ja,en):
    key='chain_body_'+key;texts[key]={'ja':ja,'en':en};return key
setup=msg('setup','`chain.h`を読み込み、`chain.c`を1回だけコンパイルします。`ChainBody`は各節の現在位置と向きを保持します。座標履歴を蓄積する`Chain`とは別の状態型です。','Include `chain.h` and compile `chain.c` exactly once. `ChainBody` holds each joint’s current position and heading. It is a separate state type from the `Chain` position-history ring.')
storage=msg('storage','`x`、`y`、`heading`はそれぞれ`capacity`バイトの書き込み可能な配列です。相互に重ねず、使用中は保持してください。添字0が頭で、`count`には頭も含みます。初期化後にポインター・容量・画面サイズを直接変更しないでください。','Supply three separate writable arrays, `x`, `y` and `heading`, each containing `capacity` bytes. Keep them alive while the body is used. Index zero is the head, included in `count`. Do not alter storage pointers, capacity or field dimensions after initialization.')
directions=msg('directions','向きは時計回りの16方向で、0=右、4=下、8=左、12=上です。入力は下位4ビットを使います。画面座標は右・下が正で、幅・高さは1～256ピクセルです。','Headings use 16 clockwise sectors: 0=right, 4=down, 8=left, 12=up. Only the low four input bits are used. Screen coordinates increase rightward and downward; each dimension is 1..256 pixels.')
expected=msg('expected','画像は上から直線、下向きへ曲がって1回更新、4回更新の姿です。座標を2倍に拡大して描き、右端の頭から曲がりが後ろへ伝わります。CGB・FCでは頭が赤、胴が青、尾が緑、DMGでは黒です。成長時に重ねた尾を4回の更新で離してから比較しています。画像は同じ8節を3時点で並べたもので、24節の1本の鎖ではありません。','The image shows a straight body at the top, one update after a downward turn in the middle, and four updates after the turn below. Coordinates are drawn at twice their logical size. The bend travels backward from the head at the right. CGB and FC use red for the head, blue for the body and green for the tail; DMG uses black. Four settling updates separate the duplicated tail after growth. These are three views of the same eight joints, not one 24-joint body.')
no_physics=msg('physics','頭の速度・加速度、当たり判定、描画、待機は呼び出し側で行います。通常は頭を動かした後、シミュレーション1回につき`chain_body_step`を1回呼びます。これは関節追従であり、剛体や厳密な長さ拘束を解く物理ソルバーではありません。','The caller handles head velocity, acceleration, collisions, rendering and waiting. Normally update the head first, then call `chain_body_step` once per simulation tick. This is joint following, not a rigid-body or exact length-constraint solver.')
void=msg('void','戻り値はありません。','No return value.')
body_arg=msg('arg_body','対象の`ChainBody`。`0`なら処理しません。初期化以外は初期化済みの状態を渡します。','Target `ChainBody`; null is ignored. Except for initialization, pass an initialized state.')
data={
'init':('呼び出し側の3配列を関節データに割り当て、節数を0にします。メモリは確保しません。','Attach three caller-owned joint arrays and set the joint count to zero, without allocating memory.',[
('body',body_arg),('x',msg('arg_x','各節のX座標を保持する配列。','Array of joint X coordinates.')),('y',msg('arg_y','各節のY座標を保持する配列。','Array of joint Y coordinates.')),('heading',msg('arg_dirs','各節の向きを保持する配列。','Array of joint headings.')),('capacity',msg('arg_cap','確保済み配列の長さ、1～255。','Allocated array length, 1..255.')),('width',msg('arg_w','折り返す画面の幅、1～256。','Wrapped field width, 1..256.')),('height',msg('arg_h','折り返す画面の高さ、1～256。','Wrapped field height, 1..256.'))],
msg('init_ret','成功なら1、無効な引数なら0です。有効な`body`に対する失敗では`capacity`と`count`を0にし、以後の更新を無効にします。','Return 1 on success or 0 for invalid arguments. Failure with a non-null body sets capacity and count to zero, disabling updates.'),[]),
'reset':('指定した頭の位置から後方へ節を並べ、直線の初期姿勢を作ります。','Build a straight initial pose by placing joints behind the specified head.',[
('body',body_arg),('count',msg('arg_count','頭を含む節数。1～capacity。','Joint count including the head, 1..capacity.')),('head_x',msg('arg_hx','頭のX座標。画面幅に合わせて折り返します。','Head X coordinate, wrapped to the field width.')),('head_y',msg('arg_hy','頭のY座標。画面高さに合わせて折り返します。','Head Y coordinate, wrapped to the field height.')),('heading',msg('arg_heading','頭の16方向の向き。','Head heading in the 16-sector system.'))],
msg('reset_ret','成功なら1。節数が0、容量超過、またはbodyが0なら姿勢を変えず0です。','Return 1 on success. A zero or excessive count, or a null body, returns 0 without changing the pose.'),[
msg('reset_gap','上下左右は4ピクセル間隔です。斜めは整数ベクトル(4,1)、(3,3)、(1,4)などを使うため、実距離は厳密に4ピクセルではありません。画面端をまたぐ姿勢も生成できます。','Cardinal spacing is four pixels. Intermediate headings use integer vectors such as (4,1), (3,3) and (1,4), so Euclidean distance is not exactly four pixels. The initial pose may cross a field edge.')]),
'step':('頭を指定位置へ置き、前の節の後方へ各関節を少しずつ引き寄せます。曲がりが1更新につき1節ずつ後方へ伝わります。','Set the head pose and pull each joint gradually toward a socket behind its predecessor. Heading changes propagate by one joint per update.',[
('body',body_arg),('head_x','chain_body_arg_hx'),('head_y','chain_body_arg_hy'),('heading','chain_body_arg_heading')],void,[
msg('step_algorithm','前の節の更新済み座標から目標位置を求め、画面端をまたぐ最短差分を各軸で計算します。差分0なら移動せず、絶対値1～4なら1ピクセル、5以上なら2ピクセル動きます。ちょうど画面半分の距離では元の差分の符号を保ちます。','Use the predecessor’s updated position to find the target socket, then compute the shortest wrapped displacement on each axis. A zero displacement does not move; magnitude 1..4 moves one pixel, and magnitude 5 or more moves two. At exactly half a field, retain the original displacement sign.'),
msg('step_heading','次の節へ渡すのは、上書きする前に保存した向きです。全身へ頭の新しい向きを一度に配る処理ではありません。空の状態では何もしません。','Pass each joint’s saved, pre-update heading to the next joint, allowing a bend to travel through the body. An empty body is unchanged.'),no_physics]),
'grow':('尾の現在位置と向きを次の空きスロットへ複製し、節数を1増やします。','Copy the tail’s current position and heading into the next free slot and increase the count by one.',[('body',body_arg)],
msg('grow_ret','追加できたら1。空、容量一杯、無効化された状態、またはbodyが0なら0です。','Return 1 if a joint was appended; return 0 for an empty, full, disabled or null body.'),[
msg('grow_overlap','追加直後の尾は前の尾と重なります。以後の`chain_body_step`で徐々に離れます。成長そのものでは頭や他の節を移動させません。','The new tail initially overlaps the previous tail, then separates during subsequent `chain_body_step` calls. Growth itself does not move the head or other joints.')]),
'clear':('節数だけを0にして、同じ配列と画面設定を再利用できるようにします。','Set the joint count to zero while retaining the arrays and field settings.',[('body',body_arg)],void,[
msg('clear_data','配列のバイト列は消去しません。再開には`chain_body_reset`を使います。クリア直後に`chain_body_grow`しても追加されません。','Array bytes are not erased. Use `chain_body_reset` to start again; calling `chain_body_grow` immediately after clearing does not append a joint.')])}
for platform in ['gb','fc']:
    header=REPOS/f'kitaq{platform}/lib/chain.h';library=header.with_suffix('.c')
    declarations={r['name']:r for r in catalog.definitions(header)};definitions={r['name']:r for r in catalog.definitions(library)}
    inventory=SITE/f'reference/{platform}-api.json';doc=json.loads(inventory.read_text(encoding='utf-8'))
    sample_path=f'samples/api-examples/{platform}/chain_body.c';sample=(SITE/sample_path).read_text()
    for suffix,(ja,en,args,returns,notes) in data.items():
        name='chain_body_'+suffix;r=declarations[name]
        r.update(module='chain',definition=definitions[name],availability='implementation',arity_only=False)
        fp=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
        snippet=re.search('// example:'+name+':start\s*\n(.*?)\s*// example:'+name+':end',sample,re.S)[1]
        build=f'.\\kitaq{platform}\\kitaq{platform}.exe .\\kitaq-docs\\'+sample_path.replace('/','\\')+f' -I .\\kitaq{platform}\\lib -I .\\kitaq-docs\\samples -o .\\out\\chain_body.'+('gb --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --cart=mbc5 --romsize=128k' if platform=='gb' else 'nes --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\api-examples\\fc\\chain_body.chr')+' --no-cache --no-disasm'
        contracts[platform+':'+name]=dict(review='chain-body-source-20260922',record_sha256=fp,purpose=[msg(suffix,ja,en)],args=[[a,[b]] for a,b in args],returns=[returns],notes=[setup,storage,directions]+notes,example=dict(program=sample_path,code=snippet,expected=[expected],build='New-Item -ItemType Directory -Force .\\out | Out-Null\n'+build))
        doc['records']=[old for old in doc['records'] if old['name']!=name]+[r]
    doc['records'].sort(key=lambda r:(r['module'],r['name']));inventory.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
for filename,value in [('chain_body_contracts.json',contracts),('chain_body_texts.json',texts)]:
    (HERE/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
print('Ten articulated-chain API contracts authored')
