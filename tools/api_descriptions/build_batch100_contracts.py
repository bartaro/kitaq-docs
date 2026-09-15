"""Bind 100 individually authored library contracts to their exact current source."""
from pathlib import Path
import json,hashlib,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];ROOT=SITE.parents[1];REPOS=ROOT/'publish/github_20260912';
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog
catalog.ROOT=REPOS
plan=json.loads((HERE/'batch100_scope.json').read_text(encoding='utf-8'));authored=json.loads((HERE/'batch100_authored.json').read_text(encoding='utf-8'))
texts=json.loads((HERE/'batch100_texts.json').read_text(encoding='utf-8'));contracts={};sources={};evidence={};modules={}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def msg(key,ja,en):
 key='b100_'+key;texts[key]={'ja':ja,'en':en};return key
group_for={'fixed.h':'math','chain.h':'chain','debug.h':'debug','system.h':'services','scene.h':'services','collision.h':'geometry','rpg.h':'menu_state'}
module_text={
 'fixed':('整数だけで座標や速度の小数部分を扱うQ8.8演算と、矩形・点の当たり判定です。各演算の精度と範囲の制限を確認してください。','Q8.8 arithmetic represents fractional coordinates and speeds using integers, alongside rectangle/point collision tests. Check each operation’s precision and range limits.'),
 'chain':('移動物体の過去の座標をリングバッファに保存するライブラリです。最新点から古い点へ取り出し、追従する物体や軌跡の計算に使えます。','A circular buffer for an object’s past positions. Read from newest to oldest to implement followers or movement trails.'),
 'debug':('名前・値・フレーム番号を固定容量のRAMログに記録します。アサートは情報を残して実行を続ける方式です。','Record names, values and frame tags in a fixed-capacity RAM log. Assertions retain diagnostic information and allow execution to continue.'),
 'system':('フレーム待機回数の管理、待機後のコールバック、CPU割り込みの許可・禁止を扱います。','Manage frame-wait counts, callbacks after waits, and maskable CPU interrupt control.'),
 'scene':('シーン表のenter・update・draw・exitを使い、タイトル画面やプレイ画面の処理を切り替えます。','Dispatch a scene table’s enter, update, draw and exit handlers to switch between screens such as a title and gameplay.'),
 'collision':('FCのワールド座標用に、符号なし16ビット座標の矩形同士・矩形と点の重なりを調べます。','Test box/box and box/point overlap in FC world coordinates using unsigned 16-bit positions.'),
 'rpg':('選択メニューは、決定まで待つ関数と、ゲームループから入力・描画を個別に呼ぶ関数を用意しています。所持品メニューは名前と数量を表示します。','Menus support both blocking selection and separate input/draw calls driven by the game loop. The inventory menu displays item names and quantities.')}
