# Native manual maintenance

`python tools/rust_native_update.py` updates all nine compiler, library and verification editions while preserving console C examples, API cards and the original runtime evidence. Published language navigation remains the existing eight-language menu.

The dated `check_*`, `api_*_proofs.py` and source-backed `catalog.py` are historical reference verifiers. Their compiler/library hashes deliberately refer to their recorded C# revisions; use the matching pre-Rust repository revision when revalidating that evidence. Do not replace those hashes with native Rust hashes. New native checks are in the compiler repositories' `tests/`, `tools/platform_smoke.py` (GB), `tools/auxiliary_smoke.py`, and GitHub Actions. The public distribution and current help inventory are updated separately.
