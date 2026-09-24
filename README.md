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

[Japanese manuals](https://bartaro.github.io/kitaq-docs/) / [English manuals](https://bartaro.github.io/kitaq-docs/en/)

### HTML manuals

Seven volumes are presented in Japanese and English, based on the source snapshot of September 14, 2026. The reference inventory contains 1,055 API entries and 47 complete sample programs. Open `en/index.html` for English or `index.html` for Japanese; each volume provides language navigation. The sample explanations identify the tested behavior and conditions.

Original source excerpts are preserved verbatim; captured emulator screens appear beside the sample explanations. The HTML files support offline reading, searching within a volume, copying code and printing.

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

---

<a name="japanese"></a>

## 日本語

[日本語 / Japanese](https://bartaro.github.io/kitaq-docs/) / [English](https://bartaro.github.io/kitaq-docs/en/)

### 日本語・英語のHTMLマニュアル

2026年9月14日のソースに基づく7冊のマニュアルを日本語・英語で収録しています。各言語版に共通の1,055個のAPI項目と47本の完全なサンプルプログラムがあります。英語版は `en/index.html`、日本語版は `index.html` から開けます。各巻上部で言語を切り替えられます。サンプルの説明には期待結果と確認した実行画像を掲載しています。

全言語に同じ1,055件のAPIと47本の完成サンプルを収録しています。元のソース抜粋は原文のまま保持し、確認した実行画像をサンプルの説明に添えています。
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