for platform in ['gb','fc']:
 path=SITE/'reference'/(platform+'-api.json');data=json.loads(path.read_text(encoding='utf-8'));records={r['name']:r for r in data['records']}
 for key,filename in plan['apis'].items():
  owner,name=key.split(':')
  if owner!=platform:continue
  header=REPOS/('kitaq'+platform)/'lib'/filename;library=header.with_name('menu.c' if filename=='rpg.h' else header.stem+'.c')
  declarations={r['name']:r for r in catalog.definitions(header)};definitions={r['name']:r for r in catalog.definitions(library)}
  record=records[name]
  if name in declarations:
   for field in ['ret','args','signature','path','line','comment','body']:record[field]=declarations[name][field]
  if record.get('kind')=='macro':
   lines=header.read_text(encoding='utf-8').splitlines();line=next(i for i,l in enumerate(lines) if re.match(r'#define\s+'+re.escape(name)+r'\(',l))
   record['signature']=lines[line];record['line']=line+1;record['implementation_excerpt']=lines[line]
  else:record['definition']=definitions[name]
  record['arity_only']=False
  fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
  contract=json.loads(json.dumps(authored[name]));expected=contract.pop('expected')
  group=group_for[filename]
  if name in ['kq_abs_s16','kq_min_s16','kq_max_s16','kq_clamp_s16']:group='math_limits'
  if name in ['kq_rect_intersect','kq_point_in_rect']:group='geometry'
  if name in ['menu_run','menu_yesno','menu_inventory']:group=name
  program='samples/api-examples/'+platform+'/batch_'+group+'.c';sample=(SITE/program).read_text(encoding='utf-8')
  match=re.search(r'// example:'+name+r':start\s*\n(.*?)\s*// example:'+name+r':end',sample,re.S);assert match,(name,program)
  # Match argument labels to declarations, including the platform-specific menu pointer name.
  actual_args=[re.search(r'([A-Za-z_]\w*)\s*(?:\[[^]]*\])?$',a.strip()).group(1) for a in record['args'].split(',') if a.strip() not in ['', 'void']]
  documented=[a[0] for a in contract['args']]
  renames={'box':'box','x':'px','y':'py'} if name=='nes_box16_contains_point' else {}
  for arg in contract['args']:
   if arg[0] in renames:arg[0]=renames[arg[0]]
  assert sorted(actual_args)==sorted(a[0] for a in contract['args']),(key,actual_args,documented)
  if filename=='chain.h' and name in ['chain_init','chain_clear']:
   contract['notes'].append(msg(platform+'_'+name+'_null','GB版は有効な `chain` ポインターが必要です。' if platform=='gb' else 'FC版は `chain == 0` なら何もしません。','The GB version requires a valid `chain` pointer.' if platform=='gb' else 'The FC version does nothing when `chain == 0`.'))
  if filename=='system.h':
   contract['notes'].append(msg(platform+'_system_hardware','GB版の待機はLCDが停止していると直ちに戻ります。その場合もラッパーのカウンター加算とコールバックは行います。初期化だけではLCDや割り込み元は設定しません。' if platform=='gb' else 'FC版の初期化はNMIを許可します。待機にはNMIが実際に動作する必要があります。CPUのIRQ禁止だけではNMIは止まりません。','On GB, waiting returns immediately with the LCD off, but the wrapper still increments its counter and calls its callback. Initialization alone does not configure the LCD or interrupt sources.' if platform=='gb' else 'FC initialization enables NMI. Waiting requires functioning NMI delivery. Masking CPU IRQs does not stop NMI.'))
  if group=='geometry':
   expected=[msg(platform+'_'+name+'_geometry','座標1単位を1タイルとして、A=(1,1)、B=(5,4)、両方8×6の矩形を表示します。Aだけの領域はA、BだけはB、重なり4×3=12マスはOです。Aの右辺x=9は内部に含みません。CGBではAが赤、Bが青、Oが緑です。','Each coordinate unit occupies one tile. Rectangles A at (1,1) and B at (5,4) are both 8×6. A-only cells show A, B-only cells show B, and the 4×3 overlap shows 12 O cells. A’s right edge x=9 is excluded. On CGB, A is red, B blue and O green.')]
  command='.\\kitaq'+platform+'\\kitaq'+platform+'.exe '
  if platform=='fc' and group=='services':command+='.\\kitaqfc\\lib\\runtime.c '
  command+='.\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaq'+platform+'\\lib -I .\\kitaq-docs\\samples -o .\\out\\batch_'+group+('.gb' if platform=='gb' else '.nes')+' --no-cache --no-disasm'
  command+=(' --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --cart=mbc5 --romsize=64k' if platform=='gb' else ' --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\font.chr')
  contract.update(review='batch100-source-20260915',record_sha256=fingerprint,example={'program':program,'code':match[1],'expected':expected,'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n'+command})
  contracts[key]=contract;evidence[key]={'record_sha256':fingerprint,'header_line':record['line']}
  for source in [header,library]:sources[source.relative_to(REPOS).as_posix()]=sha(source)
  module=header.stem;modules[platform+':'+module]=[msg('module_'+module,*module_text[module])]
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(contracts)==100
for filename,data in [('batch100_contracts.json',contracts),('batch100_texts.json',texts),('batch100_modules.json',modules),('batch100_review_sources.json',{'source_sha256':sources,'records':evidence})]:
 (HERE/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('100 contracts bound to current declarations, bodies and complete examples.')
