## 1. KITAQFC and the GB compiler
KITAQFC uses the KITAQGB front end to generate code for the NES/Famicom's 6502-family CPU. It does not convert a GB ROM into an NES ROM. Write software for the target's display, sound, memory and mapper.

The recorded checks ran examples using structure copies and ordinary function calls. However, **do-while and switch produced unsupported-code-generation errors on NES**. A construct appearing in the parser is not sufficient evidence that it can be used on this target.

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

## 5. Rewrite unsupported constructs
{{CODE:4}}

Execute the loop body once before testing its exit condition to replace do-while. A simple switch dispatch can become an if/else chain. These are explanatory fragments: supply your own `update` and state functions. Use `fc_control.c` for a complete ROM example.

Do not assume desktop-style support for recursion, indirect function calls or variadic functions. Some scene/entity callback APIs currently store function pointers without invoking them indirectly.

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

## 9. FDS, expansion sound and peripherals
FDS involves disk-file placement, startup, overlays and saving. Consult `fds_manifest_sample.json` and the FDS headers. Prepare any required BIOS in your own runtime environment; the public distribution contains no BIOS.

Calling a VRC6 or VRC7 sound operation does not change the ROM's mapper setting. Match the mapper to the expansion sound being used. For peripherals, separately test readable input, connection state and effects on the ordinary controller path.

## 10. Diagnostics and build results
KQ diagnostics and developer commands such as `symfind`, `src2asm` and `romdiff` resemble their GB counterparts. Some inherited GB help choices may not represent implemented NES features. The FC dictionary is collected separately from FC source and headers.

Warnings such as KQ2421 for direct PPU operations can appear even in display-off initialization. Do not disrupt safe initialization merely to eliminate a warning: inspect rendering timing and execution logs. Zero errors and zero warnings are different outcomes.
