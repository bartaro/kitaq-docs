## Prebuilt Windows CLI
The repository now includes `kokura-cli.exe` at its root. Download the repository ZIP and keep the license notices with the executable. This Windows x64 CLI needs no Rust, Python or .NET installation to run. The build steps below are for rebuilding from source. The independent project code is licensed by DAISUKE OBA under MIT; dependency terms are preserved in BINARY_NOTICES.md and licenses/.

## 1. What KOKURA does
KOKURA emulates GB/CGB software and records observations of pictures, audio, CPU execution, memory, banks, input and diagnostic events. This manual uses the current executable name `kokura-cli.exe`; do not assume that historical references to `kokuradbg` name the executable in this release.

## 2. Build and run your first ROM
{{CODE:0}}

Install Rust and Cargo. Build the named crate when you need only the CLI. Use the hello ROM from Volume 1. The default frame count is one; set `--run-frames` to reach the scene you want. This counts emulated frames, not seconds of waiting.

## 3. Choose DMG or CGB
`--hardware auto` is the default; `dmg` and `cgb` are explicit alternatives. Test dual-mode ROMs in both modes. A CGB-only ROM refusing to start as DMG is not, by itself, an emulator failure.

{{CODE:1}}

## 4. Provide input
`--input` holds a simultaneous button combination; `--input-seq` supplies a sequence over time. Button names are `A,B,START,SELECT,UP,DOWN,LEFT,RIGHT`; use `NONE` for released intervals. Quote sequences containing semicolons in PowerShell.

{{CODE:2}}

Include a released interval when testing press edges. Holding A for 120 frames is different from pressing A 120 times. With the input-counter lesson, the sequence above should increment the count once.

## 5. Pictures, video and audio
`--png` saves the final screen. `--screenshot` with `--screenshot-frames` captures selected frames. `--record-video` records video and `--record-wav` records audio. A silent WAV from a hello program that does not use the APU is expected.

{{CODE:3}}

Ranges use `start:end`. Keep the report to distinguish accumulated frame numbers in a loaded state from positions in the current run. Check audible output, pitch, interruptions and clipping separately. Emulator recording does not establish sample-for-sample equality with physical hardware.

## 6. Save and resume state
{{CODE:4}}

Normally use the same ROM and emulator version. Emulator state is different from a game's own save data. CLI KQS files and the C API's JSON state are different formats; renaming their extensions does not make them interchangeable.

## 7. Observe symbols and memory
Sidecars named `.map`, `.source_map.txt`, `.dbg2.json` and `.build_report.json` can be detected beside the ROM. Keep a ROM with its matching sidecars: files from another build can produce misleading observations.

{{CODE:5}}

`wram` is the observation-window label, 0xC000 is its starting address and 0x40 its length. Small windows make changed variables easier to identify. `--watch-baseline-mode` selects comparison against initial values, the previous frame or a named baseline.

## 8. Stop conditions, replay and reverse analysis
`--breakpoint`, `--watchpoint`, `--run-until` and `--snapshot-at` stop or save on conditions. Their argument mini-languages differ; use the reference and captured help below.

{{CODE:6}}

Find the first divergence, then observe a narrower interval around it. `--decompile-out` produces pseudocode and control-flow information; `--disassemble-out` displays CPU instructions. Decompilation does not perfectly restore original C code or variable names.

## 9. Send diagnostics to SARAKURA
{{CODE:7}}

KOKURA `--emit-diagnostics` takes a **JSONL filename**, such as `out/gb_events.jsonl`. An ordinary run-report JSON file or a CPU-trace JSONL file is not the same as diagnostic-event input.

## 10. Communication jobs
`pair` models two machines. `four_player_adapter` is a logical host-selected-peer arrangement. `dmg07` models the physical DMG-07 protocol. Supply job JSON with `--link-job` or configure sessions through `--link-topology` and `--link-session`.

{{CODE:8}}

Each ROM must implement communication. Running two ordinary hello programs does not test the link library. Record each session's ROM, slot, input and state, and identify which physical-device behavior remains untested.

## 11. GUI and external applications
The GUI frontends and PLITA are deferred from this public release. Their behavior is separate from CLI screenshots: GUI key bindings and available features depend on the frontend implementation. The published C ABI is in `kokura-capi`; Python access is available through the supplied bridge and Python crate. Establish a minimal CLI reproduction before distinguishing a frontend issue from a ROM issue.

## 12. Read reports in order
Check the executed frames and stop reason first, then the screen, input result, sound, errors and warnings, and profile. A long observation of a title screen with no input can naturally produce static-screen or repeated-PC warnings. Compare warnings with the intended scene rather than mechanically treating every warning as a malfunction.
