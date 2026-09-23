## 13　コマンドの使い分けと引数の書式

以下は各リポジトリが横に並ぶフォルダーから実行するPowerShellの例です。先に `New-Item -ItemType Directory -Force out` で出力先を作り、`out/game.gb` を自分のROMへ置き換えます。KOKURAはROMの後ろにオプションを指定します。KUROSAKIのような `run` サブコマンドは付けません。手元の実行ファイルが受け付ける一覧は `--help` で確認できます。

### 13.1　実行方式とフレーム数を決める

| 引数 | 目的と動作 |
| --- | --- |
| `ROM` | 通常実行するROMのファイル名です。ジョブや検証行列では、その設定内でROMを指定できます。 |
| `--hardware auto` / `dmg` / `cgb` | 動かす本体の種類です。既定はauto。両対応のゲームはdmgとcgbを明示してそれぞれ確認します。 |
| `--run-frames 120` | 通常実行の最大フレーム数です。既定は1。停止条件に達すると早く終了します。入力列には別途、各区間の長さがあります。 |
| `--job out/test.json` | JSONにまとめた設定で実行します。フレーム数はrun.framesへ書きます。ROM、入力、状態、記録先はジョブ内の指定が使われ、相対パスの基準はジョブファイルの場所です。 |
| `--dump-report out/run.json` | 実行レポートをJSONへ保存します。通常実行で保存先を省くと標準出力へ表示します。 |
| `--regression-matrix out/matrix.json` | ジョブと期待する観測結果をまとめて検証します。コマンドの正常終了だけで全件成功とは判断せず、JSON内の各ケースの結果を確認します。 |

1回の呼び出しでは1つの方式を選びます。複数指定時の優先順は、デコンパイル、逆アセンブル、検証行列、通信ジョブ、直接指定の通信セッション、通常実行です。複数の処理を順番に実行する指定にはなりません。

```powershell
.\kokura\kokura-cli.exe out/game.gb --hardware dmg --run-frames 120 --png out/game.png --dump-report out/run.json
```

最大120フレームを進め、最後の画面とレポートを保存します。まず実際に進んだフレーム数と停止理由を読み、その後で画面を判断します。

### 13.2　同時押しと時間順の入力

| オプション | 書式と使い方 |
| --- | --- |
| `--input "A,RIGHT"` | 通常実行中にAと右を同時に押し続けます。大文字・小文字は区別しません。NONEは全ボタンを離します。 |
| `--input-seq "NONE:30;A:1;NONE:89"` | ボタン:フレーム数をセミコロンでつなぎます。この例は30フレーム離す→1フレームA→89フレーム離す、の順です。 |
| `--input-script "NONE:30;A:1;NONE:89"` | 同じ入力列の文字列を受け取ります。ファイル名ではありません。input-seqとの同時指定ではこちらが優先されます。 |

ボタン名は `RIGHT,LEFT,UP,DOWN,A,B,SELECT,START` です。16進マスクではRIGHT=0x01、LEFT=0x02、UP=0x04、DOWN=0x08、A=0x10、B=0x20、SELECT=0x40、START=0x80です。NESのパッド値とは並びが違います。PowerShellでは入力列全体を引用符で囲みます。押した瞬間を試すときは離す区間を挟み、観測したい時間を入力列で覆ってください。

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 120 --input-seq "NONE:30;A:1;NONE:89" --png out/after-a.png --dump-report out/after-a.json
```

ボタン回数のサンプルなら、カウンターが1回増えることを期待します。押し続けたときの連射判定を調べる場合は、長押しと押し直しを別々に試します。

### 13.3　画面・動画・音を保存する

| オプション | 書式と使い方 |
| --- | --- |
| `--png out/final.png` | 最後の画面を保存します。screenshotと両方指定した場合はこちらが優先されます。 |
| `--screenshot out/frame.png` | 画面保存先の別指定です。PNGとBMPに対応し、拡張子がなければ.pngを補います。 |
| `--screenshot-frames 30:32` | 指定区間の各フレームを、番号付きのファイル名で保存します。画面保存先も指定します。 |
| `--record-wav out/audio.wav` | 音声をWAVへ記録します。実際に発音するROMと時間区間を選んでください。 |
| `--record-wav-frames 1:180` | 録音するフレームの範囲です。音声サンプル数ではありません。 |
| `--record-video out/motion.gif` | 動きをGIFまたはY4Mへ記録します。拡張子なしでは.gifを補います。MP4は指定できません。 |
| `--record-video-frames 30:120` | 動画に含めるフレームの範囲です。 |
| `--audio-buffer-frames 8192` | 音声バッファの容量をステレオのサンプルフレーム数で指定します。映像のフレーム数や片チャンネルのサンプル数ではありません。 |

記録範囲は1から始まる十進数で、`30` は1フレーム、`30:32` は30・31・32の3フレームです。0や逆順の範囲はエラーになります。記録番号は今回の実行区間に対する番号なので、保存状態から再開するときはレポートも残します。保存先の親フォルダーは先に作成してください。

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 180 --record-wav out/audio.wav --record-wav-frames 1:180 --record-video out/motion.gif --record-video-frames 30:120
```

