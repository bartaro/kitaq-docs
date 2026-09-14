# Publication checks

## Source and documentation update — September 14, 2026

The seven manuals, contents page and verification page are provided in English,
Japanese, Korean, Simplified Chinese, Traditional Chinese, Spanish, Brazilian
Portuguese, French and German: 81 manual pages. All editions share 1,053 API
records (677 GB, 376 FC) and 47 complete sample programs. Four FC declarations
have no implementation in the published library; the reference marks them as
such. Argument-passing fragments are not standalone programs or runtime proof.

The API records and bundled examples were refreshed from the reviewed public
source trees. `verification/sample_sources.json` records the synchronized source
hashes. `verification/font_conversion.json` verifies all 92 original glyphs and
the complete GB/NES output arrays, preserving the pixel indices.

The current whole-site check passed 14,157 local links and anchors. The ten
primary READMEs link directly to the corresponding software/library volumes in
the requested language order. The source-comment review covers 429 public source
files across the five software repositories; it does not certify every feature
or every physical device. Later code changes still require focused checks.

Documentation maintenance does not rerun build or emulator tests. The historical
sample records below retain their original scope. Build results must be tied to
the source and executable used; a fresh source hash alone is not runtime proof.

### Final executable checks

All five Windows Release executables were built from the reviewed publication
sources. KITAQGB built without warnings; KITAQFC retained 17 existing
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

To run fresh sample and pixel checks without replacing the historical records:

```powershell
python -B kitaq-docs/tools/verify_samples.py --runtime
python -B kitaq-docs/tools/check_pixels.py
```

Fresh results go to `verification/current`. HTML regeneration alone does not run
these checks. The browser checks cover the documented controls and selected
layouts; they do not establish that every expanded API entry was visually read.

## Historical publication checks — September 12–13, 2026

The initial publication supplied Japanese and English editions with 1,029 API
records and 47 complete sample programs. The following build and test counts
refer to that publication, before the September 14 source corrections.

### Checks on the initial curated publication source trees

- KITAQGB Release build: passed, no warnings.
- KITAQFC Release build: passed, 17 existing unassigned-field warnings.
- All 47 manual ROM examples: compiled successfully with the publication compilers.
- Standalone compiler examples: GB and FC hello and object-pool examples compiled.
- KOKURA workspace tests: 239 reported passed, one ignored. Some external-ROM
  probes return early when input files are absent; these counts are not proof
  that external-ROM suites were exercised.
- KUROSAKI workspace tests: 102 passed. The published DMA smoke test uses a
  synthetic NROM assembled in memory rather than a precompiled external fixture.
- SARAKURA workspace tests: 49 passed.
- Rust results above are debug/test builds, not a new release-binary distribution.

The historical sample runtime records and screenshots in `verification/` retain
their original provenance. Publication compilation and English translation do
not imply that all runtime checks or physical-hardware tests were repeated.
Individual API fragments and declaration-only APIs are explicitly distinguished
from the 47 complete programs.

### Initial website checks

Run `python -B tools/check_bilingual.py` from this repository to check English and
Japanese page coverage, API/sample/command IDs, local links and fragments, and
untranslated English prose outside verbatim source and recorded output.
Results are written to `verification/bilingual_checks.json`.

The English edition was also loaded in an isolated headless Microsoft Edge
session. All nine pages loaded without JavaScript errors. Search filtering,
API anchor expansion, print expansion/restoration and language switching in
both directions passed. Desktop (1440 px) and mobile (390 px) layouts had no
document-level horizontal overflow. The index screenshots were visually
inspected; see `verification/english_browser_checks.json` and the adjacent
`english-*.png` images. This does not claim that every expanded API entry was
visually reviewed.

## Published scope

Source repositories: KITAQGB, KITAQFC, KOKURA core/CLI/APIs, KUROSAKI core/CLI/APIs,
and SARAKURA. KOKURA GUI frontends, KUROSAKI GUI, PLITA, private builders,
commercial ROMs, BIOS images and private analysis data are excluded.
Original font glyphs and synthetic tutorial assets are included with their
applicable license notices. See `LICENSE`, `LICENSE.ja` and
`THIRD_PARTY_NOTICES.md` for licensing scope.

## Compiler layout update — 2026-09-13

KITAQGB and KITAQFC now put build sources inside a same-named subdirectory.
For example, from the parent of the sibling repositories the project is
`kitaqgb/kitaqgb/kitaqgb.csproj`; the ready-to-run compiler remains
`kitaqgb/kitaqgb.exe`. The same convention applies to KITAQFC. Each compiler
repository includes a Release executable and its `.exe.config`, plus the
library and license notices. Windows with .NET Framework 4.8 is required.

Build commands in both editions use the new layout. Historical source-location
labels and fingerprints still describe the September 12 snapshot: a recorded
`kitaqgb/Program.cs` is now `kitaqgb/kitaqgb/Program.cs`, and likewise for KITAQFC.
The relocation did not change those C# source contents.

日本語: コンパイラのビルド用ソースを各リポジトリ内の同名フォルダーへ移しました。
ビルド済みEXEは各リポジトリの直下にあります。日英本文のビルドコマンドは更新済みです。
過去の検証記録にあるC#ソースの場所には、同名フォルダーを一段追加して読み替えてください。
ライブラリと教材の配置は変わりません。
