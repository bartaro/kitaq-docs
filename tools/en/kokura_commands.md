## 13. Command recipes and exact argument syntax

Run these PowerShell commands from the directory containing the sibling repositories. Create the output directory first with `New-Item -ItemType Directory -Force out`. Replace `out/game.gb` with your own ROM. KOKURA uses options after the ROM path; it does not use KUROSAKI's `run` subcommand. `--help` lists the options in the installed executable.

### 13.1 Choose an operation and a frame budget

| Argument | Purpose and behavior |
| --- | --- |
| `ROM` | ROM file for an ordinary run. A job or matrix can supply its own ROM instead. |
| `--hardware auto`, `dmg`, `cgb` | Hardware selection. The default is `auto`; explicitly test both modes for a dual-mode game. |
| `--run-frames 120` | Maximum frame budget for direct execution, default 1. Stop conditions can end execution sooner. Input sequences also have their own durations. |
| `--job out/test.json` | Run a JSON job. Put its frame budget in `run.frames`; its ROM, state, input and capture settings come from the job. Relative paths inside the job are relative to the job file. |
| `--dump-report out/run.json` | Save the resulting JSON report. Without an output destination, ordinary execution prints the report to standard output. |
| `--regression-matrix out/matrix.json` | Execute jobs with expected observations. Inspect the case results in the JSON: successful execution of the matrix command does not mean every case passed. |

Choose one operation per invocation. Dispatch precedence is decompilation, disassembly, regression matrix, link job, inline link sessions, then an ordinary run. Combining modes does not make them run in sequence.

```powershell
.\kokura\kokura-cli.exe out/game.gb --hardware dmg --run-frames 120 --png out/game.png --dump-report out/run.json
```

This advances up to 120 emulated frames and saves a final screen and report. Check the report's actual frame count and stop reason before interpreting the picture.

### 13.2 Hold buttons or supply a timed sequence

| Option | Syntax and use |
| --- | --- |
| `--input "A,RIGHT"` | Hold both buttons during a direct run. Names are case-insensitive. `NONE` releases all buttons. |
| `--input-seq "NONE:30;A:1;NONE:89"` | Semicolon-separated `BUTTONS:FRAMES` intervals, in order. This sequence releases for 30 frames, presses A for one, then releases for 89. |
| `--input-script "NONE:30;A:1;NONE:89"` | Accepts the same sequence text; this is not a filename. If both sequence options are supplied, `--input-script` wins. |

Button names are `RIGHT,LEFT,UP,DOWN,A,B,SELECT,START`. Hexadecimal masks use RIGHT=0x01, LEFT=0x02, UP=0x04, DOWN=0x08, A=0x10, B=0x20, SELECT=0x40, START=0x80. These are KOKURA's input masks; do not reuse NES pad masks. Quote the full sequence in PowerShell. Supply released intervals when testing a new press, and make the sequence cover the intended observation interval.

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 120 --input-seq "NONE:30;A:1;NONE:89" --png out/after-a.png --dump-report out/after-a.json
```

For the button-counter sample, this should increase the counter once. A static picture alone cannot establish whether a held button repeats correctly; compare a held interval with separate presses.

### 13.3 Capture pictures, motion and sound

| Option | Syntax and use |
| --- | --- |
| `--png out/final.png` | Save the final screen; takes precedence over `--screenshot` when both are supplied. |
| `--screenshot out/frame.png` | Alternative screen destination. PNG and BMP are supported; an extensionless path receives `.png`. |
| `--screenshot-frames 30:32` | Save each selected frame, with a frame number in the output filename. Requires a screen destination. |
| `--record-wav out/audio.wav` | Record audio as WAV. Use a ROM and interval that actually play sound. |
| `--record-wav-frames 1:180` | Select the inclusive recording interval; these are frame numbers, not sample counts. |
| `--record-video out/motion.gif` | Record motion as GIF or Y4M. An extensionless path receives `.gif`; MP4 is not an accepted format. |
| `--record-video-frames 30:120` | Select the inclusive video interval. |
| `--audio-buffer-frames 8192` | Set audio buffer capacity in stereo sample frames, not emulated video frames or individual left/right samples. |

Capture ranges are decimal and one-based: `30` selects one frame and `30:32` includes frames 30, 31 and 32. Zero and reversed ranges are rejected. Capture indices refer to the current run, so retain the report when resuming an older state. Create parent directories before capture.

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 180 --record-wav out/audio.wav --record-wav-frames 1:180 --record-video out/motion.gif --record-video-frames 30:120
```