スクロールは複数フレームの位置の変化で、音はWAVで確認します。画面に終了を示す数値が出ても、狙ったチャンネルの発音まで証明したことにはなりません。

### 13.4　状態を保存して再開する

| オプション | 役割と優先順位 |
| --- | --- |
| `--save-state out/checkpoint.kqs` | 終了時のマシン状態を保存します。 |
| `--snapshot out/checkpoint.kqs` | 同じ保存先の指定で、save-stateより優先されます。 |
| `--load-state out/checkpoint.kqs` | 実行前にKQS状態を読み込みます。 |
| `--resume-state out/checkpoint.kqs` | load-stateより優先され、ジョブの開始状態も上書きできます。 |
| `--snapshot-at "frame=60&&frame_end=>out/frame60.kqs"` | 観測条件に一致したとき保存します。複数指定できます。保存先を省くと、ROM名を使った連番のKQSファイルを作業フォルダーへ保存します。 |

ROMとエミュレータの版が合った状態を使います。KQSは本体の状態であり、カートリッジのセーブRAMやC APIのJSON状態とは別形式です。

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 120 --save-state out/title.kqs
.\kokura\kokura-cli.exe out/game.gb --resume-state out/title.kqs --input START --run-frames 30 --png out/started.png --snapshot out/started.kqs
```

### 13.5　名前を付けてメモリを観測する

| オプション | 書式と使い方 |
| --- | --- |
| `--symbols out/game.map` | 対応するビルドのシンボルを読み込みます。 |
| `--source-map out/game.source_map.txt` | 実行位置とソースの位置を対応付けます。 |
| `--toolchain-metadata out/game.dbg2.json` | 構造化されたツールチェーン情報を読み込みます。ROM横の対応ファイルを自動検出する経路もあります。 |
| `--watch-window "player:0xC700:16"` | 0xC700から16バイトをplayerという名前で観測します。複数指定できます。観測窓を作るだけでは実行は停止しません。 |
| `--watch-baseline-mode initial` | 開始時からの変化を比較します。previous-frameは前フレームとの差、namedは名前付き基準との比較です。 |
| `--watch-baseline-tag ready` | namedで比較する基準名を選びます。 |
| `--capture-watch-baseline "ready=>frame=30&&frame_end"` | 条件成立時の値をreadyという基準名で保存します。複数指定できます。 |
| `--watch-fields preview,diff` | 観測項目を選びます。hash、activity、preview、baseline、diff、insights、allを指定できます。previewは長さに制限のある抜粋です。 |
| `--report-sections cpu,watched_memory` | 残すレポート項目を指定します。metaとschema_versionは残ります。未知の名前を書いても新しい項目は作られません。 |
| `--report-minimal cpu,watched_memory` | レポート項目の別指定で、report-sectionsより優先されます。真偽のスイッチではなく、カンマ区切りの値が必要です。 |

アドレスと長さは十進数、または0x付きの16進数です。変数の位置は現在のビルドのシンボルで調べてください。例の0xC700は固定のプレイヤー領域という意味ではありません。

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 60 --watch-window "player:0xC700:16" --watch-fields preview,diff --report-sections cpu,watched_memory --dump-report out/watch.json
```

### 13.6　実行位置やハードウェアイベントで止める

