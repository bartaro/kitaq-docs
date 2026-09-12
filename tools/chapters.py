"""Hand-edited Japanese chapters. API listings are generated separately."""
BOOKS=[('kitaqgb','01','KITAQGB','ゲームボーイ Cプログラミング'),('gb-library','02','KITAQGB LIBRARY','ゲームを組み立てる道具箱'),('kokura','03','KOKURA','実行・観察・記録'),('kitaqfc','04','KITAQFC','ファミコン Cプログラミング'),('fc-library','05','KITAQFC LIBRARY','NESライブラリと機器'),('kurosaki','06','KUROSAKI','NES・FDSの実行と解析'),('sarakura','07','SARAKURA','診断・比較・再テスト')]

TEXT={
'index':r'''
## はじめに
KITAQGBは、ZachtronicsのNES向けCコンパイラ **NORCALのフォーク** として始まった、ゲームボーイ／ゲームボーイカラー向けのC系コンパイラです。NORCALを出発点に、GBのCPU、メモリ、映像、音、ROMバンクなどに合わせた機能が加えられています。原作者・原プロジェクトへの敬意を込めて、ここに系譜を明記します。

{{ORIGIN}}

NORCALはNES版HACK*MATCHに関係してKeith Holman氏が開発したCコンパイラです。[NORCAL: A C Compiler for the NES](https://keithholman.net/nes-compiler.html) と [HACK*MATCH for the NES](https://trashworldnews.com/hack-match/) に原作者による紹介があります。フォークの説明と名称の由来は作者提供のREADMEに基づきます。

## このマニュアルの使い方
昔のコンピュータに付属した取扱説明書のように、最初は短いプログラムを入力し、実行結果を見てから仕組みを学びます。わからない語をすべて覚えてから始める必要はありません。

1. GBなら第1巻、FCなら第4巻の「最初のプログラム」から始めます。
2. 入力・画像・音を加えるときは、第2巻または第5巻の対応する機能へ進みます。
3. 画面や音の確認はKOKURA／KUROSAKI、異常の整理はSARAKURAを使います。
4. 関数名がわかるときは、検索欄または各巻の命令・API辞典を使います。

「命令」は文法、コンパイラ組み込み関数、ライブラリ関数、コマンドライン操作を分けて説明します。CPUの命令表もコンパイラ巻の付録にあります。GBとFCで同じ名前に見えても、引数や動作が同じとは限りません。

## 7冊の役割
| 巻 | 入力 | 出力・役割 |
| --- | --- | --- |
| KITAQGB | Cソース・素材 | GB/CGB用ROM、マップ、ビルド情報 |
| KITAQGBライブラリ | ゲームからの関数呼び出し | 描画・音・入力・物理などの処理 |
| KOKURA | GB/CGB用ROM | 実行画面、音、状態、観測ログ |
| KITAQFC | Cソース・CHR素材 | NES/FDS向け出力とビルド情報 |
| KITAQFCライブラリ | ゲームからの関数呼び出し | NES向けの描画・音・機器処理 |
| KUROSAKI | NES/FDSイメージ | 実行・記録・解析 |
| SARAKURA | ビルド情報と診断イベント | 診断HTML、修正・再テストの計画 |

## 指定フォントの使い方
大文字26字、数字10字、小文字26字、記号30字は、作者指定の [ascii.c](samples/assets/ascii.c) をそのまま収録しました。追加の字形を描き直してはいません。元データの番号とASCIIコードの対応は [変換記録](verification/font_conversion.json)、全字形は [タイル一覧](verification/font_source_atlas.png) にあります。空白は空タイルです。元データにないバックスラッシュと縦棒は空白となります。すべての提供字形を `gb_font.c` と `fc_font.c` で表示できます。

## 本書の版と検証の読み方
**2026年9月12日のローカルソースを基準** とする版です。「最新」はこの採取時点を指し、将来のGitHub公開版の更新まで自動追従する意味ではありません。参照ソースと使用実行ファイルのSHA-256を同梱しています。過去のREADMEにある「未対応」「確認済み」は、そのまま現在の保証として転載していません。

「ビルド確認」はROMが生成できたこと、「実行確認」は指定フレームまでエミュレータで動かしたことです。画面の期待値を照合した結果はサンプル一覧に別記します。実機や全周辺機器での互換性を保証する印ではありません。警告はログに残します。

## 作業机を用意する
本書のコマンド例は **Windows PowerShell** です。CソースはUTF-8のテキストとして保存します。コマンドを実行するフォルダーを「カレントディレクトリ」と呼びます。ファイル名に空白があるときは引用符で囲み、実行ファイルのパスは `& "パス"` と書きます。

```powershell
# リポジトリのルートで実行します。
New-Item -ItemType Directory -Force out | Out-Null
.\kitaqgb\kitaqgb.exe --help
.\kitaqfc\kitaqfc.exe --help
```

説明中の `game.c`、`game.gb`、`game.nes` は自分のファイル名に置き換えます。山括弧付きの `<ROM>` は書式上の引数名であり、山括弧ごと入力しません。長いコマンドは本書では原則1行にしています。Bashの行継続文字 `\` をPowerShellへ貼り付けないでください。

## この版で修正したコンパイラの問題
サンプルを実行する過程で、KITAQGBの同名ローカル分岐ラベルの混同と、KITAQFCの関数呼び出し時の途中値・戻り値の扱いに問題が見つかりました。本版の検証では修正済みコンパイラを使い、GBのオブジェクトプール例も通常の教材に含めています。[変更内容と再発防止テスト](verification/compiler_fixes.md) を参照してください。古いEXEで同じ症状が出る場合は、本版のソースからコンパイラを再ビルドします。

API辞典の呼び出し断片は完全なROMとは区別しています。全API・実機・全周辺機器を試験したという意味ではありません。各教材の確認結果は [検証記録](verification.html) に示します。

## HTMLを持ち歩く・公開する
このフォルダーの `index.html` を開けば、外部CDNやインターネットなしで読めます。スタイル、検索用JavaScript、サンプル、検証画像も相対リンクで同梱しています。HTMLファイルだけを抜き出さず、フォルダー単位で扱ってください。印刷ボタンでは目次欄を省いた紙面になります。

GitHubへアップロードする範囲はこの `latest` フォルダーです。閲覧用HTMLの生成にサーバー処理は不要です。GitHubでHTMLファイルを開く画面は通常ソース表示になるため、Webマニュアルとして公開する場合はGitHub Pagesなどの静的ホスティングを設定します。公開作業そのものは本書作成時には実行していません。具体的な配置手順は同梱 `README.md` を参照してください。
''',
'kitaqgb':r'''
## 1　KITAQGBを知る
KITAQGBはZachtronicsのNORCALをフォークして発展した、GB/CGB用のC系コンパイラです。{{ORIGIN}} Cファイルを読み、CPU命令へ変換し、ゲーム機が読み込むROMにまとめます。一般のPC用Cコンパイラとは言語・標準ライブラリ・呼び出し規約が異なります。

GBは小さなメモリと8ビットCPUを持ちます。画面は基本的に8×8画素のタイルを並べて作ります。背景とは別に動かす小さな絵がスプライトです。文字も自動的には存在せず、文字のタイルを用意します。本書のサンプルには、作者指定の `ascii.c` の英数字・記号を使います。GBではビット列を保ったままASCII番号へ配置し、FCでは同じ字形をNESのCHR形式へ変換しています。

## 2　準備とコンパイラのビルド
ソースから作る場合は、.NET Framework 4.8を対象とするVisual Studio/MSBuild環境を用意します。以下はDeveloper PowerShellなど、`MSBuild.exe` が使える端末での操作です。

```powershell
MSBuild.exe .\kitaqgb\kitaqgb.csproj /t:Build /p:Configuration=Release
.\kitaqgb\bin\Release\kitaqgb.exe --help
```

実行ファイル配布を使う場合は、その版の `kitaqgb.exe` と付属ファイルを使います。開発フォルダーのルートにあるEXEと `bin\Release` のEXEは、更新日時が違うことがあります。サンプルのビルド時には、どちらを使うか明示してください。

## 3　最初のプログラム
同梱 `samples/gb_hello.c` は `gb_common.h` の画面準備・文字表示関数を使います。ヘッダーとフォントも一緒に置きます。`#include` は別ファイルを読み込む指示です。

```c
#include "gb_common.h"
void main() {
    m_init();
    m_text(2, 5, "HELLO WORLD");
    m_number(42);
    while (1) { m_wait(); }
}
```

```powershell
.\kitaqgb\kitaqgb.exe .\kitaq-docs\samples\gb_hello.c -I .\kitaq-docs\samples -o .\out\hello.gb --profile=dev --rst-disable --stack-bank=fixed
.\kokura\target\release\kokura-cli.exe .\out\hello.gb --run-frames 120 --png .\out\hello.png --dump-report .\out\hello.json
```

画面にHELLO WORLDと042が出れば、この例の目標達成です。`m_` で始まる関数は本書の学習用ヘルパーで、KITAQGBの標準命令ではありません。定義はサンプルの共通ヘッダーで読めます。`__wait_vblank` や `__vram_copy` が本来の組み込み機能です。

## 4　プログラムの文法
文の終わりに `;`、処理のまとまりに `{ }` を使います。`//` 以降は1行コメント、`/* ... */` は複数行コメントです。名前の大文字・小文字は区別します。エントリーポイントは `void main()` です。**このGB版では `void main(void)` にすると構文エラーになります。** FC版のコードをそのまま移すときの注意点です。

| 型 | 使い道・範囲 |
| --- | --- |
| `u8` | 8ビット符号なし整数、0～255 |
| `s8` | 8ビット符号付き整数、-128～127 |
| `u16` | 16ビット符号なし整数、0～65535 |
| `s16` | 16ビット符号付き整数、-32768～32767 |
| `void` | 戻り値なし |
| `T*` | T型のデータを指すポインタ |

最初はこの短い型名を使ってください。PC用Cの `int`、`long`、`float`、`double` や標準ヘッダーの存在を前提にしません。`char` は本実装では符号なし8ビット型として扱われます。符号が必要な計算には `s8` / `s16` を明記します。

```c
u8 lives = 3;
u16 score;
score = (u16)200 + 100;
```

`(u16)` は型変換です。小さな型のまま計算してから大きな型に代入しても、途中で失った桁は戻りません。8ビットの範囲を超える計算では、演算前に型を広げます。小数の動きにはライブラリの固定小数点を使います。

## 5　式と演算子
| 種類 | 記号 | 例・意味 |
| --- | --- | --- |
| 算術 | `+ - * / %` | `n / 10` は整数の商、`n % 10` は余り |
| 比較 | `== != < <= > >=` | `lives == 0` は等しいかの判定 |
| 論理 | `! &&` / `||` | 条件の否定・両方成立・どちらか成立 |
| ビット | `&` / `|` / `^ ~ << >>` | ボタン・フラグなどのビット集合 |
| 代入 | `= += -=` など | `x += 1` は値を更新 |
| 増減 | `++ --` | `i++` は1を加える |
| 選択 | `条件 ? A : B` | 条件に応じて値を選ぶ |
| ポインタ | `&変数` / `*p` | アドレスを得る／指す先を読む |

`=` と `==` を混同しないでください。複雑な式は括弧で意図を明確にし、呼び出しと副作用を1行へ詰め込みません。ゼロ除算や配列範囲外へのアクセスは避けます。`sizeof` はバイト数、`offsetof` は構造体メンバーの位置を得るために使います。

## 6　条件分岐と繰り返し
```c
if (lives == 0) { game_over = 1; }
else { score = score + 10; }
for (i = 0; i < 4; i++) { table[i] = i; }
while (running != 0) { update_game(); }
do { count++; } while (count < 3);
```

`break` はループやswitchを抜け、`continue` は次の反復へ進み、`return` は関数から戻ります。`switch` のcaseから次のcaseへ意図的に進む場合は、本言語の `fallthrough;` を使います。暗黙の流れ落ちは診断の対象です。動作例は `gb_control.c` にまとめています。

## 7　関数・配列・構造体
```c
u8 add(u8 a, u8 b) { return (u8)(a + b); }
typedef struct { u8 x; u8 y; } Point;
Point player;
u8 tiles[4];
```

配列は0から数えます。4要素なら有効な添字は0～3です。`player.x` はメンバー、`pointer->x` はポインタで指した構造体のメンバーです。構造体・union・enumの構文があり、レイアウトは型や `__packed` / `__aligned` の指定に依存します。バイナリファイルやハードウェアへ渡すときは `sizeof` を確認します。

標準のLegacy ABIは引数やローカル領域を固定配置する設計です。再帰や割り込みによる再入をPC用Cと同様に扱わないでください。`__stackcall` や `--abi=stack` は呼び出し規約に関わる上級指定です。混在するときはビルドのABIレポートと実行を確認します。

## 8　ソースの分割とプリプロセッサ
ヘッダーには型・定数・関数宣言を書き、`.c` に関数本体を書きます。`#pragma once` またはinclude guardで二重取り込みを防ぎます。`#define`、`#undef`、`#if`、`#ifdef`、`#ifndef`、`#elif`、`#else`、`#endif` を使ってコンパイル時にコードを選べます。

```powershell
.\kitaqgb\kitaqgb.exe main.c game.c .\kitaqgb\lib\input.c -I .\kitaqgb\lib -o .\out\game.gb --profile=dev
```

`-I` はヘッダーを探す場所です。ライブラリのヘッダーをincludeしただけでは本体は結合されません。必要な `.c` もコマンドへ並べます。すべてのライブラリを一括指定するとレジスター定義や割り込み処理が衝突し得るので、機能に必要なものを選びます。

## 9　ROM・メモリ・バンク
ROMはプログラムと定数、WRAMは変数、VRAMは画像、OAMはスプライトの情報です。バンクとは、同じCPUアドレスへ見せるメモリの領域を切り替える仕組みです。16ビットのアドレスだけでは、別バンクのデータを区別できません。

```c
#pragma bank 1
__prg_rom u8 level_data[] = { 1, 2, 3, 4 };
```

`__prg_rom` はROM配置、`__location(0xFF40)` のような指定は固定アドレス、`__wram` / `__hram` はメモリ領域の指定です。`#pragma bank` や `#pragma fixed_bank` を使う場合はマップを読み、割り込みで呼ぶコードやデータが常に見えるか確認します。

```powershell
.\kitaqgb\kitaqgb.exe main.c -o .\out\game.gbc --cart=mbc5 --romsize=256k --ramsize=32k --cgb=cgb --rom-title=MYGAME --stack-bank=fixed --emit-ai-metadata=.\out\build.json
```

`--cgb=dmg` はDMG向け、`--cgb=cgb` は両モード用、`--cgb=cgb_only` はCGB専用の宣言です。CGB機能をDMGで動かす場合はハードウェア判定が必要です。ROMヘッダーの宣言だけでゲーム側の両対応が完成するわけではありません。

## 10　画像を書き込む時間
VBlankは画面の描画区切りです。VRAMやOAMへ無計画に書くと、画面の欠けや更新漏れが起きます。入門では画面OFF中に素材を転送し、通常画面では安全な組み込み関数やVRAMキューを使います。`_unsafe` / `_fast` の付いた関数は、呼び出し側が転送可能な時間を保証する必要があります。

OAM DMAのバッファは256バイト境界に配置し、GB版の `__oam_dma` には転送元アドレスを渡します。FC版の同名命令は引数なしなので混同しないでください。

## 11　ビルドコマンドと出力
`-o` は出力先、`-O0` / `-O1` は最適化、`--profile=dev|release|test` は複数の設定をまとめたプロファイルです。`--no-disasm` は逆アセンブル出力を省き、`--debug-out=...` や `--trace-out=...` は調査用ファイルの出力先です。速いビルドと詳細な調査で使い分けます。

```powershell
.\kitaqgb\kitaqgb.exe main.c -I .\kitaqgb\lib -o .\out\game.gb --profile=dev --diag-json=.\out\compile.json --emit-ai-metadata=.\out\build.json --debug-out=.\out\debug
```

`.map` は名前と配置、`.funcsizes.txt` は関数サイズ、`.dbg2.json` / `.source_map.txt` は実行位置とソースを結ぶ情報、`.build_report.json` はビルドの要約です。SARAKURAへの入力には、明示して出した `--emit-ai-metadata` のJSONを使うと経路がわかりやすくなります。

## 12　エラーを読む
エラーの先頭にあるファイル名・行・KQ番号を読みます。後続のエラーは先頭の構文ミスに連鎖していることがあります。まず最初のエラーを直します。未定義シンボルなら宣言・本体・ビルドへの追加を、ROM容量超過なら素材・関数サイズ・バンク配置を確認します。

```powershell
.\kitaqgb\kitaqgb.exe kqhelp KQ1002
.\kitaqgb\kitaqgb.exe symfind main --map=.\out\game.map
.\kitaqgb\kitaqgb.exe romdiff .\out\before.gb .\out\after.gb
```

## 13　インラインアセンブリ
`__asm { ... }` にKITAQGBの命令名を書けます。これは他のGBアセンブラのソースをそのまま受け付けるという意味ではありません。例えば `LD_A_IMM` のような内部形式の命令名があります。引数・戻り値・保持すべきレジスター・スタックを確認してから使います。命令名・オペランド形式は本書の付録を参照してください。

```c
void nop_example() {
    __asm { NOP }
}
```
''',
'gb-library':r'''
## 1　ライブラリの使い方
ライブラリは、繰り返し使う処理をまとめたCソースです。KITAQGB本体の `__` 組み込み関数を土台にしています。画面制御などの小さな機能から、物理、3D、通信まであります。

```c
#include "input.h"
// 起動時に一度
input_init();
// ゲームの1フレームに一度
input_update();
if (input_pressed(BTN_A)) { /* 決定処理 */ }
```

```powershell
.\kitaqgb\kitaqgb.exe .\kitaqgb\lib\input.c .\kitaq-docs\samples\gb_input.c -I .\kitaqgb\lib -I .\kitaq-docs\samples -o .\out\input.gb --profile=dev
```

各API辞典には宣言、所属ヘッダー、実装ソース、呼び出し例を掲載しています。既存例のない関数にも引数を受け渡す関数断片を新設しています。断片中のバッファやオブジェクトは呼び出し側が準備するものです。ROMとしてそのまま動かせる教材は「完全なサンプルプログラム」欄を使ってください。

## 2　1フレームの組み立て
`system_init` はフレーム管理を初期化し、`system_wait_vblank` は待機とフレーム番号更新を行います。GB版のVBlankコールバックはこの待機関数から呼ばれる協調処理です。ハードウェア割り込みへ自動登録されるという意味ではありません。

1. 入力を1回更新する。
2. 移動・当たり判定・ゲーム状態を計算する。
3. 描画コマンドとOAMを準備する。
4. VBlankに合わせて画面へ反映する。
5. 採用した方式の音楽更新を行う。

`vram_flush` や `sprite_flush_oam` のような待機付き処理を重ねると、1回のゲーム更新で2フレーム待ってしまうことがあります。待機済みなら対応する `_now` 関数を使う設計もできますが、呼ぶタイミングを自分で保証してください。

## 3　入力・リピート
`input_down(mask)` は押している間、`input_pressed(mask)` は押した瞬間、`input_released(mask)` は離した瞬間、`input_repeat(mask)` はメニュー向けの連続入力です。状態は `input_update()` ごとに更新されます。1フレーム中に何度もupdateすると押下エッジが失われます。

| ボタン | マスク |
| --- | --- |
| 右・左・上・下 | 0x01 / 0x02 / 0x04 / 0x08 |
| A・B・SELECT・START | 0x10 / 0x20 / 0x40 / 0x80 |

`gb_input.c` はAを押した回数を表示します。押し続けても増え続けないことを確かめ、`input_pressed` を `input_down` に変えて違いを試してください。

## 4　背景・文字・VRAM
`vram_queue_bg_tile` は1枚、`vram_queue_bg_rect` は長方形、`vram_queue_bg_block` は配列を転送する予約です。戻り値や `vram_get_overflowed()` を調べ、キュー容量を超えていないか確認します。転送元がポインタで保持される予約では、flush完了までデータを変更せず、有効なバンクとメモリを保ちます。

`text.c` / `menu.c` は `rpg.h` の文字・選択肢・ウィンドウを提供します。文字列からどのタイル番号を引くか、あらかじめどのフォントをVRAMに置くかを合わせて使います。本書の `m_text` のフォント配置とは自動的には共通になりません。

## 5　スプライト・アニメーション
`sprite_init`、`sprite_alloc`、`sprite_set_tile`、`sprite_set_pos` の順に準備します。GBでは全体40個、走査線あたり10個という制約があるため、メタスプライトを大量に並べる場合は行ごとの密度も考えます。`sprite_warn_scanline_overflow` と `sprite_max_scanline_count` は配置の調査に使えます。

`MetaSpritePart` は複数OBJの相対配置、`SpriteAnim` はタイルのフレーム番号と更新間隔を持ちます。`metasprite_draw` の数と確保したOBJ枠を合わせます。`gb_sprite.c` の文字Aも、文字のタイルをOBJに使った例です。

## 6　カラー・スクロール・ラスタ・カメラ
`cgb_bg_rgb` / `cgb_obj_rgb` のRGBは各0～31です。PCの0～255の値をそのまま渡しません。`CGB_RGB15` はこの3成分を16ビットの容器へ詰めます。高水準のCGBパレットヘルパーはDMGでは何もしないように作られています。

`Scroll_SetBg` は背景座標、`Scroll_SetWindow` はウィンドウ、`camera` はゲーム世界の座標から表示範囲を決めます。カメラの固定小数点値と画面のピクセル値を区別してください。

`raster.c` は画面を帯に分けるスクロール表や、行ごとのX方向変形を組み立てます。`Scroll_SplitCommit` 系はVBlank/STATベクターを使用します。別の音楽IRQ処理と同じベクターを独立に所有させず、必要なら共通ディスパッチャーを設計します。

## 7　音楽・効果音
`audio_hwregs_gb.c` → `audio.c` → ゲーム本体の順にコンパイルします。既にゲーム側にNR10～NR52等の定義があるなら、同じ定義ファイルを重ねません。`Audio_Init` の後、通常は1フレームに1回 `Audio_Update` を呼びます。

`Audio_PlayMusic(bank,song)` は曲のバンクを明示します。`Audio_PlaySFXBanked` は別バンクの効果音用です。優先度による競合を考慮して同じ音源チャンネルを譲り合います。GBの物理音源はCH1/CH2/CH3/CH4の4系統です。

音楽ストリームの `AUDIO_CMD_NOTE` / `AUDIO_CMD_SET_INST` だけは歴史的な番号順 **0=CH1、1=CH2、2=CH4、3=CH3** です。通常APIのチャンネル定数と混ぜないでください。現在のノート上限はヘッダーの `AUDIO_NOTE_MAX=67` です。

効果音の基本CH1ストリームはノートと音量値の組をフレームごとに読み、ノート0で終了します。CH3は別のマーカーと書式です。`gb_sound.c` を参照してください。フェードは `Audio_Update` で進むため、更新を止めるとフェードも止まります。

## 8　VBlank IRQ音楽
`audio_vblank.c` は別の方式です。1イベントは `delay, ch2_note, ch1_note, ch3_note, ch4_noise_param` の5バイトです。固定バンクの直接参照曲と、バンク曲をWRAMキューへ補充する方式があります。通常の `audio.c` のストリームをそのまま渡せません。

```powershell
# この方式を採用したROMに対してのみ行います。
.\kitaqgb\scripts\patch_gb_vblank_irq.ps1 .\out\game.gb .\out\game.map
```

パッチは0x0040のVBlankベクターを設定し、チェックサムを更新します。独自VBlank ISRやスクロール分割処理との所有権を確認します。ビルド成功だけで音が出たと判断せず、KOKURAで録音し、曲が進むことを確認してください。

## 9　固定小数点・物理・3D
`fixed.h` のQ8.8では256が1.0です。例えば128は0.5です。`fix_from_int`、`fix_mul`、`fix_to_int` を使う例を `gb_fixed.c` に示します。値が取り得る範囲を先に設計すると、オーバーフローを避けやすくなります。

`physics2d` は矩形、`physics2d_circle` は円、`physics3d` は3DのAABBを扱います。worldとbodyの配列を用意して初期化し、速度や重力を設定してstepを呼びます。矩形の位置・速度は整数画素／フレーム、逆質量や摩擦係数はQ8です。円のサンプルも位置40・速度2という整数単位で統一しています。逆質量0は固定物体です。円の1ステップ例は `gb_circle.c` です。係数の単位は各構造体定義を参照してください。

`wire3d` はDMGの128×120ワイヤー表示、`x3d` はX風の1bpp経路、`wire3d_cgb` はCGB専用の色付き経路です。使用WRAM・VRAM・転送方式が違います。複数のレンダラーを無計画に同時使用せず、画面とメモリの所有範囲を確保します。CGB版は倍速とDMAを使用し、`--cgb=cgb_only` が必要です。

## 10　ゲーム状態・オブジェクト・弾幕
`scene` はタイトル・ゲーム・ポーズ等の切り替え、`entity` は固定数のオブジェクトプール、`chain` は蛇・列車・ひもの座標履歴です。プールの生成失敗は0xFFなどの戻り値で確認し、成功を確認してから `entity_get` の指す先を使います。

`danmaku` は固定小数点の弾プール、方向・扇状生成、被弾・かすりなどを扱います。CGBのBG合成経路は通常のOBJ上限とは別ですが、更新時間とBG転送量の上限は残ります。多い弾数だけを目標にせず、1フレームの処理時間を測ります。

## 11　RPG・ADV・SLG・保存
`rpg.h` に乱数、フラグ、クエスト、圧縮、文字、メニュー、スクリプト、マップ、保存、経路探索の宣言がまとまっています。本体は `rng.c`、`flags.c`、`rle.c`、`text.c` などに分かれます。辞典の実装ファイルを確認して必要な単位だけ結合します。

`rng_seed` を固定すると乱数列を再現でき、テストが楽になります。`rand_range` / `rng_range` の上限の扱いは実装を確認してください。`flag_get` / `flag_set` はビット集合です。`save.c` はMBC5風SRAMアクセスを前提とした保存形式を持ち、ROMヘッダーのRAM容量とゲーム側の保存範囲を一致させます。

`slg.h` の盤面・合法手リスト・undoと、`slg_path.c` の経路探索は、ゲーム固有の評価やルールと分けて使います。幅・高さ・作業配列の大きさは、引数だけでなくライブラリ上限にも合わせます。

## 12　通信
基本の `link.c` はシリアルのバイト転送、`link_packet.c` は任意のパケット層です。`link_hwregs_gb.c` を先に結合します。ポーリングと割り込み方式では呼ぶ処理が異なり、割り込み方式のベクター0x0058はゲーム側で接続します。

論理的な `Link4_*` と物理Nintendo DMG-07用の `LinkDmg07_*` は別系統です。DMG-07は外部クロックで動き、`LinkDmg07_Poll` を高頻度に、`LinkDmg07_TickFrame` を1フレームに1回呼びます。1フレームに一度のPollだけでは間に合わない可能性があります。KOKURAのpair／dmg07ジョブを使い、接続、開始、切断、再接続を分けて試します。

## 13　バンク・素材・デバッグ
`bank.h` の `BankPtr` はバンク番号とポインタをまとめます。`far_data_read` は別バンクの素材をRAMへ読むための窓口です。`asset` は素材IDと記述表を結びます。素材の寿命・バンク・サイズはゲーム側で管理します。

`debug_trace_u8` / `debug_trace_u16` はRAM内の記録、`debug_assert_fail` はコード番号を残す機能です。PCのコンソールへ自動出力するprintfではありません。エミュレータのメモリ観測と合わせて読みます。`gb_debug.c` ではHP=42を記録します。
''',
'kitaqfc':r'''
## 1　KITAQFCとGB版の違い
KITAQFCはKITAQGBのフロントエンドを利用し、NES/Famicomの6502系CPUへコードを出すコンパイラです。GB用ROMをNESへ変換するツールではありません。画面、音、メモリ、マッパーに合わせてプログラムを作ります。

今回のビルド確認では、構造体のコピーと通常の関数呼び出しを含む教材が動きました。一方、**do-whileとswitchはNESコード生成で未対応エラー** になりました。構文解析コードに名前があるだけで「使用可能」としないでください。

## 2　準備とビルド
```powershell
MSBuild.exe .\kitaqfc\kitaqfc.csproj /t:Build /p:Configuration=Release
.\kitaqfc\bin\Release\kitaqfc.exe --help
```

以下では作業ツリーに配置済みの `kitaqfc.exe` を使う書式を示します。新しくビルドした版を使うときはEXEの場所を読み替えます。素材のCHRファイルとCコードは異なる入力です。本書の `font.chr` は作者指定の `ascii.c` を変換した8KiBのCHR素材です。

## 3　最初のプログラム
```c
#include "fc_common.h"
void main(void) {
    m_init();
    m_text(2, 5, "HELLO WORLD");
    m_number(42);
    while (1) { m_wait(); }
}
```

```powershell
.\kitaqfc\kitaqfc.exe .\kitaq-docs\samples\fc_hello.c -I .\kitaq-docs\samples -I .\kitaqfc\lib --mapper=nrom --nes-chr=.\kitaq-docs\samples\font.chr -o .\out\hello.nes --kurosaki-metadata=.\out\hello.debug.json
```

HELLO WORLDと042を表示します。共通ヘッダーの `m_wait` はVRAMキューをcommitしてNMIを待ち、スクロールを復元します。PPUADDRへの転送でスクロール内部状態が変化するため、復元を抜かすと文字が画面端へずれる場合があります。画面OFF→素材準備→描画ON→NMI同期の流れを覚えてください。

## 4　言語入門
GB巻の文と式の説明が共通の出発点です。FCでは `unsigned char` / `unsigned short` が使え、`core.h` に `u8` / `u16` / `s8` / `s16` の短い名前が定義されています。`fc.h` は集約ヘッダーです。引数なし関数は `void main(void)` の形式を使えます。

```c
#include "core.h"
u8 clamp_score(u8 n) {
    if (n > 99) return 99;
    return n;
}
```

整数は8ビットまたは16ビットの範囲で扱います。配列の添字は0からです。関数・ポインタ・構造体を使う実例は `fc_aggregate.c`、算術は `fc_arithmetic.c`、繰り返しは `fc_control.c` にあります。GB用のCGBレジスターやGB専用組み込み命令を混ぜないでください。

## 5　未対応構文の書き換え
```c
// do { update(); } while (condition);
// の代わりに、必ず1回実行してから条件を見る。
while (1) {
    update();
    if (!condition) break;
}
// switchの単純な振り分けはif/elseで表せる。
if (state == 0) { title_update(); }
else if (state == 1) { game_update(); }
else { pause_update(); }
```

このコードは説明用断片で、`update` 等は自分の関数名です。完全なROM例では `fc_control.c` を使います。再帰、間接関数呼び出し、可変長引数などもPC用Cと同じ保証を前提にしません。ライブラリのscene/entityコールバックは現在、保存だけして間接呼び出ししない箇所があります。

## 6　メモリとPPU
NESのCPU内部RAMは0x0000～0x07FFです。0x0800以降のミラーを別RAMのように配置しません。スタックは6502のページ1、OAMシャドウやキューにも予約領域があります。`--nes-local-ram=START:LENGTH` / `--nes-temp-ram=START:LENGTH` はマップを調べて使う上級設定です。

PPUのアドレス空間はCPUのメモリとは別です。CHRは絵のパターン、ネームテーブルはどのタイルをどこへ置くか、属性テーブルは色の選択、パレットは色番号です。背景の属性は通常16×16画素単位なので、GBのタイル属性と同じ操作にはなりません。

## 7　NMIとVRAMキュー
NMIは画面の区切りに来る割り込みです。描画中にPPUのメモリを直接大量更新すると表示が壊れます。起動時の描画OFF中は直接初期化し、通常更新では `__vramq_put` / `__vramq_copy` / `__vramq_fill` とcommitを使います。

```c
__vramq_put(0x2000 + 8 * 32 + 3, '4');
__vramq_commit();
__nmi_wait();
__scroll_set(0, 0);
```

キューの容量と転送元の寿命を確認します。デフォルトNMIはキュー処理を行います。独自 `__nes_nmi` を定義する場合は、必要なキュー実行・OAM・レジスター保存等を引き継ぎます。

## 8　マッパーとROM構成
| 指定 | 最初に考える用途 |
| --- | --- |
| nrom | 小さな固定ROMの教材 |
| uxrom / cnrom / axrom | 単純なPRGまたはCHR切り替え |
| mmc1 / mmc3 / mmc5 | 大きなゲームとマッパー固有機能 |
| vrc6 / vrc7 / fme7 | バンク制御と対応する拡張機能 |
| fds | ディスク形式の出力経路 |

この表はコンパイラの選択肢です。各エミュレータや実機での完成度一覧ではありません。`--board=surom512` はMMC1の特定基板構成を明示するためにあり、単にファイルを512KiBにすれば同じになるわけではありません。KUROSAKIのboard auditと組み合わせます。

```powershell
.\kitaqfc\kitaqfc.exe main.c --mapper=mmc3 --nes-chr=tiles.chr --mirroring=vertical -o .\out\game.nes --kurosaki-metadata=.\out\game.debug.json --emit-ai-metadata=.\out\build.json
```

`--battery` / `--no-battery`、CHR容量、PRG配置、バンク呼び出しは対象基板の条件を確認します。マッパーやミラーリングを変更したら、ROM生成だけでなく起動・スクロール・データ切り替えまで再確認します。

## 9　FDS・拡張音源・機器
FDSはディスクのファイル配置、起動方式、オーバーレイ、保存などを含む別の作業です。`fds_manifest_sample.json` とFDS関連ヘッダーを参照します。ディスクイメージを入力するエミュレータに、必要なBIOSや起動条件がある場合はその利用者自身の環境で準備します。本書の配布物にBIOSは含めません。

VRC6/VRC7音源を呼ぶだけでは、ROM側のマッパー設定は変わりません。選んだマッパーと実際に使う音源を一致させます。周辺機器は入力値が読めること、接続状態、通常のパッド入力への影響を別々に試します。

## 10　エラーとビルド結果
KQ番号を使う診断体系や `symfind` / `src2asm` / `romdiff` などの開発補助コマンドはGB版と似ています。ただしGB由来のヘルプに残る選択肢すべてがNES機能として実装済みとは限りません。FC巻の辞典はFC側のソース・ヘッダーで分けています。

KQ2421のようなPPU直接操作の警告は、画面OFFの初期化コードでも出ることがあります。警告を消すためだけに安全な初期化を崩さず、描画時刻と実行ログを確認します。エラー0と警告0を区別します。
''',
'fc-library':r'''
## 1　機能を選んで組み込む
`fc.h` はまとめて宣言を読むヘッダー、`core.h` は型、`intrinsics.h` はコンパイラ命令です。通常のCライブラリには対応する `.c` が必要です。ヘッダーだけのマクロ・組み込み関数には、同名の `.c` が不要な場合があります。

```powershell
.\kitaqfc\kitaqfc.exe .\kitaqfc\lib\audio.c .\kitaq-docs\samples\fc_sound.c -I .\kitaqfc\lib -I .\kitaq-docs\samples --nes-chr=.\kitaq-docs\samples\font.chr --mapper=nrom -o .\out\sound.nes
```

同じ名前のGB用 `lib` を `-I` に指定しないでください。例えば `__oam_dma()` はNES側では引数なしです。GB版のポインタ引数付きAPIを持ち込むと意味が変わります。

## 2　runtimeとsystem
`runtime.c` はPPUレジスター、OAMシャドウ、VRAMキューなどのCヘルパーを持ちます。一方 `__vramq_*` のような組み込み経路もあるため、どちらのデータをNMIが処理するか確認します。似た名前だけを根拠に、別のキューを混ぜないでください。

`system_init` はフレーム状態を初期化してNMIを有効にします。`system_wait_vblank` はNMIを待ってソフト側のフレーム数を増やします。**FC版の `system_set_vblank_callback` は値を保存しますが、現在の待機関数からコールバックを実行しません。** GB版と同じと思ってゲーム処理をコールバックだけへ置かないでください。

## 3　PPU・タイル・属性・パレット
`ppu_direct.h` は直接PPU操作、`vram_queue.h` はNMI更新、`tilemap` / `nametable_asset` は素材と表、`attribute` は属性更新、`palette` はパレット操作です。初期ロードと毎フレーム更新を分けます。

背景パレットは16バイト、スプライトパレットも16バイトのまとまりです。パレット番号はRGB値ではなくNESの色コードです。属性テーブルは複数タイルの色をまとめて選ぶので、1枚だけ色を変えるつもりでも周辺に影響する場合があります。

`ppu.h` の宣言と `ppu.c` の実装名が一致しないAPIが現存します。API辞典で **宣言のみ** と示すものは本体が見つからないため、入門例の直接呼び出し先にはしていません。動く教材では確認した組み込み命令を使います。宣言だけあるAPIを、結合すれば使える完成機能として扱わないでください。

## 4　OAM・メタスプライト・公平表示
NESは最大64スプライト、同一走査線に通常8個です。大量の敵や弾で9個以上が重なると、すべてを同時には表示できません。`metasprite` は複数OBJを1つの絵として置きます。確保範囲と終端データの形式を確認します。

`oam_fair.h` / `oam_fair_impl.h` は優先順位を保ちつつ候補の順序を回すための方式です。重要なプレイヤーやHUDを優先し、残りを時間で交替する設計に向きます。どれだけOAM順を入れ替えても、走査線あたりのハードウェア上限自体は変わりません。

## 5　入力・連打・周辺機器
`input.c` はNES生パッド値をGB風の `BTN_*` マスクへ変換します。**生のNESパッドではA=0x01、ライブラリのBTN_Aは0x10** です。KUROSAKIの `--pad1` にBTN_Aをそのまま渡さないでください。

`pad` は基本取得、`input_repeat` は押し続けたときのリピートです。`zapper`、`keyboard`、`rob`、`mic`、`midi` はそれぞれ機器の低水準窓口です。機器なしのゼロ値を「操作成功」と解釈せず、利用側の接続条件を確認します。

## 6　音源
`nes_apu_init` の後、`nes_sfx_square1` / `nes_sfx_square2` / `nes_sfx_triangle` / `nes_sfx_noise` を呼ぶと内蔵音源を鳴らせます。引数のperiodは周波数Hzそのものではなく、ハードウェアの周期値です。`fc_sound.c` はパルス音の最小例です。

DMCはサンプルのアドレス・長さ・アラインメント・再生レートの制限があります。ポインタを適当に渡さず、配置結果をマップで確認します。DMC DMAが入力読み取りと干渉する候補もあるため、安全パッド読み取りとKUROSAKIの診断を組み合わせます。

VRC6は追加パルス／鋸波、VRC7はFM音源のレジスター操作、FDSは波形音源です。対応マッパーのROMで使い、録音して変化を確認します。音源ライブラリはGBの `Audio_*` ドライバーとは別APIです。

## 7　シーン・アクター・エンティティ
`actor` / `entity` は固定配列のゲームオブジェクト、`scene` は場面の状態です。配列の上限を超えた生成を検出し、破棄したIDを使い続けないでください。関数ポインタを登録するAPIでも、現在のFC実装では登録だけで呼び出さない箇所があります。メインループから自分で状態別updateを呼ぶ方式を入門では推奨します。

`chain` は過去の座標を蓄積し、`collision` は矩形などの接触を判定します。動かす、衝突を調べる、描く、の順序を揃えると1フレーム遅れの判定を避けられます。

## 8　数学と物理
`fixed.h` はQ8.8、`math_fast` / `math_fixed` は高速な数値処理、`math_lut` は表による計算です。現行の `physics2d.h` は **Q5.3用の型と定数** を提供します。積分関数や更新マクロの本体はありません。これはGBの `physics2d` のworld/body APIと同じではありません。

Q5.3の小数部は1/8画素単位です。整数座標、小数部、速度、方向を分けて保持し、ゲーム側で加算・桁上がりを処理します。`fc_subpixel.c` は毎回2/8画素を8回加えて、40画素から42画素へ移動する完全例です。Q8.8の値256をQ5.3へそのまま流用しないでください。

## 9　素材・マッパー・FDS
`bank` / `asset` はPRGバンクと素材の記述を扱います。`mapper.h` の操作が実際に有効かは、ビルド時に選んだマッパーによります。スクロールIRQを使うときは、IRQの設定・有効化・ack・禁止を一組で設計します。

FDSは `fds_file`、`fds_overlay`、`fds_save`、`fds_sound` に分かれます。オーバーレイを切り替えると同じメモリに別コードが入るため、戻り先やデータの寿命を特に確認します。通常のカートリッジ用farcallと同じと決めつけないでください。

## 10　機能別の辞典と使用例
以下の辞典は公開ヘッダーごとに整理しています。関数、関数形式のマクロ、別名を区別し、構造体や定数はヘッダー全文からも読めます。実装のない宣言、保存だけのコールバック、特殊機器用の窓口は、動作を確認した一般機能と区別します。原ソースのコメントは正確さを保つため原文も残しています。
''',
'kokura':r'''
## 1　KOKURAとは
KOKURAはGB/CGB用のエミュレータと観測ツールです。ROMを動かすだけでなく、画面、音、CPU、メモリ、バンク、入力、診断イベントを記録します。本書では現在のCLI名 `kokura-cli.exe` を使います。過去の資料の `kokuradbg` 表記をそのまま実行ファイル名と思わないでください。

## 2　ビルドと最初の実行
```powershell
Push-Location .\kokura
cargo build -p kokura-cli --release
Pop-Location
.\kokura\target\release\kokura-cli.exe .\out\hello.gb --run-frames 120 --png .\out\hello.png --dump-report .\out\hello.json
```

Rust/Cargoの環境が必要です。CLIだけが必要なら上記の対象crateをビルドします。ROMは第1巻のhelloで作れます。引数を省いたフレーム数の既定値は1なので、見たい場面まで進めるには `--run-frames` を指定します。これは待機する秒数ではなく、エミュレータが進めるフレーム数です。

## 3　DMGとCGBを選ぶ
`--hardware auto` が既定で、`dmg` / `cgb` を明示できます。両対応ROMを確認するときは両モードで実行します。CGB専用ROMをDMGで起動できないことを、エミュレータの故障と混同しないでください。

```powershell
.\kokura\target\release\kokura-cli.exe .\out\game.gbc --hardware cgb --run-frames 180 --png .\out\cgb.png
```

## 4　入力を与える
`--input` は同時押し、`--input-seq` は時間順です。ボタン名は `A,B,START,SELECT,UP,DOWN,LEFT,RIGHT`、何も押さない区間は `NONE` を使います。PowerShellではセミコロンを含む入力列を引用符で囲みます。

```powershell
.\kokura\target\release\kokura-cli.exe .\out\game.gb --run-frames 120 --input-seq "NONE:30;A:1;NONE:89" --png .\out\after_a.png --dump-report .\out\after_a.json
```

押下エッジを調べるには離す区間も必要です。単にAを120フレーム押す試験は、Aを120回押す試験とは違います。サンプル入力教材なら上の入力でカウンターが1回増えることを目標にします。

## 5　画面・動画・音
`--png` は最後の画面、`--screenshot` と `--screenshot-frames` は選択したフレームの連続画像です。`--record-video` は動画、`--record-wav` は音の記録です。音源を使わないhelloのWAVが無音でも異常ではありません。

```powershell
.\kokura\target\release\kokura-cli.exe .\out\sound.gb --run-frames 180 --record-wav .\out\sound.wav --record-wav-frames 1:180 --png .\out\sound.png
.\kokura\target\release\kokura-cli.exe .\out\game.gb --run-frames 180 --record-video .\out\play.gif --record-video-frames 30:120
```

範囲指定は `開始:終了` です。ロードした状態の通算フレームと実行区間の番号を混同しないよう、レポートも残します。音の有無、音程、途切れ、クリップは別々に確認します。エミュレータ録音と実機録音が完全一致するという保証にはなりません。

## 6　状態の保存と再開
```powershell
.\kokura\target\release\kokura-cli.exe .\out\game.gb --run-frames 120 --save-state .\out\title.kqs
.\kokura\target\release\kokura-cli.exe .\out\game.gb --load-state .\out\title.kqs --input START --run-frames 30 --save-state .\out\started.kqs --png .\out\started.png
```

同じROMと同じエミュレータ版を基本にします。セーブステートはゲーム内セーブデータとは別です。CLIのKQS形式とC APIのJSON状態は同じファイル形式ではありません。拡張子を書き換えて相互に使わないでください。

## 7　シンボルとメモリの観測
ROMと同じ場所に `.map`、`.source_map.txt`、`.dbg2.json`、`.build_report.json` があれば自動検出されます。別のビルドの情報を同じ名前で置くと観測が誤解を招くため、ROMとsidecarを一組で保存します。

```powershell
.\kokura\target\release\kokura-cli.exe .\out\game.gb --symbols .\out\game.map --watch-window wram:0xC000:0x40 --run-frames 60 --dump-report .\out\watch.json
```

`wram` は窓のラベル、0xC000は先頭アドレス、0x40は長さです。観測窓を小さくすると、ゲームのどの変数が変化したか読みやすくなります。`--watch-baseline-mode` は初期値・前フレーム・名前付き基準からの比較方法を選びます。

## 8　停止条件・リプレイ・逆解析
`--breakpoint`、`--watchpoint`、`--run-until`、`--snapshot-at` は条件で止める・保存するための窓口です。引数の小言語はそれぞれ異なるため、下の実装書式とヘルプを参照してください。

```powershell
.\kokura\target\release\kokura-cli.exe .\out\game.gb --run-frames 120 --replay-interval 1 --replay-max-checkpoints 120 --dump-replay-tape .\out\baseline.replay.json --dump-report .\out\baseline.json
.\kokura\target\release\kokura-cli.exe .\out\game.gb --run-frames 120 --replay-interval 1 --compare-replay-tape .\out\baseline.replay.json --dump-report .\out\compare.json
```

最初に違った位置を調べてから、その周辺を細かく観測します。`--decompile-out` は疑似コードや制御フロー、`--disassemble-out` はCPU命令の表示です。デコンパイルは元のCソースや変数名を完全復元する機能ではありません。

## 9　診断をSARAKURAへ渡す
```powershell
.\kokura\target\release\kokura-cli.exe .\out\game.gb --run-frames 300 --emit-diagnostics .\out\gb_events.jsonl --dump-report .\out\run.json
.\sarakura\target\debug\sarakura.exe gb analyze --metadata .\out\build.json --events .\out\gb_events.jsonl --out .\out\gb_report --fail-on error
```

KOKURAの `--emit-diagnostics` は **JSONLファイル名** を受け取ります。例えば `out/gb_events.jsonl` を指定します。通常の実行レポートJSONやCPUトレースJSONLを、診断イベントと取り違えないでください。

## 10　通信ジョブ
pairは2台、four_player_adapterはホストが相手を選ぶ論理方式、dmg07は物理DMG-07プロトコルのモデルです。`--link-job` にJSONを渡す方法と、`--link-topology` / `--link-session` を指定する方法があります。

```powershell
.\kokura\target\release\kokura-cli.exe --link-topology pair --run-frames 120 --link-session "name=p1|slot=0|rom=out/host.gb|input=NONE" --link-session "name=p2|slot=1|rom=out/peer.gb|input=NONE" --dump-report .\out\pair.json
```

各ROMは通信を行うように作る必要があります。普通のhelloを2台動かしても通信ライブラリのテストにはなりません。セッションごとのROM、slot、入力、状態を残し、物理機器未確認の境界も記録します。

## 11　GUIと外部プログラムから使う
CLIの画面保存はGUIの操作ではありません。GUIやPLITAフロントエンドは別の実行面で、キー割り当てや対応機能はその実装に依存します。C ABIは `kokura-capi`、Pythonは同梱ブリッジから利用できます。まずCLIで最小の再現を作ると、GUI固有の問題とROM側の問題を分けられます。

## 12　レポートを読む順番
実行フレームと停止理由、画面、入力結果、音、エラーと警告、プロファイルの順に読みます。無入力のタイトル画面を長く観測すると、静止画面やPCループの警告が自然に出ることがあります。警告を機械的に故障と断定せず、意図した場面と照合します。
''',
'kurosaki':r'''
## 1　KUROSAKIとは
KUROSAKIはKITAQFCの情報を読み込めるNES/Famicom/FDSの観測エミュレータです。ROM調査、実行、録音、診断、スナップショット、リプレイ、逆アセンブル、デコンパイルをCLIから行えます。マッパーごとに実装の範囲が違うため、最初にROM情報と対応状態を調べます。

## 2　ビルドと起動
```powershell
Push-Location .\kurosaki
cargo build -p kurosaki-cli --release
.\target\release\kurosaki.exe --help
Pop-Location
```

以後の短い `kurosaki` コマンド例は、EXEのあるフォルダーをPATHへ設定した場合の書式です。設定していない場合は `& "EXEのフルパス"` に置き換えます。

```powershell
kurosaki inspect-rom .\out\hello.nes --json .\out\rom.json
kurosaki run .\out\hello.nes --frames 120 --png .\out\hello.png --json .\out\run.json
```

第4巻のhelloを使えば文字表示まで確かめられます。`inspect-rom` はヘッダーを調べる操作、`run` はCPU/PPUを進める操作です。前者が成功しても後者の動作保証にはなりません。

## 3　マッパー・基板の確認
`mapper-list` は登録済みの種類、`mapper-info` は特定種類の情報、`audit-board` は基板条件の検査です。マッパー番号はROMヘッダーと実配線の前提をつなぎます。名前だけから容量・CHR-RAM・固定バンクの条件を決めつけません。

```powershell
kurosaki mapper-list
kurosaki mapper-info 4
kurosaki audit-board .\out\surom.nes --expected-board surom512 --json .\out\board.json
```

`--allow-unimplemented` は未実装要素を許容して観測を進める指定です。これを付けて走ったことを、対応済みの証拠にはしません。

## 4　パッド入力
`run --pad1` / `--pad2` はNESの生ボタンマスクです。A=1、B=2、SELECT=4、START=8、UP=16、DOWN=32、LEFT=64、RIGHT=128です。複数同時押しは値を足します。

```powershell
kurosaki run .\out\game.nes --frames 120 --pad1 1 --png .\out\held_a.png --json .\out\held_a.json
```

この例は120フレームAを押し続けます。タイトル→ゲーム→決定といった時間順の操作にはリプレイを使います。`replay-record` のCLI例は基準となる無操作実行を記録するためのもので、人がGUIで操作する録画とは異なります。

## 5　スナップショットとリプレイ
```powershell
kurosaki snapshot-save .\out\game.nes --frames 120 --out .\out\title.kss.json
kurosaki snapshot-load .\out\title.kss.json
kurosaki replay-record .\out\game.nes --frames 120 --out .\out\baseline.replay.json
kurosaki replay-run .\out\game.nes .\out\baseline.replay.json --json .\out\replay.json
```

再開できる状態はversion 2のスナップショットです。ROMのSHA-256と状態の対応を保ちます。snapshot-resumeは保存時点から続きを進める操作、snapshot-rebaseは互換な別ROMへの明示的な契約付き付け替えです。修正ROMへ古い状態を無条件に流用すると、RAMやコード配置が変わっていて危険なので、通常は起動から同じ操作を再現します。

## 6　トレース・診断・プロファイル
```powershell
kurosaki trace .\out\game.nes --frames 2 --cpu --ppu --apu --mapper --nmi --dma --out .\out\trace.jsonl
kurosaki diagnose .\out\game.nes --frames 120 --out .\out\diagnostics.json --md .\out\diagnostics.md
kurosaki profile .\out\game.nes --frames 120 --out .\out\profile.json
```

トレースは何が起きたかの時系列、診断はルールに当たった観測、プロファイルはどこに処理が集中したかです。最初から長時間のfull traceを作るより、異常の直前直後を数フレームに絞ると読みやすくなります。

`--kitaqfc-debug` に同じビルドのデバッグJSONを渡します。ソース行までの情報がない観測を、自動で完全なソース行トレースだとは解釈しません。

## 7　音と画像の保存
```powershell
kurosaki audio-export .\out\sound.nes --frames 180 --wav .\out\sound.wav --json .\out\audio.json
kurosaki run .\out\game.nes --frames 120 --png .\out\frame.png --snapshot .\out\frame.kss.json --json .\out\frame.json
```

音源レジスターが変わったこと、PCMが生成されたこと、意図した音に聞こえることは別の検証です。内蔵音源と拡張音源は、対象マッパーも記録します。静止PNGだけでは移動や入力の正常性はわからないので、前後の状態・入力も残します。

## 8　逆アセンブルとデコンパイル
```powershell
kurosaki disasm .\out\game.nes --bytes 256 --text .\out\reset.txt
kurosaki decompile .\out\game.nes --format markdown --out .\out\decompile.md
```

disasmは命令列、decompileは関数境界候補・CFG・参照・疑似コードを出します。切り替え可能なバンクでは、CPUアドレスだけで元のROM位置が決まりません。必要なら `--snapshot` でマッパー状態を与え、実行トレースや注釈を補助情報として使います。元ソースの完全復元ではありません。

## 9　SARAKURAへつなぐ
```powershell
kurosaki run .\out\game.nes --frames 300 --emit-diagnostics .\out\kurosaki_events.jsonl --json .\out\run.json
sarakura fc analyze --metadata .\out\build.json --events .\out\kurosaki_events.jsonl --out .\out\fc_report --fail-on error
```

KUROSAKIの `--emit-diagnostics` は **JSONLファイル** を指定します。KOKURAと同様にファイル名を指定します。CPU traceファイルと診断イベントファイルを取り違えないでください。

## 10　GUIの操作
`cargo build -p kurosaki-gui --release` でGUIをビルドできます。ROMを開くかドロップし、矢印で方向、Z/XでA/B、EnterでSTARTを操作します。Spaceで実行／停止、Ctrl+Bでキャプチャbundle切り替え、Ctrl+Kでcheckpoint保存です。GUI文書とキー定義で確認した基本操作を掲載しています。

キャプチャの既定保存先は `%LOCALAPPDATA%\KUROSAKI\captures` です。`.kcb` は開始状態・トレース・終了状態等をまとめるフォルダー形式です。保存先のファイルが揃っていることを確かめてから共有します。CLI画像の確認は、GUIのDPIやキー操作まで確認したという意味ではありません。

## 11　FDS・保存データ
`fds-inspect` はディスクの構造、`export-assets` は素材の抽出窓口です。FDSは起動方式・BIOS・ディスクアクセスの条件も関わるため、NESカートリッジの試験と分けます。バッテリー保存 `.sav` とスナップショット `.kss.json` は用途が違います。実装に対応した保存レイアウトを確認して使います。

```powershell
kurosaki battery-export .\out\game.nes .\out\title.kss.json --out .\out\save.sav
kurosaki battery-run .\out\game.nes --sav .\out\save.sav --frames 120 --save-out .\out\next.sav --png .\out\battery.png
```

battery-exportは一致するROMとスナップショットから生の保存RAMを抽出します。battery-runはそのRAMを読み込んで電源投入から起動します。CPUやPPUの途中状態は復元しません。出力先は `--save-out` で明示します。保存RAMを持つ対応ROM用で、すべてのサンプルROMに使えるわけではありません。
''',
'sarakura':r'''
## 1　SARAKURAの仕事
SARAKURAは、コンパイラのビルド情報とエミュレータの診断イベントを整理し、修正や再テストを考えやすい形へ変換します。ROMを実行するエミュレータでも、Cコードを勝手に修正するプログラムでもありません。

## 2　準備
```powershell
Push-Location .\sarakura
cargo build -p sarakura-cli --release
.\target\release\sarakura.exe --help
Pop-Location
```

以下の `sarakura` はPATHが通った場合の略記です。通常は作成したEXEへのパスに置き換えて実行します。GBは `gb analyze`、FCは `fc analyze` を選びます。

## 3　初めての診断
必要な入力は2種類です。`--metadata` はビルド時のJSON、`--events` は実行時に出した診断JSONLです。JSONLは1行に1個のJSONオブジェクトが入る形式です。

```powershell
sarakura gb analyze --metadata .\out\build.json --events .\out\gb_events.jsonl --out .\out\report --fail-on error
```

出力の `report.html` をブラウザーで開きます。最初に対象、観測フレーム、エラー件数、警告件数を確認し、それから個々の診断を読みます。`--frames` は解析条件の情報で、SARAKURAがその数だけROMを実行する指定ではありません。

## 4　入力を先に点検する
```powershell
sarakura inspect-metadata --metadata .\out\build.json
sarakura inspect-events --events .\out\gb_events.jsonl
sarakura emitter-check gb --metadata .\out\build.json --events .\out\gb_events.jsonl --strict
```

ファイルが読めない、platformが違う、event_typeが規約と合わない、といった問題を先に分けます。通常のエミュレータJSONレポートをeventsに渡すだけでは、正しい診断入力になりません。

## 5　診断の読み方
errorは優先して調べる問題、warnは条件次第で問題になり得る観測、infoは参考情報です。分類は重大さの手掛かりで、ゲームの意図を完全には理解しません。例えばタイトルの待機ループとゲームのフリーズは、CPUが同じ場所を回るという観測だけでは区別できない場合があります。

ROMのSHA、入力手順、場面、画面、音、ソース位置を一緒に確認します。修正する前後で条件を揃えないと、診断が減った理由がコード改善なのか別場面を走ったからなのかわからなくなります。

## 6　出力ファイルの役割
標準の説明文・診断ヒント・修正指示は英語です。HTMLには `lang="en"` を指定しています。利用者が渡した文字列やイベントIDを自動翻訳するものではありません。通常は一部のプロジェクト名・パスを置換しますが、アドレスや観測内容をすべて匿名化する機能ではありません。解析結果を公開する際は内容を確認してください。

| ファイル | 読み方 |
| --- | --- |
| ai_diagnostics.json | 機械が扱いやすい正規化診断 |
| diagnostic_summary.json | 件数と概要 |
| report.html | 人が読むHTML報告 |
| repair_prompt.md | 修正検討を始めるための説明 |
| repair_plan.json / .md | 修正順や対象の計画 |
| automation_plan.json / .md | ツール能力を踏まえた作業計画 |
| retest_plan.json | 再確認の計画 |
| repro_bundle.zip | 再現情報の束 |

計画が作られたことと、その計画が実行されたことは別です。CファイルやROMを修正したら、コンパイラ→エミュレータ→SARAKURAをもう一度実行します。

## 7　カタログ・絞り込み・カバレッジ
```powershell
sarakura catalog gb --json
sarakura catalog fc --json
sarakura pack-plan gb
sarakura coverage gb --events .\out\gb_events.jsonl --out .\out\coverage.json
```

catalogは診断ルールの一覧、pack-planは分野ごとの組、coverageは今回どのルールに対応するイベントが観測されたかを調べます。カタログ項目が存在しても、今回のエミュレータがそのイベントを必ず出せるとは限りません。

```powershell
sarakura gb analyze --metadata .\out\build.json --events .\out\gb_events.jsonl --out .\out\ppu_report --diagnostic-pack ppu --min-severity warn --fail-on error
```

`--diagnostic-rule` はイベント名またはカタログID、`--phase` は段階、`--diagnostic-pack` は分野で選びます。フィルターで見えなくした診断を「解決した」と数えないでください。

## 8　修正前後を比較する
```powershell
sarakura baseline-delta --baseline .\out\before --current .\out\after --out .\out\delta --markdown .\out\delta --fail-on-new error --fail-on-regression error --enforce
```

newは新規、resolvedは解消、improvedは改善、persistingは残存、regressedは悪化の分類です。既存の問題が残っているかと、新しい問題を入れたかを分けて読みます。入力・フレーム・診断フィルターを固定して比較してください。

## 9　検証とCI
```powershell
sarakura validate .\out\report\ai_diagnostics.json --strict
sarakura ci-summary --diagnostics .\out\report --fail-on error --enforce
sarakura schema export --out .\out\schemas
```

CIは繰り返し確認を自動化する仕組みです。`ci-summary` は `--enforce` を付けて初めて判定をプロセス終了コードへ反映します。付けない場合はJSON内の判定結果を読む動作です。analyzeの `--fail-on error` はerror以上があれば非ゼロ終了にします。analyzeの既定の `never` は診断が出ても失敗扱いにしないので、CIでは目的に合わせて明示します。`warn` を選ぶと警告も失敗条件に入ります。

```powershell
sarakura ci-summary --diagnostics .\out\report --fail-on error --enforce
if ($LASTEXITCODE -ne 0) { throw "診断の失敗条件に該当しました" }
```

スキーマのvalidate成功は形式の検証です。ゲームが期待通り遊べることの検証には、入力・画面・音の試験も必要です。

## 10　再現用ファイルを扱う
`normalize-events` はイベントの正規化、`inspect-repro` は再現bundleの中身の確認です。共有前に、今回のROMと情報が対応しているか、必要な入力手順が含まれるかを確認します。`--allow-project-labels` はプロジェクト由来のラベルや識別子を残したい場合の明示指定です。

## 11　最小の練習用入力
本書には小さなGB/FCビルド情報とイベントのサンプルを同梱しています。[GBの合成データの診断結果](verification/sarakura-gb-synthetic.html) と [FCの合成データの診断結果](verification/sarakura-fc-synthetic.html) も閲覧できます。`samples/sarakura_demo.ps1` はそれを解析する手順です。これは診断書式を学ぶための合成データで、実際のROMから採取した証拠ではありません。実ROMの試験はKOKURA/KUROSAKIから採取したイベントで行います。

## 12　修正と再テストの一巡
1. 同じROM・入力で問題を再現し、ログと画像を保存する。
2. SARAKURAで候補を整理し、関係するソースを読む。
3. 原因に対応する狭い修正を行う。
4. 同じ操作で再ビルド・再実行する。
5. baseline-deltaと画面・音・ゲームの挙動を照合する。

この一巡を小さく回すことが、最初から全機能を同時に調べるより理解しやすい進め方です。
'''
}
