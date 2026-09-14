from pathlib import Path
import re,json,html,shutil
from collect import ROOT,SITE,read
from chapters import TEXT,BOOKS
from languages import language_nav
E=html.escape
def slug(t):return re.sub(r'[^\w-]+','-',t).strip('-')
def code(t,lang='c'):return '<div class="codebox"><span class="lang">'+lang+'</span><button class="copy" type="button">コピー</button><pre><code>'+E(t.strip())+'</code></pre></div>'
def inline(t):
 stash=[]
 def protect(m):stash.append('<code>'+E(m[1])+'</code>');return '\x00'+str(len(stash)-1)+'\x00'
 t=re.sub(r'`([^`]+)`',protect,t);t=E(t)
 t=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',t)
 t=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',t)
 return re.sub('\x00(\d+)\x00',lambda m:stash[int(m[1])],t)
def md(t):
 lines=t.strip().splitlines();out=[];i=0
 while i<len(lines):
  s=lines[i]
  if not s.strip():i+=1;continue
  if s.startswith('```'):
   lang=s[3:] or 'text';block=[];i+=1
   while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
   out.append(code('\n'.join(block),lang));i+=1;continue
  if s.startswith('## '):
   title=s[3:];out.append('<h2 id="'+slug(title)+'">'+inline(title)+'</h2>');i+=1;continue
  if s.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].startswith('|'):
    row=lines[i];i+=1
    if re.match(r'^\|[\s:|\-]+$',row):continue
    # Preserve table separator characters inside inline code.
    parts=re.split(r'\|(?=(?:[^`]*`[^`]*`)*[^`]*$)',row.strip('|'))
    rows.append(parts)
   out.append('<div class="tablewrap"><table>')
   for j,row in enumerate(rows):
    tag='th' if j==0 else 'td';out.append('<tr>'+''.join('<'+tag+'>'+inline(c.strip())+'</'+tag+'>' for c in row)+'</tr>')
   out.append('</table></div>');continue
  if re.match(r'^\d+\. ',s):
   out.append('<ol>')
   while i<len(lines) and re.match(r'^\d+\. ',lines[i]):out.append('<li>'+inline(re.sub(r'^\d+\. ','',lines[i]))+'</li>');i+=1
   out.append('</ol>');continue
  para=[]
  while i<len(lines) and lines[i].strip() and not lines[i].startswith(('## ','```','|')) and not re.match(r'^\d+\. ',lines[i]):para.append(lines[i]);i+=1
  out.append('<p>'+inline(' '.join(para))+'</p>')
 return '\n'.join(out)

