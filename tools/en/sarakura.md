## 1. SARAKURA's job
SARAKURA combines compiler build information with emulator diagnostic events and presents them in a form useful for repairs and retests. It is neither a ROM-executing emulator nor a program that silently edits your C code.

## 2. Build the tool
{{CODE:0}}

Short `sarakura` commands assume it is on PATH. Otherwise use the path to the built executable. Select `gb analyze` for GB or `fc analyze` for FC.

## 3. Your first analysis
Two inputs are required: `--metadata` is build-time JSON, and `--events` is runtime diagnostic JSONL. JSONL contains one JSON object per line.

{{CODE:1}}

Open the output `report.html` in a browser. Check the target, observed frames, error count and warning count before reading individual diagnostics. `--frames` describes analysis conditions; it does not ask SARAKURA to execute a ROM for that many frames.

## 4. Inspect the inputs first
{{CODE:2}}

Separate unreadable files, mismatched platforms and unsupported event types before investigating game behavior. Passing an ordinary emulator report as an events file does not make it valid diagnostic input.

## 5. Interpret diagnostics
An error deserves priority, a warning may indicate a problem depending on circumstances, and an info item provides context. Severity helps triage but does not fully understand the game's intent. A repeated-PC observation alone may not distinguish a normal title-screen wait loop from a freeze.

Compare the ROM hash, input sequence, scene, screen, sound and source location. Keep conditions equal before and after a repair; otherwise fewer diagnostics might simply mean that a different scene ran.

## 6. Output files
Built-in explanations, diagnostic hints and repair instructions are in English, and HTML declares `lang="en"`. User strings and event IDs are not automatically translated. Default redaction replaces selected project labels and paths; it does not anonymize every address or observation. Inspect reports before publishing analysis of private input.

| File | Purpose |
| --- | --- |
| ai_diagnostics.json | Normalized diagnostics for automated processing |
| diagnostic_summary.json | Counts and summary |
| report.html | Human-readable report |
| repair_prompt.md | Starting context for a repair investigation |
| repair_plan.json / .md | Repair order and targets |
| automation_plan.json / .md | Work plan based on tool capabilities |
| retest_plan.json | Recheck plan |
| repro_bundle.zip | Reproduction information bundle |

Producing a plan is different from executing it. After changing C source or a ROM, run the compiler, emulator and SARAKURA again.

## 7. Catalogs, filtering and coverage
{{CODE:3}}

`catalog` lists diagnostic rules, `pack-plan` groups them by area, and `coverage` examines which corresponding events were observed. A catalog entry does not guarantee that the current emulator emits that event.

{{CODE:4}}

`--diagnostic-rule` selects an event name or catalog ID, `--phase` selects a stage, and `--diagnostic-pack` selects an area. Filtering a diagnostic out of view does not resolve it.

## 8. Compare before and after
{{CODE:5}}

Results are classified as new, resolved, improved, persisting or regressed. Distinguish retained problems from newly introduced ones. Keep input, frame counts and diagnostic filters fixed during comparisons.

## 9. Validation and CI
{{CODE:6}}

Continuous integration automates repeatable checks. `ci-summary` changes the process exit code only when `--enforce` is supplied; otherwise read its JSON verdict. For analyze, `--fail-on error` returns a nonzero exit code when errors occur. The default `never` does not fail the process for diagnostics, so choose a policy explicitly in CI. Selecting `warn` also makes warnings a failure condition.

```powershell
sarakura ci-summary --diagnostics .\out\report --fail-on error --enforce
if ($LASTEXITCODE -ne 0) { throw "The diagnostic failure condition was met" }
```

Successful schema validation checks the data format. Verifying that a game plays as intended also requires input, screen and sound tests.

## 10. Handle reproduction files
`normalize-events` normalizes event records. `inspect-repro` examines a reproduction bundle. Before sharing, check that its information matches the intended ROM and includes the needed input steps. `--allow-project-labels` explicitly retains project-derived labels and identifiers.

## 11. Minimal practice inputs
The manual includes small GB/FC build-metadata and event samples. Open the [GB synthetic report](verification/sarakura-gb-synthetic.html) or [FC synthetic report](verification/sarakura-fc-synthetic.html). `samples/sarakura_demo.ps1` demonstrates analyzing them. These are synthetic inputs for learning the format, not evidence captured from an actual ROM. Use events recorded by KOKURA or KUROSAKI for real-ROM tests.

## 12. One repair and retest cycle
1. Reproduce the problem with the same ROM and input, retaining logs and pictures.
2. Organize candidates with SARAKURA and inspect the relevant source.
3. Make a focused change addressing the cause.
4. Rebuild and rerun the same actions.
5. Compare baseline-delta with pictures, audio and game behavior.

Keep this loop small so that each change and its effect remain understandable.
