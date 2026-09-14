# Game development with KITAQFC, KUROSAKI and SARAKURA

Fill in the requirements and give this entire document to the AI assistant. Commands assume sibling repositories named `kitaqgb`, `kitaqfc`, `kokura`, `kurosaki`, `sarakura` and `kitaq-docs`, with your `game-gb` or `game-fc` project beside them. Run commands from their parent directory; adapt paths to the actual environment.

## Requirements

- Game title: <fill in>
- Genre and core gameplay: <fill in>
- Controls, success and failure conditions: <fill in>
- Required screens, stages, enemies and items: <fill in>
- Visual style, music and sound effects: <fill in; identify any supplied assets>
- Saving, communication, peripherals and other requirements: <fill in, or none>
- Project directory: <fill in>
- Redistribution requirements: <for example, original code and assets suitable for MIT publication>

- Target: <NES/Famicom cartridge or FDS>
- Mapper, ROM size and mirroring: <specify, or select from the requirements>
- Video standard and performance: <for example, NTSC and 60 gameplay updates per second>

## Task

Implement the game with KITAQFC and its libraries. Use KUROSAKI for execution and debugging, and SARAKURA to organize diagnostics and compare results before and after a fix.

Repeat this cycle until the acceptance criteria are met: make the specification concrete → implement a small change → build → apply inputs and observe → investigate the cause → fix → retest under the same conditions. A plan, a code listing or a successful compilation is not completion.

### Establish the environment and acceptance criteria

1. Read workspace instructions, tool READMEs, HTML manuals, and the headers and implementations of the libraries you will use. Record executable paths and versions or SHA-256 hashes. Verify commands against actual `--help` output and APIs against source.
2. Define measurable acceptance criteria for inputs, images, audio, progression and update frequency. Examples: pressing and releasing START begins the game; a collision removes one life; pausing silences the intended audio and resuming restores playback.
3. Ask only about material ambiguities. Make ordinary reversible implementation decisions autonomously. Do not weaken requirements or acceptance criteria.
4. First run a small supplied sample through the compiler, emulator and SARAKURA. This checks the tool connection, not completion of the requested game.

### Implement a small playable slice

- Start with NROM for a small game; choose MMC3 or another mapper when banking or size requires it. Verify required board features using `inspect-rom`, `mapper-info`, `audit-board` and the implementation, rather than relying on the mapper name alone.
- Plan PRG/CHR size, CHR-ROM or CHR-RAM, mirroring, fixed banks, interrupt vectors and save RAM. Check headers against actual placement after optimizations or banking changes. `--nes-local-ram` uses internal CPU RAM in `$0000–$07FF`; avoid overlaps with zero page, stack, OAM buffers and runtime/library storage.
- Use the KITAQFC C dialect, FC libraries and `void main(void)`. Do not assume GB APIs are compatible. Check implementation providers and include the required `.c` files; some header entries are declarations only.
- Account for PPU registers, NMI, OAM DMA, per-scanline sprite limits, scrolling, mirroring, attribute tables and APU/DMC behavior. Transfer-queue free space is not PPU VRAM capacity; budget the work done per NMI.
- Convert the supplied original `ascii.c` font to FC CHR for letters, digits and symbols. Verify CHR, palettes, nametables and attributes. For FDS, separately verify disk access, saving and BIOS requirements; do not assume cartridge boot conditions.

- First connect boot, title, a controllable player, success or failure, and restart. Then expand the game.
- Keep editable graphics, music and sound-effect sources and their generation steps. Verify that the build actually consumes their exports.
- Write source comments in English and progress reports in English. Keep SARAKURA’s standard reports in English.

### Connect each build to its execution

Use a separate output directory for each iteration, such as `out/iter-001`. Record commands, exit codes, and hashes of source, assets, tools, ROM and metadata. Never run an older ROM after a failed build. Maps, source maps and debug information must come from the same build as the ROM.

The following is an NROM check with no input. Supply `main.c`, required library implementation units and the CHR file; select the appropriate mapper. Do not pass compiler build metadata to KUROSAKI’s `--kitaqfc-debug` without first checking its required format.

```powershell
$iteration = '.\game-fc\out\iter-001'
New-Item -ItemType Directory -Force $iteration | Out-Null

# Include all additional implementation units required by the game.
& '.\kitaqfc\kitaqfc.exe' '.\game-fc\src\main.c' `
  -I '.\kitaqfc\lib' -o "$iteration\game.nes" `
  --mapper=nrom '--nes-chr=.\game-fc\assets\game.chr' --no-disasm `
  "--kurosaki-metadata=$iteration\build.json"
if ($LASTEXITCODE -ne 0) { throw 'Build failed; inspect the build log.' }

& '.\kurosaki\kurosaki.exe' run "$iteration\game.nes" `
  --frames 300 --pad1 0 --png "$iteration\frame.png" `
  --json "$iteration\run.json" --emit-diagnostics "$iteration\events.jsonl"
if ($LASTEXITCODE -ne 0) { throw 'Emulator run failed; inspect the run log.' }

& '.\sarakura\sarakura.exe' fc analyze `
  --metadata "$iteration\build.json" --events "$iteration\events.jsonl" `
  --frames 300 --out "$iteration\analysis" --fail-on error
