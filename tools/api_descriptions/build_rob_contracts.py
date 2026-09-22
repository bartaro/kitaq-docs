"""Author three optical-mask timing primitives from emitted code and measured timing."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;SITE=HERE.parents[1];REPOS=SITE.parents[1]/'publish/github_20260912'
sys.path.insert(0,str(SITE/'tools'));import catalog
catalog.ROOT=REPOS
texts={};contracts={}
def msg(key,ja,en):
 key='rob_'+key;texts[key]={'ja':ja,'en':en};return key
common=msg('setup','`intrinsics.h`を読み込みます。既定のNMIハンドラーが動き、内部のNMIカウンターが更新される状態で使ってください。NMIが無効、または独自ハンドラーがカウンターを更新しない場合、待機は終わりません。タイムアウトはありません。','Include `intrinsics.h`. The default NMI handler must be running and advancing its counter. Disabled NMI or a custom handler that does not maintain that counter leaves the wait blocked. There is no timeout.')
mask=msg('mask','点灯側はPPUMASKとその保持値を0x1E、消灯側は0にします。以前の描画マスクは復元しません。背景・スプライト・左端描画をまとめて切り替え、グレースケールや色強調の指定も上書きします。','The on phase sets PPUMASK and its software shadow to 0x1E; the off phase sets both to zero. The previous mask is not restored. This changes background, sprite and left-edge rendering together and also replaces grayscale and color-emphasis settings.')
light=msg('light','描画を有効にするだけでは白い画面になりません。明るいタイルとパレット、消灯中に見える暗い背景色を呼び出し側で用意します。サンプルは白い単色タイルと黒い背景色を使い、処理中に画面全体を点滅させます。','Enabling rendering does not create a white screen by itself. Supply bright tiles and palette entries plus a dark backdrop for the off phase. The sample uses solid white tiles and a black backdrop, flashing the whole screen during the operation.')
timing=msg('timing','待機回数はNMIカウンターの変化数です。呼び出し時点から最初のNMIまでは1フレーム未満になる場合があります。前景処理から使い、割り込み内から呼ばないでください。別処理による描画マスクの変更は点滅を乱します。','Wait counts measure NMI-counter changes. The interval from entry to the first NMI may be shorter than one frame. Call from foreground code, not an interrupt. Another routine changing the rendering mask can disturb the pattern.')
scope=msg('scope','画面の明暗と待機のための低水準部品です。ロボット用コマンドの前置きや機種別の命令列、受信確認は生成しません。検証はKUROSAKI上のPPUMASK書き込み順序・NMI回数・画像を対象とし、実機ロボットの受信は確認していません。','These are low-level display-mask and wait primitives. They do not generate a robot command preamble, device-specific command sequence or reception acknowledgement. Verification covers PPUMASK writes, NMI counts and pixels in KUROSAKI; physical robot reception has not been tested.')
void=msg('void','戻り値はありません。指定した待機が終わると呼び出し元へ戻ります。','No return value. Return to the caller after the requested waits complete.')
expected=msg('diagram','実行後、FLASH WAITS 1、PULSE 3 ON / 2 OFF = 5、A5 BYTE WAITS 48と表示します。下の図は0xA5のビット列で、上段が1・0・1・0、下段が0・1・0・1です。1区画は1回の待機、白は描画有効、黒は無効を表します。ビット1は白4区画＋黒2区画、ビット0は白2区画＋黒4区画です。FINAL MASK 0とTIMING CHECKS OKが完了を示します。','After execution, the screen shows FLASH WAITS 1, PULSE 3 ON / 2 OFF = 5 and A5 BYTE WAITS 48. The diagram represents 0xA5: 1,0,1,0 on the upper row and 0,1,0,1 below. Each cell is one wait; white means rendering enabled and black means disabled. A one has four white cells followed by two black cells; a zero has two white followed by four black. FINAL MASK 0 and TIMING CHECKS OK indicate completion.')
data={
'__rob_flash':('描画を点灯側または消灯側へ設定し、NMIカウンターが1回変わるまで待ちます。設定したマスクは戻った後も維持します。','Select the on or off rendering mask and wait for one NMI-counter change. The selected mask remains in effect after return.',[['bright',[msg('bright','0なら消灯、0以外なら点灯です。1だけでなく255なども点灯として扱います。輝度の段階指定ではありません。','Zero selects off; any nonzero byte selects on, including 255. This is not a brightness level.')]]],[]),
'__rob_pulse':('指定回数の点灯待機を行い、続けて指定回数の消灯待機を行います。1組のパルスを作る関数です。','Perform the requested on waits followed by the requested off waits, producing one pulse.',[['on_frames',[msg('on','点灯側の待機回数0～255。0なら点灯側を実行しません。','On-phase wait count, 0..255. Zero skips the on phase.')]],['off_frames',[msg('off','消灯側の待機回数0～255。0なら消灯側を実行しません。合計は最大510回です。','Off-phase wait count, 0..255. Zero skips the off phase. The total can reach 510 waits.')]]],[msg('zero','両方0ならマスクも待機も変更しません。消灯回数が1以上なら終了時のマスクは0、点灯だけなら0x1Eです。','With both counts zero, neither the mask nor timing changes. Any off waits leave mask zero; an on-only pulse leaves 0x1E.')]),
'__rob_send_byte':('1バイトを最上位ビットから8ビットの点滅パターンに変換します。1は点灯4回・消灯2回、0は点灯2回・消灯4回の待機で表し、合計48回のNMI待機を行います。','Encode one byte as eight blink patterns, most-significant bit first. One uses four on waits and two off waits; zero uses two on waits and four off waits. The total is 48 NMI waits.',[['pattern',[msg('pattern','送る8ビットのパターン0～255です。0xA5なら1,0,1,0,0,1,0,1の順になります。チャンネル番号やロボットの操作番号ではありません。','Eight-bit pattern, 0..255. For 0xA5 the order is 1,0,1,0,0,1,0,1. This is not a channel ID or a robot action number.')]]],[msg('final','最後のビットも必ず消灯待機で終わり、終了時のPPUMASKと保持値は0です。固定長の8ビットだけを送り、開始記号や終端記号は加えません。','The last bit also ends with off waits, leaving PPUMASK and its shadow at zero. Send exactly eight bits; no start or end marker is added.')])}
header=REPOS/'kitaqfc/lib/intrinsics.h';compiler=REPOS/'kitaqfc/kitaqfc/CodeGenerator.cs'
decls={r['name']:r for r in catalog.definitions(header)};body=compiler.read_text(encoding='utf-8')
program='samples/api-examples/fc/rob_timing.c';sample=(SITE/program).read_text(encoding='utf-8')
inventory=SITE/'reference/fc-api.json';records=json.loads(inventory.read_text(encoding='utf-8'))
for name,(ja,en,args,notes) in data.items():
 r=dict(decls[name]);start=body.index('EmitHelperStart("'+name+'");');end=body.find('EmitHelperStart(',start+20)
 lines=header.read_text(encoding='utf-8').splitlines();index=next(i for i,line in enumerate(lines) if re.match(r'void\s+'+name+r'\s*\(',line));comment=[]
 for line in reversed(lines[:index]):
  if not line.strip().startswith('//'):break
  comment.insert(0,line.strip()[2:].strip())
 r['comment']='\n'.join(comment)
 if name=='__rob_send_byte':end=body.index('void EmitMidiBitDelay()',start)
 r.update(module='intrinsics',availability='compiler',definition=None,implementation_excerpt=body[start:end].strip(),implementation_source={'path':'kitaqfc/kitaqfc/CodeGenerator.cs','line':body.count('\n',0,start)+1})
 records['records']=[old for old in records['records'] if old['name']!=name]+[r]
 fp=hashlib.sha256(json.dumps({k:r.get(k) for k in ['name','signature','comment','definition','implementation_excerpt']},sort_keys=True).encode()).hexdigest()
 snippet=re.search('// example:'+name+':start\s*\n(.*?)\s*// example:'+name+':end',sample,re.S)[1]
 build='New-Item -ItemType Directory -Force .\\out | Out-Null\n.\\kitaqfc\\kitaqfc.exe .\\kitaq-docs\\'+program.replace('/','\\')+' -I .\\kitaqfc\\lib -I .\\kitaq-docs\\samples --mapper=nrom --nes-chr=.\\kitaq-docs\\samples\\api-examples\\fc\\vram_shapes.chr -o .\\out\\rob_timing.nes --no-cache --no-disasm'
 contracts['fc:'+name]=dict(review='rob-source-20260922',record_sha256=fp,purpose=[msg(name,ja,en)],args=args,returns=[void],notes=notes+[common,mask,light,timing,scope],example=dict(program=program,code=snippet,expected=[expected],build=build))
records['records'].sort(key=lambda r:(r['module'],r['name']));inventory.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
for name,data in [('rob_contracts.json',contracts),('rob_texts.json',texts)]:
 (HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Three individual optical-mask contracts authored.')
