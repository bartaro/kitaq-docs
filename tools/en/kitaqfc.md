## 1. KITAQFC and the GB compiler
KITAQFC uses the KITAQGB front end to generate code for the NES/Famicom's 6502-family CPU. It does not convert a GB ROM into an NES ROM. Write software for the target's display, sound, memory and mapper.

KITAQFC supports structure copies, ordinary function calls, for, while and do-while. A do-while loop runs its body at least once before testing the condition. continue proceeds to that final test; break leaves the loop. A switch selects a case constant in 0..255 or the default body when no case matches. Its selector is evaluated once. break exits the innermost loop or switch; continue inside a switch advances the enclosing loop.

## 2. Requirements and build
{{CODE:0}}

Install the .NET Framework 4.8 Developer Pack and Visual Studio Build Tools, and use Developer PowerShell. Subsequent commands use the executable copied into the `kitaqfc` checkout. If you use another build location, adjust the path. CHR graphics and C source are distinct inputs. The manual's `font.chr` is an 8 KiB conversion of the author's `ascii.c`.

## 3. Your first program
{{CODE:1}}

{{CODE:2}}

The sample displays HELLO WORLD and 042. Its `m_wait` helper commits the VRAM queue, waits for NMI and restores scrolling. Transfers through PPUADDR affect internal scroll state; omitting restoration can shift the text toward an edge. Learn the sequence: display off, prepare assets, display on, synchronize with NMI.

## 4. Language introduction
The GB volume's statements and expressions provide a common starting point. FC accepts `unsigned char` and `unsigned short`; `core.h` defines `u8`, `u16`, `s8` and `s16`. `fc.h` is an umbrella header. No-argument functions can use `void main(void)` here.

{{CODE:3}}

Use integers within their 8-bit or 16-bit ranges. Array indexes start at zero. `fc_aggregate.c` demonstrates functions, pointers and structures; `fc_arithmetic.c` demonstrates arithmetic; `fc_control.c` demonstrates loops. Do not include CGB registers or GB-only intrinsics in an FC program.

<!-- common-language-kitaqfc:start -->
### Expression results and evaluation
The comparison operators `==`, `!=`, `<`, `<=`, `>`, `>=` and logical operators `!`, `&&`, `||` return 0 for false and 1 for true. You can store the result in a `u16`, pass or return it, or use it in arithmetic. For example, `score = 500 + (lives != 0);` produces 501 when a life remains and 500 otherwise.

`&&` skips its right operand when the left operand is zero. `||` skips its right operand when the left operand is nonzero. In `pointer != 0 && pointer->active != 0`, a null pointer prevents the member access. Both bytes of a 16-bit value participate in the truth test, so 256 is true. Bitwise `&` and `|` do not short-circuit.

`++value` returns the updated value; `value++` returns the original value. These operators also accept array elements, dereferenced pointers and structure members. `buffer[index()]++` calls `index()` once. For a `u16 *p`, `p++` advances two bytes to the next element, while `(*p)++` increments the pointed-to value.

`sizeof(array)` gives the entire array's size in bytes; `sizeof(pointer)` is 2. For `u16 values[9];`, `sizeof(values)` is 18. This includes ROM arrays, local arrays and array members. `sizeof(function())` inspects the return type without calling the function.

A function declaration and definition must agree on parameter types and order. Their parameter names may differ; the body uses the definition's names. For example, `u8 next(u8 input);` can be defined as `u8 next(u8 value) { return (u8)(value + 1); }`. Parameters and local variables hide globals with the same name.

Selecting arrays or strings with `?:` produces a pointer to the selected element type. You can pass it directly, as in `show(ready ? "READY" : "WAIT");`. For `u16` arrays `a` and `b`, `(ready ? a : b) + 1` advances two bytes to the second element of the selected array. This does not copy the array.

`condition ? yes : no` evaluates its condition and then only the selected arm. The condition and arms may contain shifts with variable counts. For example, `on = (pattern & (0x80 >> bit)) != 0 ? 4 : 2;` selects four or two for the chosen bit. Function calls in a right operand skipped by `&&` or `||` are also skipped. A `continue` in a `for` loop runs the update expression once before reevaluating the condition; in `while` and `do ... while`, it advances to the condition.

