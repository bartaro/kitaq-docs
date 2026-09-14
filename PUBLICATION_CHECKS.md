# Publication checks

## Documentation and source scope — September 14, 2026

The seven manuals, contents page and verification page are provided in English,
Japanese, Korean, Simplified Chinese, Traditional Chinese, Spanish, Brazilian
Portuguese, French and German: 81 manual pages. All editions share 1,053 API
records (677 GB, 376 FC) and 47 complete sample programs. Four FC declarations
have no implementation in the published library; the reference marks them as
such. Argument-passing fragments are not standalone programs or runtime proof.

The API records and bundled examples describe the reviewed public
source trees. `verification/sample_sources.json` records the sample source
hashes. `verification/font_conversion.json` verifies all 92 original glyphs and
the complete GB/NES output arrays, preserving the pixel indices.

The current whole-site check passed 14,157 local links and anchors. The ten
primary READMEs link directly to the corresponding software/library volumes in
the requested language order. The source-comment review covers 429 public source
files across the five software repositories; it does not certify every feature
or every physical device. Test results apply to the recorded inputs and conditions.

Build and runtime records identify the source and executable used.
Source hashes identify files; runtime observations establish tested behavior.

### Final executable checks

All five Windows Release executables were built from the reviewed publication
sources. KITAQGB built without warnings; KITAQFC reported 17
unassigned-field warnings. Each software repository records its binary and
source hashes in `BINARY_BUILD.json`.

- All 47 current samples (29 GB, 18 FC) compiled and ran for 120 emulator frames.
  [Current run records](verification/current/samples.json) include source,
  compiler, ROM and emulator hashes. These are bounded runs with no controller
  input, not complete gameplay or peripheral tests.
- [56 pixel checks](verification/current/visual_checks.json) passed for the
  expected numeric displays and original font glyphs.
- [Seven additional language editions](verification/current/localized_browser_checks.json)
  preserved code and reference IDs on all 63 pages. Search, copy, anchor
  expansion, print restoration and representative desktop/mobile layouts passed.
- KOKURA passed two focused tests: release reporting does not invent completed
  validation, and a neutral synthetic observation condition parses correctly.
- SARAKURA generated English reports for 50 built-in GB rules and 74 built-in FC
  rules, plus an unmapped event on each platform. Strict diagnostic validation,
  encoded HTML evidence names and matching bundled HTML passed.

To run the sample and pixel checks:

```powershell
python -B kitaq-docs/tools/verify_samples.py --runtime
python -B kitaq-docs/tools/check_pixels.py
```

Results go to `verification/current`. HTML regeneration alone does not run
these checks. The browser checks cover the documented controls and selected
layouts; they do not establish that every expanded API entry was visually read.

## Published scope

Source repositories: KITAQGB, KITAQFC, KOKURA core/CLI/APIs, KUROSAKI core/CLI/APIs,
and SARAKURA. KOKURA GUI frontends, KUROSAKI GUI, PLITA, private builders,
commercial ROMs, BIOS images and private analysis data are excluded.
Original font glyphs and synthetic tutorial assets are included with their
applicable license notices. See `LICENSE`, `LICENSE.ja` and
`THIRD_PARTY_NOTICES.md` for licensing scope.


## AI development prompts — September 14, 2026

The prompt supplement provides KITAQGB/KOKURA/SARAKURA and
KITAQFC/KUROSAKI/SARAKURA workflows in all nine published languages.
Each edition includes the full prompt, a complete-text copy button and two
Markdown downloads. Links from the manuals and READMEs open the corresponding
language and target platform.

[Prompt verification](verification/prompt_checks.json) records real clipboard
comparisons for all 18 prompts, shared command preservation, desktop/mobile
layout checks, and FC section navigation across language changes in an isolated
headless Microsoft Edge session. These are documentation checks, not gameplay
or physical-hardware tests. The FC prompt explicitly accounts for the public
CLI's lack of diagnostic-event output from `replay-run`.

Run `python -B tools/check_prompts.py` with Playwright available to repeat the
browser checks. `tools/generate_prompts.py` rebuilds the supplement and links.
The complete site has 90 edition pages, plus two existing diagnostic HTML reports.

日本語：GB用・FC用の開発プロンプトを公開中の9言語に収録しました。
18本すべてで全文コピーとMarkdownの一致、コマンドの保持、PC・スマートフォン幅の
表示、言語切替後もFC用の位置を保つ動作を確認しています。これは説明書の検証であり、
ゲームや実機の動作検証を意味しません。確認結果は上記の記録を参照してください。