MODULES={
'system':'起動、フレーム数、待機と割り込み', 'input':'ボタンの現在値・押下・解放・リピート', 'sprite':'OBJの確保、配置、メタスプライト、アニメーション',
'vram':'VRAM更新の予約と転送','fixed':'Q8.8固定小数点と矩形','scene':'シーンの登録、変更と更新','entity':'固定配列のオブジェクトプール',
'chain':'座標履歴を保存するリングバッファ','audio':'音楽と効果音・音源制御','audio_vblank':'VBlank IRQによる音楽再生','rpg':'乱数、文字、マップ、セーブ、RPG/ADV/SLG',
'bank':'バンク番号付きのコード・データアクセス','asset':'素材IDとデータ記述表','debug':'RAMに値とアサートを記録','cgb_palette':'CGBのBG/OBJパレット',
'cgb_tile':'CGBのタイル番号と属性','scroll':'背景・ウィンドウ・分割スクロール','raster':'帯・行単位のスクロール表','camera':'世界座標と表示範囲の変換',
'link':'シリアル通信と論理パケット','link_dmg07':'DMG-07の外部クロック通信','slg':'盤面、手の一覧とundo','physics2d':'2Dの運動と衝突',
'physics2d_circle':'円同士の物理計算','physics3d':'3DのAABB物理計算','wire3d':'DMG向けワイヤーフレーム','wire3d_cgb':'CGB専用の色付きワイヤーフレーム',
'dmg3d':'DMGの128×120モノクロワイヤーフレーム','danmaku':'弾プール・扇状生成・被弾とグレイズ','intrinsics':'コンパイラ組み込み命令','core':'基本の整数型',
'fc':'ライブラリをまとめて読むヘッダー','runtime':'NMI、OAM、PPU転送のCヘルパー','ppu':'PPU画面操作の宣言','ppu_direct':'直接PPUへ書く操作',
'vram_queue':'NMIで処理するVRAMキュー','palette':'NESのパレット操作','attribute':'ネームテーブル属性','tilemap':'タイルマップの矩形操作',
'nametable_asset':'ネームテーブル用素材と配置','metasprite':'複数OBJをまとめた画像','oam':'OAMシャドウ操作','oam_fair':'優先順位付きスプライト交替表示',
'oam_fair_impl':'スプライト交替表示の実装','actor':'ゲームアクターの配列','collision':'矩形等の接触判定','input_repeat':'押し続け入力のリピート',
'pad':'NESコントローラー入力','zapper':'光線銃の入力窓口','keyboard':'キーボードの走査','rob':'ROB制御','mic':'マイク入力','midi':'MIDI入出力の窓口',
'mapper':'マッパーのバンクとIRQ','fds':'FDSディスク操作','fds_file':'FDSファイルのロード','fds_overlay':'FDSのオーバーレイコード',
'fds_save':'FDS保存の宣言','fds_sound':'FDS波形音源','vrc6_sound':'VRC6拡張音源','vrc7_sound':'VRC7 FM音源',
'math_fast':'高速な整数計算','math_fixed':'固定小数点計算の組み込み窓口','math_lut':'ルックアップテーブル','nes_game':'ゲーム向け操作名のマクロ','wire3d_dmg':'DMG向けワイヤーフレーム',
}
SPECIAL={
'__readpadex':'下位8ビットは現在のキー、上位8ビットは新規押下。前回値を渡してエッジを求めます。',
'__wait_vblank':'次の描画更新に合わせるための待機です。待機の重複に注意してください。',
'__memcpy':'転送元から転送先へlenバイトを複製します。領域の大きさとバンクの有効性を呼び出し側で保証します。',
'__memset':'指定領域を同じバイト値で埋めます。lenはバイト数です。',
'__bankof':'シンボルの配置バンクを得ます。任意の数値アドレスを渡す操作と区別します。',
'input_init':'前回値・現在値・エッジ・リピート状態を初期化します。起動時に一度呼びます。',
'input_update':'パッドを読み、押下と解放を更新します。通常は1ゲームフレームに1回です。',
'input_down':'maskで選んだボタンが現在押されているか調べます。',
'input_pressed':'maskで選んだボタンが今回新たに押されたか調べます。',
'input_released':'maskで選んだボタンが今回離されたか調べます。',
'input_repeat':'押した瞬間と所定間隔のリピートを調べます。',
'Audio_Init':'音源・ドライバー状態を初期化します。APUレジスター定義を先に結合してください。',
'Audio_Update':'音楽・効果音・フェードを進めます。通常は1フレーム1回呼びます。',
'Audio_PlayMusic':'バンク番号と曲データを指定して音楽を開始します。曲はドライバーのストリーム形式です。',
'Audio_PlaySFX':'効果音を指定優先度で開始します。現在見えているROMバンクを記録します。',
'Audio_SetPaused':'音楽／効果音のドライバー一時停止状態を変更します。ゲーム全体の停止処理はゲーム側に必要です。',
'system_set_vblank_callback':'GBでは待機関数内から協調的に呼び出します。FCでは現実装は保存のみで、自動実行しません。',
'sprite_alloc':'未使用スプライト枠を確保します。戻り値が失敗値でないことを確認して使用します。',
'entity_create':'空いたオブジェクトを初期化してIDを返します。空きがなければ0xFFです。',
'entity_get':'有効なIDのオブジェクトを返します。範囲外や無効なIDではNULLを確認してください。',
'fix_from_int':'整数をQ8.8へ変換します。1は256に相当します。',
'fix_to_int':'Q8.8から整数部分を得ます。負数の丸めは実装を参照してください。',
'fix_mul':'Q8.8同士を掛け、Q8.8の結果へ戻します。入力範囲に注意してください。',
'fix_div':'Q8.8の除算です。ゼロ除算を避け、表現範囲を超えない値を使います。',
'cgb_rgb15':'各0～31のRGB成分をGBカラーの15ビット形式へ詰めます。',
'cgb_bg_rgb':'BGのパレット番号と色番号を選び、各0～31のRGBを設定します。',
'cgb_obj_rgb':'OBJのパレット番号と色番号を選び、各0～31のRGBを設定します。',
'__nmi_wait':'NMIによるフレーム進行を待ちます。NMIを有効にして使用します。',
'__vramq_commit':'準備したVRAM更新をNMI側へ渡すためのcommitです。',
'__vramq_exec':'キューの内容をPPUへ反映します。通常はNMI側の安全な時間に実行します。',
'__ppu_off':'画面描画を止め、初期ロードなどのPPU直接更新に備えます。',
'__scroll_set':'NESのスクロール位置を設定します。PPU転送後のスクロール復元にも使います。',
}
def purpose(r):
 if r['name'] in SPECIAL:return SPECIAL[r['name']]
 module=MODULES.get(r['module'],'関連機能')
 n=r['name'].lower()
 verbs=[('init','初期状態を準備'),('clear','内容や状態を消去'),('reset','状態をリセット'),('get','値や状態を取得'),('read','値を読み取り'),('write','値を書き込み'),('set','値や動作条件を設定'),('draw','描画データを作成'),('load','データを読み込み'),('save','データを保存'),('update','状態を更新'),('step','処理を1ステップ進め'),('wait','条件の成立を待機'),('enable','機能を有効化'),('disable','機能を無効化'),('copy','データを複製'),('fill','領域を値で埋め'),('flush','蓄積した更新を反映'),('count','件数を取得'),('push','データを追加'),('pop','データを取り出し')]
 v=next((v for k,v in verbs if k in n),'引数に対応する処理を実行')
 return module+'に関するAPIです。'+v+'します。正確な引数の単位・終端・戻り値の条件は、以下の宣言・原注記・実装に従います。'