| オプション | 書式と目的 |
| --- | --- |
| `--breakpoint "pc:0x0150"` | CPUアドレスで止めます。symbol:mainならシンボルを使います。末尾の@bank:2でバンクを限定できます。 |
| `--watchpoint "player@0xC700+4"` | 指定した4バイトへの書き込みで止めます。名前部分は省略可能で、+長さを省くと1バイトです。 |
| `--stop-on-mmio "scroll@0xFF43"` | MMIOレジスタへの書き込みで止めます。この例はSCXです。 |
| `--stop-on-irq "vblank:serviced"` | 割り込みの種類と段階を選びます。段階はrequested、serviced、blocked、anyです。段階だけなら割り込みの種類を限定しません。 |
| `--stop-on-dma oam_start` | DMAイベントを選びます。oam_start、oam_complete、hdma_start、hdma_block、hdma_complete、hdma_cancel、gdma_stall、hdma_deferred、hdma_ignoredが使えます。 |
| `--run-until "frame=60&&frame_end"` | 観測条件の全項目が一致したら止めます。複数指定できます。 |

ブレークポイントの `pc:`、`symbol:`、`@bank:` は大文字・小文字を区別します。アドレスとバンクは十進数または0x付き16進数です。条件に達しない場合に備えてフレーム数も指定してください。

観測条件は `&&` で結ぶAND条件です。指定できる項目は `frame=`、`ly=`、`pc=`、`bank=`、`bank_pc=バンク:PC`、`symbol=`、`source=`、`event=`、`ppu_mode=`（または `mode=`）、`basis=` です。frameとlyは十進数、symbol・source・eventは文字列で照合します。basisにはframe_start、frame_end、step、event、trace、snapshot、stopを指定できます。単独のframe_start、frame_end、stop、vblankも使えます。`hp<10` のようなCの式を評価する機能ではありません。

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 120 --breakpoint "pc:0x0150" --snapshot out/entry.kqs --dump-report out/entry.json
.\kokura\kokura-cli.exe out/game.gb --run-frames 120 --stop-on-mmio "scroll@0xFF43" --dump-report out/scroll-write.json
```

前者は開始位置、後者は横スクロールを書き換える処理を調べる例です。指定した理由で実際に停止したかをレポートで確認します。

### 13.7　観測点を記録し、実行結果を比較する

| オプション | 目的 |
| --- | --- |
| `--trace-point "frame=30&&frame_end"` | 条件一致時の観測点を記録します。複数指定できます。 |
| `--timeline-out out/timeline.jsonl` | 観測タイムラインの保存先です。 |
| `--trace-jsonl out/timeline.jsonl` | タイムライン保存先の別指定で、timeline-outより優先されます。全CPU命令を漏れなく記録する指定ではありません。 |
| `--timeline-format jsonl` | jsonl（既定）またはcsvを選びます。拡張子も自分で形式に合わせます。 |
| `--replay-interval 1` | リプレイのチェックポイント記録を有効にし、フレーム間隔を指定します。 |
| `--replay-max-checkpoints 120` | 保存するチェックポイント数の上限です。リプレイの既定は間隔1、保存数16です。 |
| `--rewind-on-stop-frames 10` | 停止後に、保持している履歴を使って指定フレーム分の巻き戻しを要求します。 |
| `--stop-on-divergence` | リプレイ制御の不一致時停止を有効にします。 |
| `--dump-replay-tape out/baseline.json` | 記録したリプレイを出力します。出力するには記録を有効にします。 |
| `--compare-replay-tape out/baseline.json` | 保存済みリプレイと比較します。同じROM、入力、開始状態を用意します。 |
| `--compare-replay-watch-only` | 比較対象を観測メモリへ限定します。全マシン状態の一致を確認する指定ではありません。 |
| `--snapshot-on-replay-mismatch out/mismatch` | 不一致の追跡用ファイルの接頭辞を指定します。 |

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 60 --replay-interval 1 --replay-max-checkpoints 60 --dump-replay-tape out/baseline.json --dump-report out/baseline-report.json
.\kokura\kokura-cli.exe out/game.gb --run-frames 60 --replay-interval 1 --replay-max-checkpoints 60 --compare-replay-tape out/baseline.json --dump-report out/compare.json
```

比較レポートの一致結果と最初の不一致位置を確認します。ファイルが2つ作れたことだけでは比較成功になりません。

### 13.8　診断と再現用の資料を残す