<!-- common-language-kitaqfc:end -->
## 5. Loops and state dispatch
{{CODE:4}}

These fragments show a loop that updates at least once and a branch that selects a handler for the current state. Define update, condition, state and the state handlers in your program. See fc_control.c for a complete loop example and the library's frame and scene sample for a complete scene-management ROM.

Register scene, entity and system callbacks with the argument and return types required by their declarations. The libraries invoke registered handlers from the corresponding update, drawing or frame-wait operations. Follow each API's ROM-bank and mapping requirements. Do not assume desktop-style support for recursion or variadic functions.

## 6. Memory and the PPU
NES internal CPU RAM occupies 0x0000-0x07FF. Its mirrors above 0x0800 are not additional RAM. The 6502 stack occupies page 1, while OAM shadows and queues reserve other regions. `--nes-local-ram=START:LENGTH` and `--nes-temp-ram=START:LENGTH` are advanced settings that require map inspection.

PPU addresses form a separate address space. CHR supplies patterns, nametables position tiles, attribute tables choose palette groups, and palettes contain color codes. Background attributes normally apply to 16-by-16-pixel regions, so they do not behave like GB tile attributes.

## 7. NMI and the VRAM queue
NMI is the interrupt associated with the display frame boundary. Large direct PPU writes during rendering can corrupt the screen. Initialize directly while rendering is off; use `__vramq_put`, `__vramq_copy`, `__vramq_fill` and commit for ordinary updates.

{{CODE:5}}

Check queue capacity and source lifetimes. The default NMI handles the queue. A custom `__nes_nmi` must retain the required queue execution, OAM work and register preservation.

## 8. Mappers and ROM layout
| Selection | Typical starting use |
| --- | --- |
| nrom | Small fixed-ROM lessons |
| uxrom / cnrom / axrom | Simple PRG or CHR switching |
| mmc1 / mmc3 / mmc5 | Larger programs and mapper-specific features |
| vrc6 / vrc7 / fme7 | Banking and corresponding expansion features |
| fds | Disk-image output |

These are compiler selections, not a hardware or emulator completeness table. `--board=surom512` selects a particular MMC1 board arrangement; merely padding a file to 512 KiB does not establish that arrangement. Use KUROSAKI's board audit alongside it.

{{CODE:6}}

Check board requirements for `--battery` / `--no-battery`, CHR capacity, PRG placement and banked calls. After changing a mapper or mirroring mode, test startup, scrolling and data switching as well as ROM generation.

Ordinary indexed reads and C pointer references to ROM arrays place those arrays in common bank 0 unless `#pragma fixed_bank` explicitly fixes their placement. This keeps the data visible when a caller runs in a switchable bank. For explicit far access, pass the bare array name with `__bankof` of that same name in the same call, for example `__farpeek8(__bankof(table), table)`. A bank-number query alone does not request common-bank placement. Explicit fixed-bank data and references inside assembly require you to maintain the correct mapping; this rule is a syntax-based placement check, not pointer-flow analysis. Common-bank capacity still applies.

## 9. FDS, expansion sound and peripherals
FDS involves disk-file placement, startup, overlays and saving. Consult `fds_manifest_sample.json` and the FDS headers. Prepare any required BIOS in your own runtime environment; the public distribution contains no BIOS.

Calling a VRC6 or VRC7 sound operation does not change the ROM's mapper setting. Match the mapper to the expansion sound being used. For peripherals, separately test readable input, connection state and effects on the ordinary controller path.

## 10. Diagnostics and build results
KQ diagnostics and developer commands such as `symfind`, `src2asm` and `romdiff` resemble their GB counterparts. Some inherited GB help choices may not represent implemented NES features. The FC dictionary is collected separately from FC source and headers.

Warnings such as KQ2421 for direct PPU operations can appear even in display-off initialization. Do not disrupt safe initialization merely to eliminate a warning: inspect rendering timing and execution logs. Zero errors and zero warnings are different outcomes.

## Source locations
The compiler sources and project file are in the repository’s same-named subdirectory. The executable is at the repository root, and the libraries are in `lib/`. See [the directory layout](../GITHUB_SETUP.md) for project paths and build requirements.
