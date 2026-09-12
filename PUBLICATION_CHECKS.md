# Publication checks — September 12–13, 2026

This repository contains seven manuals in Japanese and English, plus a contents
page and verification page for each language. Both editions share 1,029 API
records, 47 complete sample programs, source excerpts and recorded evidence.
The source snapshot is September 12; the English edition was prepared September 13.

## Checks on the curated publication source trees

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

## Website checks

Run `python tools/check_bilingual.py` from this repository to check English and
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
