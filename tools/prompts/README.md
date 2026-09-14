# Authored game-development prompts

`ja/gb.md` and `ja/fc.md` contain the Japanese prompts. Each other language has
an authored `text.json` with shared and platform-specific prose. `commands/`
contains literal PowerShell examples shared by those editions. `pt` uses
Brazilian Portuguese. No translation service is used by the generator.

Run `python -B tools/generate_prompts.py` from the manual root after editing
these files. It generates `loop-engineering.html` in all nine editions,
18 downloadable files under `prompts/`, and links in the existing volumes.
The standard Japanese, English and localized generators also call it for
their own edition, so regenerating a manual preserves prompt navigation.

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
9言語のHTML、18本のMarkdown、各巻からのリンクを生成します。通常の各言語版の
生成処理からも呼び出すため、再生成してもプロンプトへのリンクを保持します。
`python -B tools/check_site.py` でローカルリンクとアンカーを確認できます。