if ($LASTEXITCODE -ne 0) { throw 'Inspect the analysis report and fix the cause.' }
```


A 300-frame run with no input is only an initial check. Add ordered gameplay scenarios before claiming that the game works.

### Reproduce ordered input

- `--pad1` and `--pad2` use raw NES bitmasks: A=1, B=2, SELECT=4, START=8, UP=16, DOWN=32, LEFT=64, RIGHT=128. Do not confuse these with library `BTN_*` values.
- `run --pad1` applies fixed input. For sequences of actions, create a replay that distinguishes presses, holds and releases. Inspect the `Replay` and `ReplayFrame` definitions. The public CLI’s `replay-record` records neutral input, not a person’s interactive play.
- Check ROM SHA-256, replay identity and frame range yourself. `replay-run --verify` compares an expected final hash only when one is provided; it does not comprehensively validate gameplay or ROM identity. Never overwrite expected results with observed results merely to make a test pass.

```powershell
& '.\kurosaki\kurosaki.exe' replay-run `
  '.\game-fc\out\iter-001\game.nes' '.\game-fc\tests\start-and-play.replay.json' `
  --frames 900 --json '.\game-fc\out\iter-001\play.json' `
  --png '.\game-fc\out\iter-001\play.png' `
  --wav '.\game-fc\out\iter-001\play.wav'
```


Prepare the replay for the ROM being tested. The public CLI’s `replay-run` has no `--emit-diagnostics` option. Do not invent that option or pass CPU trace data as diagnostic events. To analyze ordered-input scenarios with SARAKURA, create a project-local test harness using public `kurosaki-core` APIs: `RunOptions.replay_frames` and `diagnostic_events_from_trace_and_report`. Run the same ROM, replay and frame conditions; generate diagnostic JSONL from that execution’s trace and diagnostic report. Check trace configuration and retained ranges, and compare the harness’s images and observations with CLI replay results. Do not present no-input diagnostics as evidence for a gameplay scenario. If the required environment is unavailable, report this verification as incomplete.

### Check images, audio, state and performance

- Save input scenarios with distinct presses, holds and releases. Exercise every specified path: boot, start, movement, actions, collisions, scrolling, stage changes, game over, restart, pause and saving or communication where applicable.
- Preserve PNGs at relevant frames, input data, execution reports, diagnostic JSONL, WAVs and any necessary state or memory observations. Check the reached frame count and stop reason. Actually open the images; one screenshot cannot establish motion or input response. Compare counters, positions and state changes with expected values. Check screen edges, tile/attribute boundaries and crowded sprite scenes.
- Check music, effects, simultaneous playback, dropouts, pause and resume. A generated WAV alone does not establish correct sound. If listening is unavailable, distinguish the waveform/numerical checks performed from unverified audible qualities.
- Measure heavy scenes, target CPU/update workload and transfers; on FC, include NMI work. Host emulator throughput is not game update frequency or proof of hardware speed. Continuing with `--allow-unimplemented`, where available, does not demonstrate support for the missing feature.

### Analyze, repair and retest

- Feed SARAKURA the build metadata for the tested ROM and diagnostic JSONL from the tested execution. A CPU trace or ordinary run report is not a substitute. `--frames` specifies analysis conditions; SARAKURA does not execute the ROM or automatically edit the source.
- Read `report.html`, `ai_diagnostics.json`, `repair_prompt.md` and `retest_plan.json`. Compare diagnoses with reproduction steps, images, audio and source. Distinguish inferred source locations or causes from verified facts, and normal waiting loops from hangs. Assess warnings individually and record unsupported events or analysis limits. Do not hide warnings with filters or shorten tests to obtain a passing result.
- Reduce failures to minimal reproductions, fix their causes and rebuild. If the compiler or emulator is responsible, isolate its defect from game code and add regression verification for the tool fix.
- Retest with matching input, random seed, hardware/video mode, mapper, observed frames and diagnostic settings. Use new metadata for each new ROM; do not blindly reuse save states after code or RAM layout changes.

```powershell
& '.\sarakura\sarakura.exe' baseline-delta `
  --baseline '.\game-fc\out\iter-001\analysis' `
  --current '.\game-fc\out\iter-002\analysis' `
  --out '.\game-fc\out\delta.json' --markdown '.\game-fc\out\delta.md' `
  --fail-on-new error --fail-on-regression error --enforce
```


Use diagnostic differences alongside gameplay, graphics and audio acceptance checks. If the same failure repeats, revisit the evidence and hypothesis instead of continuing arbitrary changes.

### Completion and deliverables

Rerun all required scenarios against the final ROM built from the delivered source and settings. Invincibility, automatic test input or another mapper alone does not verify normal play in the final build. Provide a requirement-to-test table, reasons for remaining warnings and explicit unverified or unsupported items. State “not tested on physical hardware” when applicable.

Deliver source, tool/library identities, editable assets, reproducible build and test scripts, the ROM, final verification evidence, and a README covering setup, controls and known limits. Include replay data and a test harness where needed. Publish or send files externally only within explicitly authorized scope. Delete unnecessary intermediate builds and temporary traces after verification, preserving source, assets, final deliverables and needed regression evidence.

If environment or permission constraints prevent a required check, report the exact reproduction steps and required action. Do not mark the work complete.