def page(key,title,subtitle,body):
 depth='../' if '/' in key else ''
 nav='<a href="'+depth+'index.html">総合目次</a>'+''.join('<a '+('aria-current="page" ' if key==k else '')+'href="'+depth+k+'.html"><b>'+num+'</b> '+E(name)+'</a>' for k,num,name,sub in BOOKS)
 headings=re.findall(r'<h2 id="([^"]+)">(.*?)</h2>',body)
 toc=''.join('<a href="#'+id+'">'+re.sub('<[^>]+>','',t)+'</a>' for id,t in headings)
 text='''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><title>'''+E(title)+''' — KITAQ SERIES MANUAL</title><link rel="stylesheet" href="'''+depth+'''assets/manual.css"></head><body><a class="skip" href="#main">本文へ</a><header class="mast"><a href="'''+depth+'''index.html">KITAQ <span>DEVELOPMENT SYSTEM</span></a><div>USER'S MANUAL <b>2026.09</b></div></header><div class="layout"><aside><nav aria-label="巻の選択">'''+nav+'''</nav><label class="searchlabel" for="search">この巻を検索</label><input type="search" id="search" placeholder="例：入力 / __memcpy"><p id="search-status" role="status"></p><nav class="toc" aria-label="この巻の目次">'''+toc+'''</nav><button class="print" type="button">この巻を印刷</button></aside><main id="main"><div class="cover"><p class="eyebrow">KITAQ SERIES • REFERENCE EDITION</p><h1>'''+E(title)+'''</h1><p class="subtitle">'''+E(subtitle)+'''</p><div class="edition">初めての一行から、実行・観測・再テストまで。<br>ローカルソース採取：2026年9月14日</div></div>'''+body+'''<footer>2026-09-14版 • <a href="'''+depth+'''index.html">総合目次</a> • <a href="'''+depth+'''verification.html">検証記録</a> • <a href="'''+depth+'''reference/inventory.json">版の指紋</a><br>サンプルのビルド・エミュレータ実行・期待値照合は別項目として記録します。</footer></main></div><script src="'''+depth+'''assets/manual.js"></script></body></html>'''
 text=text.replace('</header>', '</header>'+language_nav(key,'ja','言語'), 1)
 dest=SITE/(key+'.html');dest.parent.mkdir(exist_ok=True,parents=True);dest.write_text(text.replace('\r\n','\n'),encoding='utf-8',newline='\n')

