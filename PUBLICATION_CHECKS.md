# Documentation checks

The public reading links offer English and Japanese. The
reference inventory contains 1,055 API entries and 47 complete introductory
sample programs. Individual API documentation and sample verification are
ongoing; `tools/api_descriptions/coverage.json` identifies the reviewed entries.

Active documentation updates and API checks currently target Japanese and English.
The other seven translations are retained as data, without applying new API edits
or listing them in the public language navigation.
`tools/publication_languages.py` controls this selection independently of the
stable translation-table order. New authored messages may use `ja` and `en` keys;
translations for paused editions are not required to publish an active edition.

Captured emulator screens appear beside the corresponding sample explanations,
including the expected shapes, positions and colors where those are checked.
The descriptions state the tested conditions and remaining limitations. Emulator
results do not establish compatibility with every peripheral or physical console.
Four declarations in the FC library lack implementations; their examples show
available alternatives and identify the calls that cannot be linked.

Build logs, execution logs and raw local verification records are not included
in this repository. Source programs and reproduction commands remain available.
Running the check tools creates local records under `verification/`; those files
are ignored by Git. The API authoring renderer requires those fresh records
before it will associate a captured screen with a reviewed sample.

```powershell
python -B tools/check_site.py
python -B tools/check_input_docs.py --suite all --browser
```

The browser check requires Python Playwright and Microsoft Edge. It checks
sample images in their API entries without navigating to a separate results page.
For complete introductory samples, use `tools/verify_samples.py --runtime` and
`tools/check_pixels.py`; API-specific check tools are provided alongside them.

`tools/export_public.py` exports a documentation checkout using an explicit
allowlist. It omits raw verification records and backs up excluded tracked files
outside the destination before removing them. This prevents a new documentation
build from publishing local logs again.
The exporter preserves the translated content of paused language editions;
their navigation alone follows the visible-language setting.

## Published scope

The public software comprises KITAQGB, KITAQFC, KOKURA core/CLI/APIs, KUROSAKI
core/CLI/APIs and SARAKURA. Unpublished GUI frontends, PLITA, private builders,
commercial ROMs, BIOS images and private analysis data are excluded.
See `LICENSE`, `LICENSE.ja` and `THIRD_PARTY_NOTICES.md` for applicable notices.
Original font glyphs and tutorial assets remain included.