Use several frames to assess scrolling or animation. Use the WAV to assess sound; a visible completion number does not prove that the intended channel played.

### 13.4 Save and resume machine state

| Option | Purpose and precedence |
| --- | --- |
| `--save-state out/checkpoint.kqs` | Save the machine state at the end of the run. |
| `--snapshot out/checkpoint.kqs` | Same output role; takes precedence over `--save-state`. |
| `--load-state out/checkpoint.kqs` | Load a KQS state before execution. |
| `--resume-state out/checkpoint.kqs` | Takes precedence over `--load-state`, and can override the input state of a job. |
| `--snapshot-at "frame=60&&frame_end=>out/frame60.kqs"` | Save when an observation condition matches. Repeat for multiple requests. With no `=>path`, a numbered filename is derived from the ROM name in the current directory. |

Use a state matching the ROM and emulator version. KQS is machine state, not cartridge save RAM and not the C API's JSON serialization.

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 120 --save-state out/title.kqs
.\kokura\kokura-cli.exe out/game.gb --resume-state out/title.kqs --input START --run-frames 30 --png out/started.png --snapshot out/started.kqs
```

### 13.5 Inspect named memory windows

| Option | Syntax and use |
| --- | --- |
| `--symbols out/game.map` | Load symbols from the matching compiler output. |
| `--source-map out/game.source_map.txt` | Associate execution with source locations. |
| `--toolchain-metadata out/game.dbg2.json` | Load structured toolchain metadata. Matching sidecars may also be detected beside the ROM. |
| `--watch-window "player:0xC700:16"` | Observe 16 bytes beginning at 0xC700 under the label player. Repeat for separate windows; this observes memory and does not itself stop execution. |
| `--watch-baseline-mode initial` | Compare to initial values. `previous-frame` compares successive frames; `named` selects an explicitly captured baseline. |
| `--watch-baseline-tag ready` | Select the baseline name when using named comparison. |
| `--capture-watch-baseline "ready=>frame=30&&frame_end"` | Capture a named baseline when a condition matches. Repeat to capture other baselines. |
| `--watch-fields preview,diff` | Choose watch field groups: `hash`, `activity`, `preview`, `baseline`, `diff`, `insights`, or `all`. Preview bytes are only a bounded preview, not an unlimited memory dump. |
| `--report-sections cpu,watched_memory` | Keep the named report sections. `meta` and `schema_version` remain present. Unknown names do not create new sections. |
| `--report-minimal cpu,watched_memory` | Another section-list input, taking precedence over `--report-sections`. It requires a comma-separated value; it is not a Boolean switch. |

Addresses and sizes accept decimal or `0x` hexadecimal. Use the current build's symbols to find a variable; 0xC700 below is only an example address, not a standard player location.

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 60 --watch-window "player:0xC700:16" --watch-fields preview,diff --report-sections cpu,watched_memory --dump-report out/watch.json
```

### 13.6 Stop on execution or hardware events