def samples_section(platform,manifest):
 out=['<h2 id="samples">完全なサンプルプログラム</h2><p>各プログラムの本体、共通ヘッダー、指定ascii.cとその変換素材を同梱しています。説明中のm_*は本書専用ヘルパーです。ビルドと操作・期待結果を一組として参照してください。</p><p><a href="samples/build.ps1">一括ビルド用PowerShell</a> ／ <a href="verification.html">実行結果・検証画像</a></p>']
 for d in manifest:
  if d['platform']!=platform:continue
  libprefix='kitaqgb/lib' if platform=='gb' else 'kitaqfc/lib'
  exe='.\\kitaqgb\\kitaqgb.exe' if platform=='gb' else '.\\kitaqfc\\kitaqfc.exe'
  cmd=exe+' '+' '.join(libprefix+'/'+f for f in d['libs'])+' kitaq-docs/samples/'+d['file']+' -I '+libprefix+' -I kitaq-docs/samples -o out/'+d['id']+('.gb' if platform=='gb' else '.nes')
  cmd+=' --profile=dev --rst-disable --stack-bank=fixed' if platform=='gb' else ' --mapper=nrom --nes-chr=kitaq-docs/samples/font.chr'
  cmd+=' '+' '.join(d['options'])

  if d.get('known_issue'): cmd='# 既知のビルド制限：'+d['known_issue']+'\n'+cmd
  out.append('<details class="sample searchable" id="sample-'+d['id']+'"><summary>'+E(d['title'])+' <code>'+d['file']+'</code></summary><p>期待結果：'+E(d['expected'])+'</p><p><a href="samples/'+d['file']+'" download>ソースを保存</a> ／ <a href="verification.html#'+d['id']+'">検証状況</a></p>'+code(cmd,'powershell')+code(read(SITE/'samples'/d['file']))+'</details>')
 return ''.join(out)

