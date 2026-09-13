## Prebuilt Windows CLI
The repository now includes `kurosaki.exe` at its root. Download the repository ZIP and keep the license notices with the executable. This Windows x64 CLI needs no Rust, Python or .NET installation to run. The build steps below are for rebuilding from source. The independent project code is licensed by DAISUKE OBA under MIT; dependency terms are preserved in BINARY_NOTICES.md and licenses/.

## 1. What KUROSAKI does
KUROSAKI is an NES/Famicom/FDS observation emulator that reads KITAQFC information. Its CLI inspects ROMs, executes software, records audio, diagnoses behavior, saves snapshots, replays input, disassembles instructions and decompiles candidate functions. Mapper implementations differ in scope, so inspect the ROM and support information first.

## 2. Build and start
{{CODE:0}}

Short `kurosaki` commands below assume the executable directory is on PATH. Otherwise replace the command name with `& "full executable path"`.

{{CODE:1}}

Use Volume 4's hello ROM to verify text display. `inspect-rom` examines a header; `run` advances CPU and PPU execution. Successful inspection does not guarantee successful execution.

## 3. Check the mapper and board
`mapper-list` lists registered mapper types, `mapper-info` describes one type, and `audit-board` checks board constraints. The mapper number connects the ROM header to assumptions about physical wiring. A name alone does not establish capacity, CHR-RAM or fixed-bank behavior.

{{CODE:2}}

`--allow-unimplemented` permits observation to continue past unsupported elements. A run using it is not proof that those elements are supported.

## 4. Controller input
`run --pad1` and `--pad2` use raw NES button masks: A=1, B=2, SELECT=4, START=8, UP=16, DOWN=32, LEFT=64 and RIGHT=128. Add the values for simultaneous buttons.

{{CODE:3}}

This holds A for 120 frames. Use replay for ordered actions such as title, start and confirm. The CLI `replay-record` example records a baseline run without interactive input; it is different from recording a person operating a GUI.

## 5. Snapshots and replay
{{CODE:4}}

Resumable state uses version 2 snapshots. Keep the ROM SHA-256 matched to its state. `snapshot-resume` continues from a saved point. `snapshot-rebase` explicitly transfers state to a compatible different ROM under a supplied contract. Unconditionally reusing old state after changing code or RAM placement is unsafe; normally reproduce the same actions from startup.

## 6. Traces, diagnostics and profiles
{{CODE:5}}

A trace records what happened over time; diagnostics identify rule-matching observations; a profile shows where execution concentrated. A few frames around an anomaly are usually easier to inspect than a long full trace.

Pass matching build-debug JSON with `--kitaqfc-debug`. An observation without source-line information should not be interpreted as a complete source-line trace.

## 7. Save sound and pictures
{{CODE:6}}

Register changes, generated PCM and correctly sounding audio are separate checks. Record the mapper when testing built-in or expansion sound. A single PNG cannot establish movement or input behavior; retain the preceding and following state and input as well.

## 8. Disassembly and decompilation
{{CODE:7}}

`disasm` emits instruction sequences. `decompile` emits function-boundary candidates, CFGs, references and pseudocode. With switchable banks, a CPU address alone does not identify a physical ROM position. Provide mapper state through `--snapshot` where needed and use execution traces or annotations as supporting evidence. This is not perfect recovery of original source.

## 9. Connect to SARAKURA
{{CODE:8}}

KUROSAKI `--emit-diagnostics` takes a **JSONL file path**, just like KOKURA. Keep CPU traces and diagnostic-event files distinct.

## 10. GUI reference for a later release
**KUROSAKI-GUI and PLITA are not included in the current public source release.** The following describes the development frontend and is retained for reference; its build command cannot be used with this CLI-only publication.

In a source tree containing the frontend, `cargo build -p kurosaki-gui --release` builds it. Open or drop a ROM, use arrow keys for directions, Z/X for A/B and Enter for START. Space toggles run/pause, Ctrl+B toggles capture bundles and Ctrl+K saves a checkpoint. These are the basic bindings checked against the GUI documentation and key definitions.

The default capture location is `%LOCALAPPDATA%\KUROSAKI\captures`. A `.kcb` is a folder bundle containing start state, traces, end state and related information. Check that the expected files exist before sharing it. CLI screenshot checks do not verify GUI DPI behavior or keyboard interaction.

## 11. FDS and save RAM
`fds-inspect` examines disk structure; `export-assets` exports assets. Test FDS separately from NES cartridges because startup, BIOS and disk-access requirements differ. Battery `.sav` files and `.kss.json` snapshots serve different purposes; use a save layout supported by the implementation.

{{CODE:9}}

`battery-export` extracts raw save RAM from a matching ROM and snapshot. `battery-run` loads that RAM and starts from power-on; it does not restore the CPU or PPU's interrupted execution state. Specify output with `--save-out`. These operations require a supported ROM with save RAM and do not apply to every lesson ROM.