| Option | Syntax and purpose |
| --- | --- |
| `--breakpoint "pc:0x0150"` | Stop at a CPU address. `symbol:main` uses symbols; append `@bank:2` to restrict the bank. |
| `--watchpoint "player@0xC700+4"` | Stop on memory writes in a four-byte range. The optional prefix names the watchpoint; omitting `+size` watches one byte. |
| `--stop-on-mmio "scroll@0xFF43"` | Stop on a write to the specified MMIO register, here SCX. |
| `--stop-on-irq "vblank:serviced"` | Select an interrupt source and phase: `requested`, `serviced`, `blocked` or `any`. A phase alone matches any source. |
| `--stop-on-dma oam_start` | Select a DMA event. Accepted names: `oam_start`, `oam_complete`, `hdma_start`, `hdma_block`, `hdma_complete`, `hdma_cancel`, `gdma_stall`, `hdma_deferred`, `hdma_ignored`. |
| `--run-until "frame=60&&frame_end"` | Stop when all terms in an observation condition match. Repeat the option for additional requests. |

Breakpoint markers `pc:`, `symbol:` and `@bank:` are case-sensitive. Memory addresses and banks use decimal or `0x` hexadecimal. Keep a frame budget even when requesting a stop that might never occur.

Observation conditions use `&&` for AND, not C expressions. Supported terms are `frame=`, `ly=`, `pc=`, `bank=`, `bank_pc=bank:pc`, `symbol=`, `source=`, `event=`, `ppu_mode=` (or `mode=`), and `basis=`. Frame and LY values are decimal. Symbol, source and event terms match text. Basis values include `frame_start`, `frame_end`, `step`, `event`, `trace`, `snapshot`, `stop`; bare `frame_start`, `frame_end`, `stop` and `vblank` are also accepted. Comparisons such as `hp<10` are not part of this grammar.

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 120 --breakpoint "pc:0x0150" --snapshot out/entry.kqs --dump-report out/entry.json
.\kokura\kokura-cli.exe out/game.gb --run-frames 120 --stop-on-mmio "scroll@0xFF43" --dump-report out/scroll-write.json
```

Use the first command to examine the entry point, and the second to identify the code that changes horizontal scrolling. Check whether the requested stop actually occurred.

### 13.7 Record observation points and compare runs

| Option | Purpose |
| --- | --- |
| `--trace-point "frame=30&&frame_end"` | Record an observation when the condition matches. Repeat for several points. |
| `--timeline-out out/timeline.jsonl` | Save the observation timeline. |
| `--trace-jsonl out/timeline.jsonl` | Alternative timeline destination, taking precedence over `--timeline-out`. It is not a request for an exhaustive instruction trace. |
| `--timeline-format jsonl` | Select `jsonl` (default) or `csv`; choose the corresponding filename extension yourself. |
| `--replay-interval 1` | Enable replay checkpoints and choose the interval in frames. |
| `--replay-max-checkpoints 120` | Limit retained checkpoints; the replay default is 16, with an interval of 1. |
| `--rewind-on-stop-frames 10` | Request rewind after a stop, using retained replay history. |
| `--stop-on-divergence` | Enable the replay controller's divergence stop behavior. |
| `--dump-replay-tape out/baseline.json` | Export recorded replay data. Enable replay recording to produce it. |
| `--compare-replay-tape out/baseline.json` | Compare against an exported replay tape. Use the same ROM, inputs and initial state for a deterministic comparison. |
| `--compare-replay-watch-only` | Restrict comparison to watched-memory observations rather than treating it as a complete machine comparison. |
| `--snapshot-on-replay-mismatch out/mismatch` | Supply a prefix for mismatch investigation artifacts when comparison finds a mismatch. |

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 60 --replay-interval 1 --replay-max-checkpoints 60 --dump-replay-tape out/baseline.json --dump-report out/baseline-report.json
.\kokura\kokura-cli.exe out/game.gb --run-frames 60 --replay-interval 1 --replay-max-checkpoints 60 --compare-replay-tape out/baseline.json --dump-report out/compare.json
```

Check the comparison result and the first mismatch in the report. Merely producing both files is not a passing comparison.

### 13.8 Diagnostics and a reproducible investigation