def api_section(platform,intrinsic):
 data=json.loads(read(SITE/'reference'/(platform+'-api.json')))
 records=[r for r in data['records'] if r['name'].startswith('__')==intrinsic]
 out=['<h2 id="api">'+('組み込み命令' if intrinsic else 'ライブラリAPI')+'辞典</h2><p>全'+str(len(records))+'項目。項目名を開くと書式・引数・原注記・使用例を読めます。「呼び出し断片」は単独ROMではなく周辺の初期化が必要です。「引数受け渡し例」は、引数を用意した上位コードから使うための関数例で、実機器の操作確認を意味しません。</p>']
 for mod in sorted(set(r['module'] for r in records)):
  out.append('<h3 id="module-'+mod+'">'+mod+'.h — '+E(MODULES.get(mod,'組み込み機能'))+'</h3>')
  for r in sorted((r for r in records if r['module']==mod),key=lambda r:r['name'].lower()):
   ident='api-'+r['name'];status={'compiler':'コンパイラ組み込み','implementation':'実装あり','declaration':'宣言のみ・本体未検出','macro':'マクロ'}[r['availability']]
   out.append('<details class="api searchable" id="'+ident+'"><summary><code>'+E(r['name'])+'</code><span class="badge">'+status+'</span></summary><p>'+E(purpose(r))+'</p>'+code(r['signature']))
   if r.get('arity_only'):out.append('<p class="note">引数個数をコード生成部から採取した書式です。arg0等は説明用の名前で、型宣言ではありません。呼び出し例と実装の要求を参照してください。</p>')
   elif r['args'] and r['args']!='void':
    out.append('<p><b>引数（左から順）：</b>'+E(r['args'])+'。配列・ポインタでは必要な領域を用意し、処理が終わるまで有効に保ちます。</p>')
   if r['ret'] not in ('','void','macro'):out.append('<p><b>戻り値の型：</b><code>'+E(r['ret'])+'</code>。意味・成功値・失敗値は原注記と実装のreturn条件を参照してください。</p>')
   if r['comment']:out.append('<div class="original"><b>宣言に付属する原注記</b><pre>'+E(r['comment'])+'</pre></div>')
   if r['availability']=='declaration':out.append('<p class="note">公開ヘッダーに宣言がありますが、この採取範囲では対応する本体が見つかりません。リンク可能・動作済みとは扱いません。利用前に提供単位を確認してください。</p>')
   ex=r.get('example')
   if ex:
    out.append('<h4>呼び出し例（周辺コードの断片）</h4>'+code(ex['code'])+'<p class="source">出典：'+E(ex['path'])+':'+str(ex['line'])+'</p>')
    if 'kitaq-docs/samples/' in ex['path']:
     f=ex['path'].split('/')[-1];out.append('<p><a href="samples/'+f+'">この例の完全なプログラム</a></p>')
   else:
    out.append('<h4>引数受け渡し例</h4>'+code(r.get('new_example',r['signature']))+'<p>オブジェクトの初期化、バッファの大きさ、ROMバンク、機器状態は上位コードで準備します。この関数断片単体は実行確認していません。</p>')
    folder=SITE/'samples/api-fragments'/platform;folder.mkdir(parents=True,exist_ok=True)
    file=folder/(r['name']+'.c');file.write_text('// Usage fragment, not a standalone ROM.\n// Declaration source: '+r['path']+'\n'+r.get('new_example',r['signature'])+'\n',encoding='utf-8')
    out.append('<p><a href="samples/api-fragments/'+platform+'/'+r['name']+'.c" download>この断片を保存</a></p>')
   d=r.get('definition')
   if d:
    out.append('<p class="source"><b>結合する本体：</b><code>'+E(d['path'])+'</code>:'+str(d['line'])+'。別の関数を呼ぶ場合はその提供単位も必要です。</p><details><summary>現在の実装を読む</summary>'+code(d['body'])+'</details>')
   elif r.get('implementation_excerpt'):out.append('<details><summary>引数を検査するコード生成部</summary>'+code(r['implementation_excerpt'],'csharp')+'</details>')
   out.append('<p class="source">宣言・識別子の出典：'+E(r['path'])+':'+str(r['line'])+'</p></details>')
 return ''.join(out)

