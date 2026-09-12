# KITAQ SERIES Manuals

[日本語 / Japanese](https://bartaro.github.io/kitaq-docs/) / [English](https://bartaro.github.io/kitaq-docs/en/) / [ソースの取得と配置](GITHUB_SETUP.md)

## 日本語・英語HTMLマニュアル / Japanese and English HTML manuals

2026年9月12日のソースを基準にした7冊を、日本語と英語で収録しています。英語版は2026年9月13日に作成しました。英語版は `en/index.html`、日本語版は `index.html` から開けます。各巻上部で言語を切り替えられます。

Seven complete volumes are available in both languages, with the same 1,029 API entries and 47 sample programs. Open `en/index.html` for English or `index.html` for Japanese. Original source excerpts and recorded tool output are preserved verbatim. See [GitHub setup](GITHUB_SETUP.md) and [publication checks](PUBLICATION_CHECKS.md).
`index.html` を開いてください。オフラインで閲覧・巻内検索・コードのコピー・印刷ができます。

| ファイル | 内容 |
|---|---|
| kitaqgb.html | KITAQGBの文法・組み込み命令・ビルド |
| gb-library.html | KITAQGBライブラリ |
| kokura.html | KOKURAの実行・入力・観測・記録 |
| kitaqfc.html | KITAQFCの文法・組み込み命令・ビルド |
| fc-library.html | KITAQFCライブラリ |
| kurosaki.html | KUROSAKIの実行・保存・解析 |
| sarakura.html | SARAKURAの診断と再テスト |
| verification.html | 実際のビルド・実行・画面照合の記録 |

名称の二つの意味とNORCALへの謝辞は総合目次と第1巻の冒頭にあります。
英数字・記号は指定された `samples/assets/ascii.c` を使用しています。
GBではASCII順へ並べ、FCではNESのビットプレーン形式へ変換しています。字形は変更していません。

本文・追加サンプル・生成ツールはMITライセンスです。指定の92字形も、2026-09-12に作者から自作・MIT公開可の確認を得ています。元ソフトからの抜粋は原著作権表示を保持しています。[権利表記](THIRD_PARTY_NOTICES.md) と各LICENSEを一緒に配布してください。
マニュアルのライセンスは[英語原文](LICENSE)と[日本語参考訳](LICENSE.ja)を同梱しています。各ソフトの日本語版へのリンクは[権利表記](THIRD_PARTY_NOTICES.md)にあります。解釈に相違がある場合は英語原文を優先します。
ソフト本体のバイナリ配布では依存クレート・GUIフォント等の別ライセンスも必要です。このマニュアルの公開許諾と、全ソフト・全依存物がMITだけで再配布できるという判断は異なります。

## サンプルをビルド

各リポジトリを同じ親フォルダーの直下にcloneし、その親フォルダーから実行します。配置は [GITHUB_SETUP.md](GITHUB_SETUP.md) を参照してください。
先に各コンパイラをマニュアルの手順でビルドしてください。本版にはコンパイラ修正も含まれます。

```powershell
.\kitaq-docs\samples\build.ps1 -Only gb_hello,fc_hello
.\kitaq-docs\samples\build.ps1
```

別の場所に展開した場合は `-Root "ソースツリーの絶対パス"` を指定します。
EXEを別配置にしている場合は `-GbCompiler` / `-FcCompiler` で選べます。
生成したROMとログは既定では `samples/out/サンプル名` に入ります。
公開用ファイルにはコンパイラEXE・商用ROM・BIOSは含めません。

`samples/api-fragments` は初期化と有効な引数を用意して組み込む断片例です。
一括ROMビルドの対象は `samples/manifest.json` の47プログラムです。
宣言のみのAPI、実行していない断片、実機未確認の機能は各巻で区別しています。

## GitHubへ置く

1. このフォルダーの内容を、公開するリポジトリのルート、または `docs` フォルダーへ置きます。
2. `index.html`、7冊、`verification.html`、`assets`、`samples`、`reference`、`verification`、READMEと権利表記を一緒にアップロードします。`.nojekyll` も含めます。
3. GitHubの Settings → Pages → Build and deployment で、Sourceを Deploy from a branch にします。
4. アップロード先のブランチと `/ (root)` または `/docs` を選び、Saveします。
5. 公開処理が完了したら、Pages欄に表示されたURLから目次と各巻のリンクを確かめます。

手順の根拠：[GitHub公式の公開元設定](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。
`manual/_manual_work` はローカルのビルド・検証作業領域で、公開対象には含めません。

## 編集と更新

日本語本文は `tools/chapters.py`、英語本文は `tools/en/*.md`、英語版生成は `tools/generate_en.py`、API辞典とページ生成は `tools/generate.py`、
見た目は `assets/manual.css` にあります。Pythonで更新できます。

```powershell
python kitaq-docs/tools/collect.py
python kitaq-docs/tools/make_samples.py
python kitaq-docs/tools/catalog.py
python kitaq-docs/tools/verify_samples.py --runtime
python kitaq-docs/tools/workflow.py
python kitaq-docs/tools/check_pixels.py
python kitaq-docs/tools/generate.py
python kitaq-docs/tools/generate_en.py
python kitaq-docs/tools/check_site.py
python kitaq-docs/tools/check_bilingual.py
```

ソース採取・ビルドには元のソースツリーと各ツールが必要です。字体変換・画面照合にはPillowを使用します。
単なるHTML閲覧にはPythonもサーバーも不要です。ソースやEXEを更新したら、古い検証結果をそのまま流用しないでください。
変更内容は [compiler_fixes.md](verification/compiler_fixes.md)、権利表記は [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) を参照してください。

## 今回のソース公開範囲

KOKURA-GUI、KUROSAKI-GUI、PLITAは今回のアップロード対象外です。マニュアル内のGUIの説明は参考情報として残していますが、今回の公開ソースからはGUIをビルドできません。本体・CLI・連携APIを利用してください。
