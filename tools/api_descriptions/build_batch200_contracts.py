"""Bind the second 100-API batch to reviewed source, examples and bilingual prose."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
if not REPOS.exists():REPOS=SITE.parent
sys.path.insert(0,str(SITE/'tools'));import catalog;catalog.ROOT=REPOS
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
authored=json.loads((HERE/'batch200_authored.json').read_text(encoding='utf-8'))
texts=json.loads((HERE/'batch200_texts.json').read_text(encoding='utf-8'));specs=json.loads((HERE/'batch200_examples.json').read_text(encoding='utf-8'))
sources={};contracts={};records_proof={}
def message(key,ja,en):
 key='b200_example_'+key;texts[key]={'ja':ja,'en':en};return key
def block(source,start):
 masked=catalog.clean(source);i=masked.index('{',start)+1;depth=1
 while depth:depth+=(masked[i]=='{')-(masked[i]=='}');i+=1
 return source[start:i].strip(),source.count('\n',0,start)+1
expected={
'camera':('Q8.8の追従・境界制限・座標変換を学ぶ例です。追従後のX/Yは3584/4096、境界適用後は3072/3584。保留中の背景Xは13、flush後は8です。別の画像では、カメラを(8,16)へ動かし、ワールド(32,32)の32×24矩形が画面(24,16)へ移ることを確認します。','Learn Q8.8 following, clamping and coordinate conversion. Following yields X/Y=3584/4096; bounds give 3072/3584. BG X remains 13 while pending and becomes 8 after flush. The additional image shows a camera at (8,16) moving a 32×24 world rectangle from (32,32) to screen (24,16).'),
'board':('盤面、手順リスト、取り消し記録の役割を分けて学びます。盤面初期化は値9を保持し、容量2のリストの3件目は0で失敗します。popだけでは盤面は8のままで、取り出した記録を盤面へ適用して初めて7に戻ります。','Learn the separate roles of boards, move lists and undo records. Board initialization retains 9; a third append to a two-slot list returns 0. Popping alone leaves the board at 8; explicitly applying the retrieved record restores 7.'),
'scroll_intrinsics':('即時値と保留値、符号付き加算と周回を学ぶ例です。保留中の背景Xは250、flush後は16。ウィンドウWXは23から39へ変わり、背景Xへの−20加算は252、WYへの−40加算は248になります。見た目の例では背景矩形と独立したウィンドウ枠も示します。','Learn immediate versus pending values and wrapping signed additions. BG X is 250 before flush and 16 afterward; WX changes from 23 to 39. Adding −20 to BG X produces 252; adding −40 to WY produces 248. The visual example also shows a background rectangle and an independent window frame.'),
'scroll_wrappers':('Scroll関数を使って、即時設定・保留・flush・加算・表示切り替えを学びます。背景Xはflushで250から16、ウィンドウWXは23から39へ変わります。表示ビットはshow後32、hide後0です。','Use Scroll functions to learn immediate updates, staging, flushing, addition and visibility. Flushing changes BG X from 250 to 16 and WX from 23 to 39. The window bit is 32 after show and 0 after hide.'),
'scroll':('保存した16ビット座標からPPUCTRLとスクロールを作る例です。基本値144、座標(264,272)の適用値は147です。対象(300,260)をアンカー(128,120)に合わせるとカメラは(172,140)になります。別の状態検証ではPPUに実際に書かれた値も確認します。','Learn how saved 16-bit coordinates produce PPUCTRL and scrolling. Base control is 144; applying (264,272) produces control 147. Following target (300,260) at anchor (128,120) gives camera (172,140). Separate state checks inspect actual PPU writes.'),
'tilemap':('5×3マップの(2,1)に障害タイル5を置きます。配列位置は7、範囲外は255。障害に触れる四隅判定は1ですが、40×24の矩形の中央だけに障害がある場合は0です。四隅判定の限界を確認する例です。','Put solid tile 5 at (2,1) in a 5×3 map: its array index is 7 and an outside read returns 255. A corner touching the obstacle returns 1; a 40×24 box enclosing it only in its interior returns 0, demonstrating the corner-only limitation.'),
'palette':('背景の32×32矩形を(16,32)・(80,32)・(144,32)へ赤・青・緑で表示します。スプライトの8×8正方形も(16,96)・(80,96)・(144,96)へ同じ順で表示します。背景とスプライトで別々のパレットを使い、直接転送とキュー経由の転送を確認します。','Show red, blue and green 32×32 background rectangles at (16,32), (80,32) and (144,32), plus 8×8 sprite squares at (16,96), (80,96) and (144,96) in the same color order. Separate background/sprite palettes demonstrate direct and queued uploads.'),
'stream':('キューへ分割してコピーし、消費処理でPPUへ反映する順序を学びます。960バイトのタイル・64バイトの属性・32バイトのパレットを転送し、(16,32)に赤い64×32矩形を表示します。beginだけでは表示は変わりません。','Learn to copy a stream into queue chunks and then consume the queue into the PPU. Transfer 960 tile bytes, 64 attribute bytes and 32 palette bytes to show a red 64×32 rectangle at (16,32). Calling begin alone does not update the display.'),
'split_intrinsics':('画面を3段に分け、背景Xを0→8→16へ変える例です。24×16矩形が画面の(32,16)・(24,80)・(16,112)に並びます。予約イベントはLY=64と104です。DMGでは黒、CGBでは赤で表示します。','Split the screen into three scrolling bands with BG X=0→8→16. Three 24×16 rectangles appear at screen (32,16), (24,80) and (16,112). Events are scheduled at LY=64 and 104. Rectangles are black on DMG and red on CGB.'),
'split_wrappers':('Scrollラッパーで3段の背景スクロールを作ります。LY=64と104でXを8、16へ変え、24×16矩形を(32,16)・(24,80)・(16,112)に表示します。各段の横ずれを画像で確認できます。','Use Scroll wrappers for three background-scroll bands. Events at LY=64 and 104 change X to 8 and 16, positioning 24×16 rectangles at (32,16), (24,80) and (16,112). The image makes each band’s displacement visible.'),
'split_color':('CGBの背景色0を画面途中で切り替えます。本サンプルは通常速度で、上から行0～65が青、66～113が赤、114～143が緑です。イベント予約は0・64・112で、色書き込みと割り込みには遅延があります。DMGにはこのカラーパレット機能はありません。','Change CGB background color zero during the frame. At normal speed, this sample renders rows 0–65 blue, 66–113 red and 114–143 green. Events are scheduled at 0, 64 and 112; interrupt handling and palette access add latency. DMG does not provide these color palettes.')}
for platform in ['gb','fc']:
 path=SITE/'reference'/(platform+'-api.json');data=json.loads(path.read_text(encoding='utf-8'));byname={r['name']:r for r in data['records']}
 for key,auth in authored.items():
  p,name=key.split(':')
  if p!=platform:continue
  record=byname[name];header=REPOS/record['path'];declarations={d['name']:d for d in catalog.definitions(header)}
  for field in ['ret','args','signature','path','line','comment','body']:record[field]=declarations[name][field]
  files=[header]
  if name.startswith('__'):
   compiler=REPOS/'kitaqgb/kitaqgb/CodeGenerator.cs';source=compiler.read_text(encoding='utf-8');excerpt,line=block(source,source.index('if (funcName == "'+name+'")'))
   if '_split_' in name:
    start=source.index('    void AppendScrollHelpersIfUsed(');excerpt+='\n\n'+block(source,start)[0]
   record.update(definition=None,implementation_source={'path':compiler.relative_to(REPOS).as_posix(),'line':line},implementation_excerpt=excerpt);files.append(compiler)
  else:
   library=REPOS/record['definition']['path'];definitions={d['name']:d for d in catalog.definitions(library)};record['definition']=definitions[name];files.append(library)
  record['arity_only']=False
  fingerprint=hashlib.sha256(json.dumps({k:record.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
  contract=json.loads(json.dumps(auth));group=contract.pop('group');spec=next(s for s in specs if s['platform']==p and s['group']==group)
  program=spec['source'];sample=(SITE/program).read_text(encoding='utf-8');match=re.search(r'// example:'+re.escape(name)+r':start\s*\n(.*?)\s*// example:'+re.escape(name)+r':end',sample,re.S);assert match,(key,program)
  actual=[re.search(r'(\w+)\s*$',a.strip()).group(1) for a in record['args'].split(',') if a.strip() not in ['', 'void']];assert actual==[n for n,_ in contract['args']],key
  command='.\\kitaq'+p+'\\kitaq'+p+'.exe '
  if spec.get('runtime'):command+='.\\kitaqfc\\lib\\runtime.c '
  command+='.\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaq'+p+'\\lib -I .\\kitaq-docs\\samples -o .\\out\\batch2_'+group+('.gb' if p=='gb' else '.nes')+' --no-cache --no-disasm'
  command+=(' --profile=dev --rst-disable --stack-bank=fixed --cgb=cgb --cart=mbc5 --romsize=64k' if p=='gb' else ' --mapper=nrom --nes-chr=.\\kitaq-docs\\'+spec.get('chr','samples/font.chr').replace('/','\\'))
  example={'program':program,'code':match[1],'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n'+command,'expected':[message(group,*expected[group])]}
  if group in ['camera','scroll_intrinsics','scroll_wrappers']:
   view=next(s for s in specs if s['group']=='camera_view');example['additional']=[{'program':view['source'],'code':'Camera_Init(&view);\nCamera_Set(&view,2048,4096);\nCamera_ApplyBg(&view);\nScroll_SetWindow(103,80);\nScroll_WindowShow();','expected':[message('camera_view','カメラ(8,16)で赤い32×24矩形は画面(24,16)に表示されます。ウィンドウは画面(96,80)に64×64の青い枠、(112,96)に緑の16×16正方形を表示します。DMGではいずれも黒です。','With camera (8,16), the red 32×24 rectangle appears at screen (24,16). The window shows a blue 64×64 frame at (96,80) and a green 16×16 square at (112,96). All shapes are black on DMG.')],'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n'+command.replace(program.replace('/','\\'),view['source'].replace('/','\\')).replace('batch2_'+group+'.gb','batch2_camera_view.gb')}]
  if platform=='fc' and group=='scroll':
   view=next(s for s in specs if s['group']=='scroll_view')
   viewbuild=command.replace(program.replace('/','\\'),view['source'].replace('/','\\')).replace('batch2_scroll.nes','batch2_scroll_view.nes').replace('samples\\font.chr','samples\\api-examples\\fc\\vram_shapes.chr')+' --mirroring=vertical'
   example['additional']=[{'program':view['source'],'code':'nes_scroll_set_base_ctrl(0);\nnes_scroll_set(264,16);\nnes_scroll_apply();','expected':[message('fc_scroll_view','縦ミラーのNROMでネームテーブル1を表示します。ワールド(288,32)の赤い32×16矩形が、カメラ(264,16)により画面(24,16)へ表示されます。座標bit8によるテーブル選択と、下位バイトのスクロールを画像で確認する例です。','With vertical mirroring on NROM, display nametable 1. A red 32×16 rectangle at world (288,32) appears at screen (24,16) with camera (264,16), demonstrating bit-8 table selection and low-byte scrolling.')],'build':'New-Item -ItemType Directory -Force .\\out | Out-Null\n'+viewbuild}]
  contract.update(review='batch200-source-20260915',record_sha256=fingerprint,example=example);contracts[key]=contract
  records_proof[key]={'record_sha256':fingerprint,'header_line':record['line']}
  for file in files:sources[file.relative_to(REPOS).as_posix()]=sha(file)
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(contracts)==100
for name,value in [('batch200_contracts.json',contracts),('batch200_texts.json',texts),('batch200_review_sources.json',{'source_sha256':sources,'records':records_proof})]:
 (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
print('100 contracts bound to source and full examples.')