CLI_EXAMPLES={
'kurosaki':{
'battery-export':('状態から生のバッテリーRAMを取り出す','battery-export out/game.nes out/state.kss.json --out out/save.sav'),
'battery-run':('保存RAMだけを読み込んで電源投入から実行する','battery-run out/game.nes --sav out/save.sav --frames 120 --png out/loaded.png --save-out out/next.sav'),
'inspect-rom':('ROMヘッダーを調べる','inspect-rom out/game.nes --json out/rom.json'),
'audit-board':('基板条件を検査する','audit-board out/game.nes --expected-board surom512 --json out/board.json'),
'run':('指定フレーム実行する','run out/game.nes --frames 120 --png out/game.png --json out/run.json'),
'trace':('イベントを時系列に記録する','trace out/game.nes --frames 2 --cpu --ppu --out out/trace.jsonl'),
'audio-export':('PCM音声をWAVへ書く','audio-export out/game.nes --frames 120 --wav out/audio.wav'),
'profile':('処理の集中場所を集計する','profile out/game.nes --frames 120 --out out/profile.json'),
'diagnose':('静的／動的な診断を出す','diagnose out/game.nes --frames 120 --out out/diagnostics.json'),
'replay-record':('再生用の基準実行を記録する','replay-record out/game.nes --frames 120 --out out/replay.json'),
'replay-run':('保存した操作列を再実行する','replay-run out/game.nes out/replay.json --json out/replay-result.json'),
'snapshot-save':('状態を保存する','snapshot-save out/game.nes --frames 120 --out out/state.kss.json'),
'snapshot-load':('状態ファイルをロードする','snapshot-load out/state.kss.json --json out/state-summary.json'),
'snapshot-resume':('状態の続きから実行する','snapshot-resume out/game.nes out/state.kss.json --frames 60 --json out/resumed.json'),
'snapshot-rebase':('契約で許可した別ROMへ状態を付け替える','snapshot-rebase out/before.nes out/after.nes out/state.kss.json --contract out/compatibility.json --out out/rebased.kss.json'),
'diff':('保存結果の違いを調べる','diff --before out/before.kss.json --after out/after.kss.json --json out/diff.json'),
'decompile':('関数・CFG・疑似コードを回復する','decompile out/game.nes --format markdown --out out/decompile.md'),
'disasm':('CPU命令を表示する','disasm out/game.nes --bytes 256 --text out/disasm.txt'),
'mapper-test':('マッパー用の観測試験を行う','mapper-test out/game.nes --json out/mapper-test.json'),
'fds-inspect':('ディスク構造を読む','fds-inspect out/game.fds'),
'export-assets':('ROM内の素材を書き出す','export-assets out/game.nes --out out/assets'),
'report':('保存情報から報告を作る','report out/run.json --md out/report.md'),
'mapper-list':('登録済みマッパーを一覧にする','mapper-list'),
'mapper-info':('指定マッパーの情報を読む','mapper-info 4')},
'sarakura':{
'gb analyze':('GBの診断をまとめる','gb analyze --metadata out/build.json --events out/events.jsonl --out out/report --fail-on error'),
'fc analyze':('FCの診断をまとめる','fc analyze --metadata out/build.json --events out/events.jsonl --out out/report --fail-on error'),
'catalog':('ルール一覧を読む','catalog gb --json'),
'validate':('診断の形式を検証する','validate out/report/ai_diagnostics.json --strict'),
'compare':('2つの診断結果を比較する','compare --before out/before --after out/after --out out/comparison'),
'inspect-events':('イベントの内容を集計する','inspect-events --events out/events.jsonl'),
'inspect-metadata':('ビルド情報を点検する','inspect-metadata --metadata out/build.json'),
'retest-plan':('再テスト計画を作る','retest-plan --diagnostics out/report --out out/retest.json'),
'emitter-check':('出力元との規約適合を調べる','emitter-check gb --metadata out/build.json --events out/events.jsonl --strict'),
'normalize-events':('イベント形式を正規化する','normalize-events --events out/events.jsonl --out out/normalized.jsonl'),
'ci-summary':('CIの終了条件を判定する','ci-summary --diagnostics out/report --fail-on error --enforce'),
'coverage':('観測済みルールを調べる','coverage gb --events out/events.jsonl --out out/coverage.json'),
'pack-plan':('分野別のルール計画を読む','pack-plan gb'),
'repair-plan':('修正計画を作る','repair-plan --diagnostics out/report --out out/repair.json --markdown out/repair.md'),
'automation-plan':('ツール能力に対応する計画を作る','automation-plan --diagnostics out/report --tool kokura --out out/automation.json'),
'baseline-delta':('基準からの改善と悪化を調べる','baseline-delta --baseline out/before --current out/after --out out/delta --markdown out/delta'),
'schema export':('JSONスキーマを出力する','schema export --out out/schemas'),
'inspect-repro':('再現bundleの構成を調べる','inspect-repro out/report/repro_bundle.zip --json')}
}
def cli_section(key,inventory):
 out=['<h2 id="commands">コマンド書式辞典</h2><p>下記のヘルプは本版で実行して採取しました。省略可能な引数、既定値、列挙値は採取結果に従ってください。説明用コマンドの入力ファイルは自分の出力名に合わせます。</p>']
 for h in inventory['tools'][key]['help']:
  cmd=' '.join(h['argv'][:-1]);entry=CLI_EXAMPLES.get(key,{}).get(cmd)
  label=key+' '+cmd
  out.append('<details class="command searchable" id="cmd-'+slug(label)+'"><summary><code>'+E(label)+'</code>'+(' — '+E(entry[0]) if entry else '')+'</summary>')
  if entry:out.append(code(key+' '+entry[1],'powershell'))
  out.append(code(h['text'],'help')+'</details>')
 if key in ('kitaqgb','kitaqfc'):
  base=ROOT/('kitaqgb/kitaqgb' if key=='kitaqgb' else 'kitaqfc/kitaqfc')
  out.append('<h3>開発補助コマンドの書式</h3><p>以下は現在のProgram.DebugTools.cs / Program.VibeTools.csにある書式です。ROM差分、シンボル探索、テンプレートなどは通常のCコンパイルと別のサブコマンドです。</p>')
  for file in ('Program.DebugTools.cs','Program.VibeTools.cs'):
   for usage in re.findall(r'"(usage: [^"\r\n]+)"',read(base/file)):
    out.append(code(usage,'usage'))
  options=sorted(set(re.findall(r'arg\s*==\s*"(--[\w-]+)"|arg\.StartsWith\("(--[\w-]+)=?',read(base/'Program.cs'))))
  names=sorted({a or b for a,b in options})
  out.append('<h3>パーサーが認識する長いオプション索引</h3><p>完全な綴りを現在のProgram.csから採取。ここには互換・調査用の指定も含みます。値を必要とするかはヘルプと対応する処理を参照してください。</p><div class="tokens">'+''.join('<code>'+E(n)+'</code>' for n in names)+'</div>')
  (SITE/'reference'/(key+'-options.json')).write_text(json.dumps(names,indent=2),encoding='utf-8')
 return ''.join(out)

