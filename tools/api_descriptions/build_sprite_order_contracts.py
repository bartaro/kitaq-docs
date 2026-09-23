"""Author independent sprite-order contracts and add only their catalog entries."""
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1]
REPOS=SITE.parents[1]/'publish/github_20260912'
sys.path.insert(0,str(SITE/'tools'))
import catalog
catalog.ROOT=REPOS
texts={};contracts={}
def msg(key,ja,en):
    key='sprite_order_'+key;texts[key]={'ja':ja,'en':en};return key
state=msg('state','呼び出し側で確保した`SpriteOrder`のアドレス。初回は`init`で設定し、処理中は前景コードだけで操作してください。','Address of a caller-owned `SpriteOrder`. Initialize it before use and keep its updates in foreground code.')
setup=msg('setup','`sprite_order.h`を読み込み、`sprite_order.c`を1回だけコンパイルします。初期化後は、各フレームで`begin`、必要な回数の`push`、`build`の順に呼びます。このライブラリだけなら` sprite.c`やグローバル変数の定義は不要です。','Include `sprite_order.h` and compile `sprite_order.c` exactly once. After initialization, call `begin`, then `push` for each candidate, then `build` each frame. The ordering library itself does not require `sprite.c` or any global variable definitions.')
setup_ja=texts[setup]['ja'];texts[setup]['ja']=setup_ja.replace('` sprite.c`','`sprite.c`')
hardware=msg('hardware','ハードウェアは同じ走査線にかかる最初の10個をOAM順に選びます。低いpriority値のものを先に置くことで、混雑時にも残したい物体を優先します。ただし、同じ優先度の物体へ均等な表示頻度を保証する方式ではありません。優先物体だけで10個に達すれば、その行の下位の物体は表示されません。','Hardware selects the first ten objects intersecting each scanline in OAM order. Putting lower priority values first protects important objects when a line is crowded. Rotation does not guarantee equal display frequency within a priority band. If high-priority objects fill all ten slots, lower-priority objects on that line remain invisible.')
overlap=msg('overlap','ここでのpriorityは選択順です。背景より後ろに描く属性とは別です。DMGでは、選択された物体同士の重なりはX座標の小さいものが優先され、Xが同じときにOAM順で決まります。CGBの通常のカラー用重なり順はOAM順ですが、OPRIでDMG互換の順序を選ぶ設定には影響しません。このライブラリはハードウェアの優先規則を変更しません。','The priority argument controls selection order, independently of the behind-background attribute. On DMG, overlapping selected objects favor the smaller X coordinate, with OAM order breaking ties. Normal CGB color-mode overlap uses OAM order, but a DMG-style ordering configuration selected through OPRI still applies. This library does not change hardware priority rules.')
height_note=msg('height_note','高さは全物体で共通です。LCDCの8×8／8×16設定に合わせて8または16を指定してください。ライブラリはLCDCを設定しません。8×16モードでは、ハードウェアがタイル番号の最下位ビットを無視します。','Height is shared by all objects. Pass 8 or 16 to match LCDC’s 8×8/8×16 setting; the library does not configure LCDC. Hardware ignores the tile number’s low bit in 8×16 mode.')
integration=msg('integration','`SpriteOrderOamEntry`はY、X、tile、flagsの4バイトです。`sprite.h`の影OAMを使う場合は`(SpriteOrderOamEntry*)kq_sprite_oam`へ出力できます。ただし`SPRITE_MAX`は標準の40とし、`sprite_alloc`の割当状態と並び替えを混在させないでください。`build`は割当管理情報を更新しません。','`SpriteOrderOamEntry` contains four bytes: Y, X, tile and flags. To use the shadow OAM from `sprite.h`, write to `(SpriteOrderOamEntry*)kq_sprite_oam`. Keep the standard `SPRITE_MAX` of 40 and do not mix allocator-managed slot identities with reordered output: `build` does not update allocator bookkeeping.')
transfer=msg('transfer','`build`はRAMへの書き込みだけです。出力配列は160バイト必要で、状態や登録用配列と重ねてはいけません。OAM DMAに使うバッファは256バイト境界に配置します。書き込みを完了してからVBlank中に転送し、途中の配列を割り込みから転送しないでください。サンプルでは` sprite_flush_oam`を使います。','`build` only writes RAM. Provide a 160-byte output array that does not overlap the state or submission storage. A buffer used for OAM DMA must start on a 256-byte boundary. Finish building before transferring during VBlank; an interrupt must not transfer a half-built buffer. The sample uses `sprite_flush_oam`.')
texts[transfer]['ja']=texts[transfer]['ja'].replace('` sprite_flush_oam`','`sprite_flush_oam`')
cost=msg('cost','登録は1個ずつ一定量の処理で行い、出力時は最大4回、登録配列を走査して160バイトの影OAMを初期化します。配列自体の並び替えや一時ソート配列は不要です。255件を毎フレーム扱える速度を保証するものではありません。実際のゲームで必要な候補数に絞ってください。','Each submission takes a bounded amount of work. Building clears 160 bytes of shadow OAM and scans the submission array up to four times. It neither sorts that array nor needs a temporary sorting buffer. This is not a guarantee that 255 candidates fit a game’s per-frame budget; submit only the candidates the scene needs.')
expected=msg('expected','このサンプルは、同じ走査線に14個を置いたときの表示選択を確認するものです。左のHIGHにある菱形2個が高優先度、右のNORMALの四角12個が通常優先度です。CGBでは菱形が赤、四角が青、DMGでは灰色と黒になります。菱形は常に2個とも表示され、四角は8個だけ表示されます。下の0～Bが四角の位置番号です。PHASE 04では4～B、PHASE 08では8～Bと0～3が見えます。通常ビルドは60回のフレーム待機ごとにPHASEを進めます。掲載画像は同じプログラムの位相を固定したもので、動作版でも表示する四角の変化を確認しています。','This lesson shows scanline selection with fourteen objects on one row. The two diamonds under HIGH have high priority; the twelve squares under NORMAL have normal priority. CGB uses red diamonds and blue squares; DMG uses gray and black. Both diamonds remain visible, while only eight squares appear. The labels 0..B identify square positions. PHASE 04 shows 4..B; PHASE 08 shows 8..B and 0..3. The normal build advances PHASE after every 60 frame waits. The published captures fix the phase in the same program; the running version was also checked for changing square selection.')
module=msg('module','`sprite_order`は、重要な物体を先に選びつつ、同じ優先度の物体のOAM順を交替させるライブラリです。最大255件から画面全体で最大40件を出力し、走査線あたり10個という制限への対処を助けます。既存の`sprite`はスロットの確保やDMA転送を担当し、`sprite_order`は表示候補の選択順を担当します。','`sprite_order` places important objects first and rotates OAM order among objects with the same priority. It emits up to 40 objects from at most 255 candidates, helping manage the ten-object scanline limit. The existing `sprite` library handles slot allocation and DMA; `sprite_order` handles candidate selection order.')
program='samples/api-examples/gb/sprite_order_demo.c'
source=(SITE/program).read_text(encoding='utf-8')
build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqgb\\kitaqgb.exe .\\kitaq-docs\\samples\\api-examples\\gb\\sprite_order_demo.c -I .\\kitaqgb\\lib -I .\\kitaq-docs\\samples -o .\\out\\sprite_order_demo.gb --cgb=cgb --profile=dev --rst-disable --stack-bank=fixed --no-cache --no-disasm'
header=REPOS/'kitaqgb/lib/sprite_order.h';library=header.with_suffix('.c')
definitions={r['name']:r for r in catalog.definitions(library)}
rows={r['name']:r for r in catalog.definitions(header)}
def add(name,purpose,args,returns,notes,code):
    assert code in source and name+'(' in code
    r=rows[name];r.update(module='sprite_order',definition=definitions[name],availability='implementation',arity_only=False)
    fp=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
    contracts['gb:'+name]=dict(review='sprite-order-source-20260923',record_sha256=fp,purpose=[purpose],args=args,returns=[returns],notes=notes,
        example=dict(program=program,code=code,build=build,expected=[expected]))