| オプション | 実際の動作 |
| --- | --- |
| `--emit-diagnostics out/events.jsonl` | SARAKURAへ渡す診断イベントを出力します。 |
| `--diagnostics-jsonl out/events.jsonl` | 通常実行での診断保存先の別指定です。emit-diagnosticsが優先されます。 |
| `--repro-bundle out/repro.zip` | レポート、診断イベント、目録をZIPへまとめます。ROMとメタデータはパスの参照で、ファイル本体は含みません。画像・状態・トレースも自動では入りません。 |
| `--break-on-diagnostic all` | 最終レポートの診断を照合して資料を保存します。問題の命令で即時停止する機能ではありません。空でないフィルターがある場合、最終診断が1件でもあれば保存経路へ入ります。 |
| `--png-on-diagnostic out/diagnostic-images` | 診断時の画面保存フォルダーです。diagnostic_000001.pngへ最終状態を保存します。診断保存の指定と組み合わせます。 |
| `--snapshot-on-diagnostic out/diagnostic-states` | diagnostic_000001.kqsを置くフォルダーです。イベント発生時点ごとの状態ではなく、その実行の最終状態です。 |
| `--diagnostic-pack NAME` | 引数は受け付けますが、実行経路では診断パックの選択を適用しません。 |
| `--diagnostic-rule RULE` | 複数指定できますが、実行経路ではこのルール選択を適用しません。 |
| `--diagnostic-summary-limit N` | 引数は受け付けますが、実行経路ではこの要約件数の制限を適用しません。 |

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 180 --emit-diagnostics out/events.jsonl --dump-report out/run.json --break-on-diagnostic all --png-on-diagnostic out/diagnostic-images --snapshot-on-diagnostic out/diagnostic-states --repro-bundle out/repro.zip
```

命令や書き込みの瞬間に止めるには13.6の停止条件を使います。無入力で待つタイトル画面などは意図した挙動でも診断が出るため、観測内容とゲームの設計を照合します。

### 13.9　CPU命令と疑似コードを調べる

| オプション | 書式と目的 |
| --- | --- |
| `--disassemble-out out/code.txt` | 通常実行をせず、ROMのCPU命令を逆アセンブルします。 |
| `--disassemble-range "0:0100-0150"` | BANK:START-ENDで範囲を指定します。複数指定できます。ここでは0xがなくても3つとも16進数です。 |
| `--disassemble-format text` | text（既定）、markdown、jsonを選びます。 |
| `--decompile-out out/functions.json` | 疑似コードと制御フロー情報を出力します。 |
| `--decompile-format json` | json（既定）、markdown、textを選びます。 |
| `--decompile-function main` | 対象の関数を選びます。複数指定でき、対応するシンボルがあると識別しやすくなります。 |
| `--decompile-all` | デコンパイラが把握した名前付き関数をすべて対象にします。 |
| `--decompile-annotations out/annotations.json` | デコンパイラ用のJSON注釈を読み込みます。 |
| `--decompile-trace out/trace.json` | デコンパイラ用のトレース情報を読み込みます。任意の診断JSONLを代わりに渡すことはできません。 |

```powershell
.\kokura\kokura-cli.exe out/game.gb --disassemble-range "0:0100-0150" --disassemble-out out/entry.txt --disassemble-format text
.\kokura\kokura-cli.exe out/game.gb --symbols out/game.map --decompile-function main --decompile-out out/main.md --decompile-format markdown
```

生成された命令列の確認には逆アセンブル、制御の流れの把握には疑似コードを使います。元のCをそのまま復元する機能ではありません。ROMと同じビルドのシンボルを組み合わせます。

### 13.10　複数台の通信を動かす

| オプション | 書式と目的 |
| --- | --- |
| `--link-job out/pair.json` | 接続方式と参加ROMをJSONで指定します。相対パスはジョブのフォルダーが基準です。 |
| `--link-topology pair` | 直接指定のセッションでpair、four_player_adapter、dmg07を選びます。 |
| `--link-session SPEC` | 1台分の設定です。最低2台を指定します。PowerShellではパイプ記号を含む全体を引用符で囲みます。 |
| `--link-initial-peer-slot 1` | 相手選択を行う接続方式の初期通信相手を指定します。 |

各セッションにはname、slot、rom、symbols、source_map、toolchain_metadata、load_state、save_state、input、input_sequence、audio_buffer_frames、watch_windowを指定できます。romは必須です。観測窓は `a:0xC700:4,b:0xC710:4` のようにカンマで複数指定できます。実際にシリアル通信するROMを使い、2画面が動いただけで通信成功とは判断しないでください。
