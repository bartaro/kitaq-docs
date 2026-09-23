from pathlib import Path
import re,json,html,shutil
from collect import ROOT,SITE,read
from chapters import TEXT,BOOKS
from languages import language_nav
from sample_guides import GUIDES, render as sample_guide, screen as sample_screen, gallery as sample_gallery
E=html.escape
def slug(t):
 # Keep incoming section links stable when a heading is clarified.
 aliases={'5　ループと状態による分岐':'5-未対応構文の書き換え','5. Loops and state dispatch':'5-Rewrite-unsupported-constructs'}
 return aliases.get(t,re.sub(r'[^\w-]+','-',t).strip('-'))
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
  if re.fullmatch(r'<!-- [\w:-]+ -->',s.strip()):
   out.append(s.strip());i+=1;continue
  if s.startswith('```'):
   lang=s[3:] or 'text';block=[];i+=1
   while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
   out.append(code('\n'.join(block),lang));i+=1;continue
  if s.startswith('### '):
   title=s[4:];out.append('<h3 id="'+slug(title)+'">'+inline(title)+'</h3>');i+=1;continue
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
  while i<len(lines) and lines[i].strip() and not lines[i].startswith(('## ','### ','```','|')) and not re.match(r'^\d+\. ',lines[i]):para.append(lines[i]);i+=1
  out.append('<p>'+inline(' '.join(para))+'</p>')
 return '\n'.join(out)

MODULES={
'system':'起動、フレーム数、待機と割り込み', 'input':'ボタンの現在値・押下・解放・リピート', 'sprite':'OBJの確保、配置、メタスプライト、アニメーション',
'vram':'VRAM更新の予約と転送','fixed':'Q8.8固定小数点と矩形','scene':'シーンの登録、変更と更新','entity':'固定配列のオブジェクトプール',
'chain':'関節追従と座標履歴','audio':'音楽と効果音・音源制御','audio_vblank':'VBlank IRQによる音楽再生','rpg':'乱数、文字、マップ、セーブ、RPG/ADV/SLG',
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
'sprite_order':'優先度と交替によるスプライト選択',
}
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
  out.append('<details class="sample searchable" id="sample-'+d['id']+'"><summary>'+E(GUIDES[d['id']]['ja'][0])+' <code>'+d['file']+'</code></summary>'+sample_guide(d['id'],'ja')+sample_screen(d['id'],'ja')+'<p><a href="samples/'+d['file']+'" download>ソースを保存</a> ／ <a href="verification.html#'+d['id']+'">検証状況</a></p>'+code(cmd,'powershell')+code(read(SITE/'samples'/d['file']))+'</details>')
 return ''.join(out)

def api_section(platform,intrinsic):
 from api_scaffold import section
 return section(platform,intrinsic,'ja',MODULES)

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
  if key=='kokura':
   from kokura_guide import block
   body+=block('ja')
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
 page('verification','VERIFICATION','確認した実行画面',sample_gallery('ja'))
 from generate_prompts import publish
 publish('ja')
 from api_contracts import publish as publish_api_contracts
 publish_api_contracts('ja', require_complete=True)
 print('Generated 10 Japanese HTML pages including development prompts')
if __name__=='__main__':main()