| Option | Actual behavior |
| --- | --- |
| `--emit-diagnostics out/events.jsonl` | Export diagnostic events for SARAKURA. |
| `--diagnostics-jsonl out/events.jsonl` | Alternative diagnostic destination for direct runs; `--emit-diagnostics` takes precedence. |
| `--repro-bundle out/repro.zip` | Package a report, diagnostic events and a manifest. ROM and metadata are referenced by path, not embedded; screenshots, states and traces are not automatically included. |
| `--break-on-diagnostic all` | Match diagnostics in the final report for artifact capture. This does **not** stop the CPU at the first offending instruction. With any nonempty filter, any final diagnostic can enter the capture path. |
| `--png-on-diagnostic out/diagnostic-images` | Destination directory for the final diagnostic screen, used with diagnostic capture. The filename is `diagnostic_000001.png`. |
| `--snapshot-on-diagnostic out/diagnostic-states` | Destination directory for `diagnostic_000001.kqs`. These captures reflect the current final state, not each event's original instant. |
| `--diagnostic-pack NAME` | Accepted argument; the execution path does not apply a diagnostic pack. |
| `--diagnostic-rule RULE` | Repeatable accepted argument; the execution path does not apply these rule selections. |
| `--diagnostic-summary-limit N` | Accepted argument; the execution path does not apply this summary limit. |

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 180 --emit-diagnostics out/events.jsonl --dump-report out/run.json --break-on-diagnostic all --png-on-diagnostic out/diagnostic-images --snapshot-on-diagnostic out/diagnostic-states --repro-bundle out/repro.zip
```

To stop at a particular instruction or write, use the debugger options in 13.6. Read diagnostics in context: a deliberately idle title screen can produce observations that are not game defects.

### 13.9 Disassemble instructions or inspect pseudocode

| Option | Syntax and purpose |
| --- | --- |
| `--disassemble-out out/code.txt` | Decode ROM instructions without running the ordinary emulation job. |
| `--disassemble-range "0:0100-0150"` | Select `BANK:START-END`; repeat for more ranges. **All three numbers are hexadecimal**, even without `0x`. |
| `--disassemble-format text` | `text` (default), `markdown` or `json`. |
| `--decompile-out out/functions.json` | Generate pseudocode and control-flow information. |
| `--decompile-format json` | `json` (default), `markdown` or `text`. |
| `--decompile-function main` | Select a function; repeat for more selections. Matching symbols improve identification. |
| `--decompile-all` | Include all named functions known to the decompiler. |
| `--decompile-annotations out/annotations.json` | Read annotations in the decompiler's JSON format. |
| `--decompile-trace out/trace.json` | Read decompiler trace metadata; an arbitrary JSONL diagnostic log is not a substitute. |

```powershell
.\kokura\kokura-cli.exe out/game.gb --disassemble-range "0:0100-0150" --disassemble-out out/entry.txt --disassemble-format text
.\kokura\kokura-cli.exe out/game.gb --symbols out/game.map --decompile-function main --decompile-out out/main.md --decompile-format markdown
```

Disassembly is useful for checking generated instructions; pseudocode helps navigate control flow. Neither recovers the exact original C program. Keep symbols and metadata from the same ROM build.

### 13.10 Run multiple linked machines

| Option | Syntax and purpose |
| --- | --- |
| `--link-job out/pair.json` | Read topology and sessions from a JSON link job; relative paths are resolved from the job directory. |
| `--link-topology pair` | Select `pair`, `four_player_adapter` or `dmg07` for inline sessions. |
| `--link-session SPEC` | Add one session. At least two sessions are required. Quote the whole pipe-separated string in PowerShell. |
| `--link-initial-peer-slot 1` | Choose the initial peer where the topology uses peer selection. |

Session fields include `name`, `slot`, `rom`, `symbols`, `source_map`, `toolchain_metadata`, `load_state`, `save_state`, `input`, `input_sequence`, `audio_buffer_frames` and `watch_window`. `rom` is required. A watch field can contain comma-separated windows such as `a:0xC700:4,b:0xC710:4`. Use programs that actually exchange serial data; two running screens alone do not prove communication.
