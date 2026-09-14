# Authored game-development prompts

`ja/gb.md` and `ja/fc.md` contain the Japanese prompts. Each other language has
an authored `text.json` with shared and platform-specific prose. `commands/`
contains literal PowerShell examples shared by those editions. `pt` uses
Brazilian Portuguese. No translation service is used by the generator.

Run `python -B tools/generate_prompts.py` from the manual root after editing
these files. It generates `loop-engineering.html` in all nine editions,
18 downloadable files under `prompts/`, and numbered reference examples after
the teaching chapters in the KITAQGB and KITAQFC manuals. Other software and
library manuals do not contain game-development prompts.
The standard Japanese, English and localized generators also call it for
their own edition, so regenerating a manual preserves prompt navigation.

Run `python -B tools/publish_readme_prompts.py <repositories-directory>` to
insert the complete, collapsible examples immediately after the development
philosophy in both compilers' READMEs. The directory must contain the `kitaqgb`
and `kitaqfc` checkouts. `placement.json` supplies localized chapter and README
labels. README links open the same-language compiler chapter directly.

The prompt pages provide a complete-prompt copy button as well as individual
command copy buttons. Downloads contain the same text as complete-prompt copy.
Run `python -B tools/check_site.py` to check all local links and anchors.

The command examples are starting points. They do not constitute a complete
game or evidence that a future game's acceptance criteria have been met.

## 日本語

日本語原稿は `ja/gb.md` と `ja/fc.md`、各言語の原稿は `text.json` にあります。
`commands/` のコマンドは各言語で共有し、ポルトガル語はブラジル表記です。
生成処理は翻訳サービスを使用しません。

編集後はマニュアル直下で `python -B tools/generate_prompts.py` を実行してください。
9言語のHTML、18本のMarkdown、KITAQGB・KITAQFCの項番付き参考例を生成します。
参考例は基本事項の説明に続けて配置し、他のソフトウェアやライブラリの説明書には載せません。通常の各言語版の
生成処理からも呼び出すため、再生成してもプロンプトへのリンクを保持します。
`python -B tools/check_site.py` でローカルリンクとアンカーを確認できます。

`python -B tools/publish_readme_prompts.py <リポジトリの親ディレクトリ>` を実行すると、
両コンパイラのREADMEの開発方針の直後に、全文を折りたたんで表示できる参考例を挿入します。
指定先には `kitaqgb` と `kitaqfc` のリポジトリが必要です。READMEからは同じ言語のHTML内の該当項目へ直接移動できます。
