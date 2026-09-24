# KITAQ SERIES Manuals

<!-- manual-language-links:start -->
| Language / 言語 | HTML |
| --- | --- |
| English | [KITAQGB](https://bartaro.github.io/kitaq-docs/en/kitaqgb.html) · [KITAQGB Library](https://bartaro.github.io/kitaq-docs/en/gb-library.html) · [KOKURA](https://bartaro.github.io/kitaq-docs/en/kokura.html) · [KITAQFC](https://bartaro.github.io/kitaq-docs/en/kitaqfc.html) · [KITAQFC Library](https://bartaro.github.io/kitaq-docs/en/fc-library.html) · [KUROSAKI](https://bartaro.github.io/kitaq-docs/en/kurosaki.html) · [SARAKURA](https://bartaro.github.io/kitaq-docs/en/sarakura.html) |
| 日本語 | [KITAQGB](https://bartaro.github.io/kitaq-docs/kitaqgb.html) · [KITAQGB Library](https://bartaro.github.io/kitaq-docs/gb-library.html) · [KOKURA](https://bartaro.github.io/kitaq-docs/kokura.html) · [KITAQFC](https://bartaro.github.io/kitaq-docs/kitaqfc.html) · [KITAQFC Library](https://bartaro.github.io/kitaq-docs/fc-library.html) · [KUROSAKI](https://bartaro.github.io/kitaq-docs/kurosaki.html) · [SARAKURA](https://bartaro.github.io/kitaq-docs/sarakura.html) |
<!-- manual-language-links:end -->

<!-- ai-prompts:start -->
### AI game development prompts

Fill in the requirements, then give the complete prompt to your AI assistant. It covers implementation, emulator testing, SARAKURA analysis and retesting.

[KITAQGB](https://bartaro.github.io/kitaq-docs/en/loop-engineering.html#gb) · [KITAQFC](https://bartaro.github.io/kitaq-docs/en/loop-engineering.html#fc)

### 生成AIによるゲーム開発プロンプト

依頼内容を記入して、プロンプト全文を生成AIに渡してください。実装、エミュレータ検証、SARAKURA解析、修正後の再検証まで含みます。

[KITAQGB](https://bartaro.github.io/kitaq-docs/loop-engineering.html#gb) · [KITAQFC](https://bartaro.github.io/kitaq-docs/loop-engineering.html#fc)
<!-- ai-prompts:end -->



[English](#english) | [日本語](#japanese)

<a name="english"></a>

## English

[Japanese manuals](https://bartaro.github.io/kitaq-docs/) / [English manuals](https://bartaro.github.io/kitaq-docs/en/) / [Source checkout and layout](GITHUB_SETUP.md)

### HTML manuals

Seven volumes are presented in Japanese and English, based on the source snapshot of September 14, 2026. The reference inventory contains 1,055 API entries and 47 complete sample programs. Open `en/index.html` for English or `index.html` for Japanese; each volume provides language navigation. The sample explanations identify the tested behavior and conditions.

Original source excerpts are preserved verbatim; captured emulator screens appear beside the sample explanations. See [GitHub setup](GITHUB_SETUP.md) and [publication checks](PUBLICATION_CHECKS.md). The HTML files support offline reading, searching within a volume, copying code and printing.

| File | Contents |
|---|---|
| kitaqgb.html | KITAQGB syntax, compiler intrinsics and builds |
| gb-library.html | KITAQGB libraries |
| kokura.html | KOKURA execution, input, observation and recording |
| kitaqfc.html | KITAQFC syntax, compiler intrinsics and builds |
| fc-library.html | KITAQFC libraries |
| kurosaki.html | KUROSAKI execution, saving and analysis |
| sarakura.html | SARAKURA diagnostics and retesting |
| verification.html | Sample screens |

The contents page and the beginning of volume 1 explain the two meanings of the name and acknowledge NORCAL. Letters, digits and symbols use the supplied `samples/assets/ascii.c`. GB assets are reordered into ASCII order; FC assets are converted to NES bitplanes. The glyph shapes are unchanged.

The prose, additional samples and generation tools use the MIT License. On September 12, 2026, the author confirmed that the supplied 92 glyphs are original work and may be published under MIT. Excerpts from the original software retain their copyright notices. Redistribute [third-party notices](THIRD_PARTY_NOTICES.md) and the applicable licenses together.

The manuals include the [English license](LICENSE) and a [Japanese reference translation](LICENSE.ja). [Third-party notices](THIRD_PARTY_NOTICES.md) link to the Japanese licenses of the individual tools. The English original takes precedence if the translations differ. Software binary distributions also require the separate licenses of their dependencies. Permission to publish these manuals does not mean that every tool and dependency can be redistributed under MIT alone.

### Game programming guide

[HARAPEKO SHIROHEBI — English](https://bartaro.github.io/kitaq-docs/apps/harapeko_shirohebi/guide-en.html): program flow, snake movement and KITAQGB library usage. [Source and build instructions](https://github.com/bartaro/kitaqgb/tree/main/apps/harapeko_shirohebi).

### Build the samples

Clone the repositories as siblings under one parent directory and run the following commands from that parent. See [GITHUB_SETUP.md](GITHUB_SETUP.md) for the layout. Use the supplied compilers or rebuild them using the manual instructions; this edition includes compiler fixes.

```powershell
.\kitaq-docs\samples\build.ps1 -Only gb_hello,fc_hello
.\kitaq-docs\samples\build.ps1
```

For another source location, set `-Root "absolute path to the source tree"`. Select executables stored elsewhere with `-GbCompiler` and `-FcCompiler`. Generated ROMs and logs go to `samples/out/<sample-id>` by default. This manual package contains no compiler executables, commercial ROMs or BIOS files.

`samples/api-fragments` contains code fragments that require initialization and valid arguments in their surrounding programs. The batch ROM build covers the 47 programs in `samples/manifest.json`. Each volume distinguishes declaration-only APIs, unexecuted fragments and features not verified on physical hardware.

### Publish on GitHub

1. Place this folder's contents at the repository root or inside a `docs` folder.
2. Upload `index.html`, all seven volumes, `verification.html`, `loop-engineering.html`, `prompts`, the language directories, `assets`, `samples`, `reference`, `verification`, the README and license notices together. Include `.nojekyll`.
3. In GitHub Settings → Pages → Build and deployment, set Source to Deploy from a branch.
4. Select the uploaded branch and `/ (root)` or `/docs`, then save.
5. After publication completes, open the URL shown in Pages and check the contents and volume links.

See [GitHub's publishing-source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). `manual/_manual_work` is a local build and verification workspace and is excluded from publication.

### Edit and update

Japanese prose lives in `tools/chapters.py`, English prose in `tools/en/*.md`, English generation in `tools/generate_en.py`, API dictionaries and page generation in `tools/generate.py`, and styling in `assets/manual.css`. Use Python to update the manuals.

```powershell
python -B kitaq-docs/tools/collect.py
python -B kitaq-docs/tools/make_samples.py
python -B kitaq-docs/tools/catalog.py
python -B kitaq-docs/tools/generate.py
python -B kitaq-docs/tools/generate_en.py
foreach ($language in @('ko','zh-CN','zh-TW','es','pt','fr','de')) {
    python -B kitaq-docs/tools/generate_i18n.py --language $language
    if ($LASTEXITCODE -ne 0) { throw "Manual generation failed: $language" }
}
python -B kitaq-docs/tools/check_site.py
python -B kitaq-docs/tools/check_bilingual.py
```

Captured screens are included with the sample explanations. Build logs, execution logs and raw local verification records are excluded from the public files. Before uploading, use `tools/export_public.py` to export the manual into a separate Git checkout. See [third-party notices](THIRD_PARTY_NOTICES.md).

### Scope of this source publication

KOKURA-GUI, KUROSAKI-GUI and PLITA are excluded from this upload. The published sources and manuals cover the CLI, core and integration APIs.

---

<a name="japanese"></a>

## 日本語

[日本語 / Japanese](https://bartaro.github.io/kitaq-docs/) / [English](https://bartaro.github.io/kitaq-docs/en/) / [ソースの取得と配置](GITHUB_SETUP.md)

### 日本語・英語のHTMLマニュアル

2026年9月14日のソースに基づく7冊のマニュアルを日本語・英語で収録しています。各言語版に共通の1,055個のAPI項目と47本の完全なサンプルプログラムがあります。英語版は `en/index.html`、日本語版は `index.html` から開けます。各巻上部で言語を切り替えられます。サンプルの説明には期待結果と確認した実行画像を掲載しています。

全言語に同じ1,055件のAPIと47本の完成サンプルを収録しています。元のソース抜粋は原文のまま保持し、確認した実行画像をサンプルの説明に添えています。[取得・配置手順](GITHUB_SETUP.md)と[公開時の確認記録](PUBLICATION_CHECKS.md)も参照してください。
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
| verification.html | サンプルの実行画面 |

名称の二つの意味とNORCALへの謝辞は総合目次と第1巻の冒頭にあります。
英数字・記号は指定された `samples/assets/ascii.c` を使用しています。
GBではASCII順へ並べ、FCではNESのビットプレーン形式へ変換しています。字形は変更していません。

本文・追加サンプル・生成ツールはMITライセンスです。指定の92字形も、2026-09-12に作者から自作・MIT公開可の確認を得ています。元ソフトからの抜粋は原著作権表示を保持しています。[権利表記](THIRD_PARTY_NOTICES.md) と各LICENSEを一緒に配布してください。
マニュアルのライセンスは[英語原文](LICENSE)と[日本語参考訳](LICENSE.ja)を同梱しています。各ソフトの日本語版へのリンクは[権利表記](THIRD_PARTY_NOTICES.md)にあります。解釈に相違がある場合は英語原文を優先します。
ソフト本体のバイナリ配布では依存クレート等の別ライセンスも必要です。このマニュアルの公開許諾と、全ソフト・全依存物がMITだけで再配布できるという判断は異なります。

### ゲームのプログラム解説

[はらぺこしろへび — 日本語](https://bartaro.github.io/kitaq-docs/apps/harapeko_shirohebi/guide-ja.html)：フローチャート、白ヘビの挙動、KITAQGBライブラリの使い方。[ソースとビルド方法](https://github.com/bartaro/kitaqgb/tree/main/apps/harapeko_shirohebi)。

### サンプルをビルド

各リポジトリを同じ親フォルダーの直下にcloneし、その親フォルダーから実行します。配置は [GITHUB_SETUP.md](GITHUB_SETUP.md) を参照してください。
配布済みコンパイラを使うか、マニュアルの手順で再ビルドしてください。本版にはコンパイラ修正も含まれます。

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

### GitHubへ置く

1. このフォルダーの内容を、公開するリポジトリのルート、または `docs` フォルダーへ置きます。
2. `index.html`、7冊、`verification.html`、`loop-engineering.html`、`prompts`、各言語のフォルダー、`assets`、`samples`、`reference`、`verification`、READMEと権利表記を一緒にアップロードします。`.nojekyll` も含めます。
3. GitHubの Settings → Pages → Build and deployment で、Sourceを Deploy from a branch にします。
4. アップロード先のブランチと `/ (root)` または `/docs` を選び、Saveします。
5. 公開処理が完了したら、Pages欄に表示されたURLから目次と各巻のリンクを確かめます。

手順の根拠：[GitHub公式の公開元設定](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。
`manual/_manual_work` はローカルのビルド・検証作業領域で、公開対象には含めません。

### 編集と更新

日本語本文は `tools/chapters.py`、英語本文は `tools/en/*.md`、英語版生成は `tools/generate_en.py`、API辞典とページ生成は `tools/generate.py`、
見た目は `assets/manual.css` にあります。Pythonで更新できます。

```powershell
python -B kitaq-docs/tools/collect.py
python -B kitaq-docs/tools/make_samples.py
python -B kitaq-docs/tools/catalog.py
python -B kitaq-docs/tools/generate.py
python -B kitaq-docs/tools/generate_en.py
foreach ($language in @('ko','zh-CN','zh-TW','es','pt','fr','de')) {
    python -B kitaq-docs/tools/generate_i18n.py --language $language
    if ($LASTEXITCODE -ne 0) { throw "Manual generation failed: $language" }
}
python -B kitaq-docs/tools/check_site.py
python -B kitaq-docs/tools/check_bilingual.py
```

確認した画像はサンプルの説明とともに掲載しています。ビルドログ・実行ログ・ローカルの検証記録は公開ファイルに含めません。アップロードする前に、`tools/export_public.py`で別のGit作業フォルダへマニュアルを書き出してください。権利表記は[第三者の権利に関する通知](THIRD_PARTY_NOTICES.md)を参照してください。

### 今回のソース公開範囲

KOKURA-GUI、KUROSAKI-GUI、PLITAは今回のアップロード対象外です。今回の公開ソースとマニュアルはCLI・コア・連携APIを対象としています。本体・CLI・連携APIを利用してください。