def headers_section(platform):
 data=json.loads(read(SITE/'reference'/(platform+'-api.json')))
 out=['<h2 id="headers">構造体・定数・ヘッダー全文</h2><p>関数形式でないマクロ、構造体、配列上限、enum、別名はここで確認できます。元のコメントを含む採取時点のヘッダー全文です。</p>']
 for p in data['headers']:
  name=Path(p).name
  out.append('<details class="searchable"><summary><code>'+E(name)+'</code> — '+E(MODULES.get(Path(p).stem,''))+'</summary>'+code(read(ROOT/p))+'<p class="source">'+E(p)+'</p></details>')
 return ''.join(out)
def asm_section(platform):
 p=ROOT/('kitaqgb/kitaqgb/AsmInfo.cs' if platform=='gb' else 'kitaqfc/kitaqfc/AsmInfo.cs')
 defs=re.findall(r'Def\(0x([\dA-Fa-f]{2}),\s*"([^"]+)",\s*(\w+)\)',read(p))
 out=['<h2 id="assembly">付録：アセンブリ命令索引</h2><p>AsmInfo.csの命令表を採取しています。これはコンパイラ内部の綴り・オペランド形式の索引です。分岐先やメモリアドレスを持つ行は書式例であり、単独で実行するプログラムではありません。レジスターの保持やフラグ変化は呼び出し規約とコード生成を参照してください。</p><div class="tablewrap"><table><tr><th>opcode</th><th>命令名</th><th>形式</th><th>書式例</th></tr>']
 formats={'IMP':'','IMM':' #1','IMM8':' #1','IMM16':' #0xC000','ABS':' 0xC000','REL':' +target','IND':'','ZPG':' 0x20','LDH':' 0x40','ABX':' 0x0200,X','ABY':' 0x0200,Y','ZPX':' 0x20,X','ZPY':' 0x20,Y','ZXI':' (0x20,X)','ZYI':' (0x20),Y'}
 for op,n,f in defs:out.append('<tr class="searchable"><td>'+op+'</td><td><code>'+E(n)+'</code></td><td>'+f+'</td><td><code>'+E(n+formats.get(f,' [operand]'))+'</code></td></tr>')
 out.append('</table></div>');return ''.join(out)