add('sprite_order_init',msg('init','表示順を管理する状態に登録用配列を関連付け、登録数と回転位相を0に戻します。新しいシーンや配列へ切り替えるときに使います。','Bind submission storage to an ordering state and reset the count and rotation phase. Use this when starting a scene or changing storage.'),
    [['order',[state]],['items',[msg('items','書き込み可能な`SpriteOrderItem`配列。1件5バイトで、capacity件分を確保し、使用中は有効に保ってください。','Writable `SpriteOrderItem` array, five bytes per item. Allocate capacity entries and keep the storage valid throughout use.')]],
     ['capacity',[msg('capacity','配列の件数1～255。バイト数やハードウェアの表示枠数ではありません。','Array capacity, 1..255 items; neither a byte count nor the hardware slot count.')]],
     ['height',[height_note]]],msg('init_return','成功は1、itemsがNULL、capacityが0、heightが8/16以外、またはorderがNULLなら0です。orderが非NULLの失敗ではitems=NULL、capacity=count=phase=0、height=8の無効状態になります。items配列は変更しません。','Return 1 on success, or 0 for null items, zero capacity, a height other than 8/16, or null order. With a non-null order, failure leaves it disabled: items=NULL, capacity=count=phase=0 and height=8. The item array is untouched.'),
    [setup],'sprite_init();sprite_order_init(&order_demo,order_demo_items,14,8);')
add('sprite_order_begin',msg('begin','次のフレームの表示候補を登録するため、登録数を0にします。配列、高さ、回転位相を保持するため、毎フレームinitを呼ぶ場合と違って表示順の交替が続きます。','Clear the submission count for a new frame while retaining storage, height and rotation phase. Unlike reinitializing every frame, this lets rotation continue.'),
    [['order',[state]]],msg('begin_return','戻り値はありません。orderがNULLなら何もしません。古い配列のバイト列や出力済みOAMは消去しません。','No return value. Null order is ignored. Old item bytes and already-built OAM are not erased.'),
    [setup,hardware],'sprite_order_begin(&order_demo);')
