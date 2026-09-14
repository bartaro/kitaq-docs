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