def main():
 inventory=json.loads(read(SITE/'reference/inventory.json'));manifest=json.loads(read(SITE/'samples/manifest.json'))
 origin_path=SITE/'tools/origin.txt'
 origin=read(origin_path).strip() if origin_path.exists() else '名称の由来：作者への確認待ちです。推測で由来を確定しないため、この一文は回答後に確定します。'
 for key,num,title,sub in [('index','00','KITAQ SERIES','プログラミング・ユーザーズマニュアル'),*BOOKS]:
  body=md(TEXT[key].replace('{{ORIGIN}}',origin))
  if key=='index':
   body+='<h2 id="books">マニュアルを選ぶ</h2><div class="books">'+''.join('<a class="book" href="'+k+'.html"><span>'+n+'</span><strong>'+E(t)+'</strong><small>'+E(s)+'</small></a>' for k,n,t,s in BOOKS)+'</div>'
  if key in ('kitaqgb','gb-library','kitaqfc','fc-library'):
   p='gb' if key in ('kitaqgb','gb-library') else 'fc'
   body+=samples_section(p,manifest)
   body+=api_section(p,key in ('kitaqgb','kitaqfc'))
   if key.endswith('library'):body+=headers_section(p)
   else:body+=cli_section(key,inventory)+asm_section(p)
  else:
   if key!='index':body+=cli_section(key,inventory)
  page(key,title,sub,body)
 # Verification is generated from recorded outcomes rather than aspirational claims.
 results=json.loads(read(SITE/'verification/samples.json')) if (SITE/'verification/samples.json').exists() else []
 body='<h2 id="scope">今回の確認範囲</h2><p>以下は9月12日時点のソースに対する検証記録です。コンパイラ2種とKUROSAKI CLIは記録したソースからビルドし、KOKURAとSARAKURAはローカルの実行ファイルを使用しました。全機能・全周辺機器・実機の試験ではありません。公開するソースと実行ファイルのビルド・実行検証は <a href="PUBLICATION_CHECKS.md">publication checks</a> に記録しています。</p><p>各サンプルのコンパイル終了コード、120フレームのエミュレータ実行、画面は以下です。期待値の画素照合は別の結果がある場合に明示します。終了コード0だけで入力・音・ゲーム挙動の正常を証明したとはしません。</p>'
 for r in results:
  id=r['id'];body+='<section id="'+id+'"><h2 id="result-'+id+'">'+id+'</h2><p>ビルド終了コード：'+E(str(r['build_exit']))+' ／ 実行：'+E(r['runtime'])+'</p><p>'+E(r.get('expected',''))+'</p>'
  if (SITE/'verification'/(id+'.png')).exists():body+='<img class="screen" loading="lazy" src="verification/'+id+'.png" alt="'+id+' のエミュレータ実行画面">'
  body+='<p><a href="verification/'+id+'-build.txt">ビルドログ</a>'
  if (SITE/'verification'/(id+'-runtime.txt')).exists():body+=' ／ <a href="verification/'+id+'-runtime.txt">実行ログ</a>'
  body+='</p></section>'
 for filename,title in [('visual_checks.json','サンプル画面の数値・字体照合'),('workflow.json','診断ワークフロー'),('compiler_tests.json','コンパイラ修正の回帰試験'),('browser_checks.json','ブラウザーでの表示確認'),('site_checks.json','HTML構造とリンク')]:
  if (SITE/'verification'/filename).exists():body+='<h2 id="'+filename.replace('.','-')+'">'+title+'</h2>'+code(read(SITE/'verification'/filename),'json')
 page('verification','VERIFICATION','ビルド・実行・表示の確認記録',body)
 from generate_prompts import publish
 publish('ja')
 from api_contracts import publish as publish_api_contracts
 publish_api_contracts('ja')
 print('Generated 10 Japanese HTML pages including development prompts')
if __name__=='__main__':main()