add('sprite_order_push',msg('push','画面に少なくとも1ピクセル分かかるスプライトを1件登録します。画面外の物体は先に除外し、OAMの選択枠を無駄に使わないようにします。','Submit one sprite that intersects the visible screen by at least one pixel. Fully off-screen candidates are rejected before they can consume OAM selection slots.'),
    [['order',[state]],['x',[msg('x','画面左上を原点とする符号付きX座標。左端が−7～159なら受け付けます。−8以下または160以上は全体が画面外です。保存時に8を足してOAM座標へ変換します。','Signed screen X measured from the top left. Left edges −7..159 are accepted; at most −8 or at least 160 is fully off-screen. Storage adds 8 for OAM coordinates.')]],
     ['y',[msg('y','画面左上を原点とする符号付きY座標。高さ8なら−7～143、高さ16なら−15～143を受け付けます。保存時に16を足します。','Signed screen Y measured from the top left. Accepted range is −7..143 for height 8, or −15..143 for height 16. Storage adds 16 for OAM coordinates.')]],
     ['tile',[msg('tile','タイル番号0～255。そのまま保存します。8×16モードの扱いはheightの説明を参照してください。','Tile number, 0..255, stored unchanged. See the height notes for 8×16 mode.')]],
     ['flags',[msg('flags','ハードウェア属性の1バイト。左右・上下反転、背景優先、DMG/CGBパレット、CGB VRAMバンクなどを指定し、そのまま保存します。','Hardware attribute byte, stored unchanged: flips, behind-background priority, DMG/CGB palette and CGB VRAM bank bits retain their usual meanings.')]],
     ['priority',[msg('priority','ソフトウェアの選択優先度0～3。0が最優先です。4以上は登録を拒否します。ハードウェア属性のflagsとは別の値です。','Software selection priority, 0..3, with zero first. Values at least four are rejected. This is separate from the hardware flags byte.')]]],
    msg('push_return','登録できれば1を返しcountを1増やします。NULLまたは無効な状態、高さ不正、満杯、不正なpriority、完全な画面外なら0で、登録配列とcountは変わりません。','Return 1 and increment count when accepted. Return 0 without changing items or count for a null/disabled state, invalid height, full storage, invalid priority or a fully off-screen object.'),
    [height_note,hardware,overlap],'sprite_order_push(&order_demo,8,64,128,0,0);')
add('sprite_order_build',msg('build','登録済みの候補から、優先度と回転位相に従って160バイトの影OAMを作ります。使わない枠を全て0にして隠し、次回の位相へ進めます。登録用配列の順序は変えません。','Build 160 bytes of shadow OAM from the submitted candidates in priority and cyclic order. Hide every unused slot by zeroing it, then advance the phase for the next build. Submission storage is not reordered.'),
    [['order',[state]],['output',[msg('output','`SpriteOrderOamEntry`40件分の書き込み可能な配列。limitが0や40未満でも160バイト全体へ書き込みます。','Writable array of 40 `SpriteOrderOamEntry` values. The function writes all 160 bytes even when limit is zero or below 40.')]],
     ['limit',[msg('limit','出力する最大件数0～40。40より大きい値は40に制限します。走査線ごとの上限指定ではなく、OAM全体の件数です。','Maximum emitted count, 0..40; larger values are clamped to 40. This limits the whole OAM, not each scanline.')]]],
    msg('build_return','出力した件数0～40を返します。正常な空の登録列では全枠を消去しphase=0にします。空でなければphaseをcountで折り返して順序の開始位置に使い、最後に1進めて再び折り返します。limit=0でも位相は進みます。NULLのorder/output、無効な状態、高さ不正、count>capacityでは0を返し、出力とphaseを変更しません。','Return the emitted count, 0..40. A valid empty queue clears all slots and sets phase=0. Otherwise normalize phase modulo count, use that cyclic starting position within each ascending priority band, then increment and wrap phase. A zero limit still advances phase. Null order/output, disabled state, invalid height or count>capacity returns zero without changing output or phase.'),
    [hardware,overlap,integration,transfer,cost],'order_demo_state[1]=sprite_order_build(&order_demo,(SpriteOrderOamEntry*)kq_sprite_oam,40);')

inventory=SITE/'reference/gb-api.json';doc=json.loads(inventory.read_text(encoding='utf-8'))
doc['records']=[r for r in doc['records'] if r['name'] not in rows]+list(rows.values())
doc['records'].sort(key=lambda r:(r['module'],r['name']))
header_path=header.relative_to(REPOS).as_posix()
if header_path not in doc['headers']:doc['headers'].append(header_path);doc['headers'].sort()
inventory.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
for filename,value in [('sprite_order_contracts.json',contracts),('sprite_order_texts.json',texts),('sprite_order_modules.json',{'gb:sprite_order':[module,setup,hardware,integration]})]:
    (HERE/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
print('Four sprite-order API contracts authored in JA/EN')
