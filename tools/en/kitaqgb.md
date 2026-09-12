## 1. Meet KITAQGB
KITAQGB is a GB/CGB C-family compiler developed from Zachtronics' NORCAL. {{ORIGIN}} It reads C files, generates CPU instructions and packages them into a ROM. Its language, libraries and calling conventions differ from those of a desktop C compiler.

The GB has an 8-bit CPU and limited memory. Most screen graphics use 8-by-8-pixel tiles. Sprites are small independently positioned images. Text also needs tile graphics: a built-in universal text display is not assumed. These examples use the author's `ascii.c` glyphs, rearranged by ASCII code for GB without changing their bits. The FC edition converts the same shapes to NES CHR layout.

## 2. Requirements and compiler build
Install a Visual Studio/MSBuild environment targeting .NET Framework 4.8. Use a Developer PowerShell prompt in which `MSBuild.exe` is available.

{{CODE:0}}

If using a separately supplied executable, keep the files belonging to that version together. Record which executable you used: an old copy at a workspace root can differ from a newly built `bin\Release` copy. The published project also places its built executable in the `kitaqgb` checkout root.

## 3. Your first program
The supplied `samples/gb_hello.c` uses screen and text helpers from `gb_common.h`. Keep that header and the font files together. `#include` reads declarations or definitions from another file.

{{CODE:1}}

{{CODE:2}}

The example's target is HELLO WORLD and 042 on screen. Names beginning with `m_` are teaching helpers defined in the common sample header, not standard KITAQGB commands. The compiler intrinsics include operations such as `__wait_vblank` and `__vram_copy`.

## 4. Basic syntax and types
End statements with `;` and group statements with `{ }`. `//` begins a line comment; `/* ... */` is a block comment. Names are case-sensitive. Use `void main()` as the entry point. **In this GB version, `void main(void)` produces a syntax error**, so do not copy the FC entry-point declaration unchanged.

| Type | Meaning and range |
| --- | --- |
| `u8` | Unsigned 8-bit integer, 0 to 255 |
| `s8` | Signed 8-bit integer, -128 to 127 |
| `u16` | Unsigned 16-bit integer, 0 to 65535 |
| `s16` | Signed 16-bit integer, -32768 to 32767 |
| `void` | No return value |
| `T*` | Pointer to data of type T |

Start with these short type names. Do not assume desktop definitions of `int`, `long`, `float`, `double` or standard headers. This version treats `char` as unsigned 8-bit data; explicitly use `s8` or `s16` when signed arithmetic is needed.

{{CODE:3}}

`(u16)` is a cast. Assigning an already-overflowed small value to a larger variable does not recover lost bits: widen operands before the calculation. Use the fixed-point library for fractional movement.

## 5. Expressions and operators
| Group | Operators | Example or meaning |
| --- | --- | --- |
| Arithmetic | `+ - * / %` | `n / 10` is the integer quotient; `n % 10` is the remainder |
| Comparison | `== != < <= > >=` | `lives == 0` tests equality |
| Logic | `! &&` / `||` | Negation, both conditions, either condition |
| Bits | `&` / `|` / `^ ~ << >>` | Button masks and other bit sets |
| Assignment | `= += -=` and related forms | `x += 1` updates a value |
| Increment | `++ --` | `i++` increments by one |
| Selection | `condition ? A : B` | Choose a value according to a condition |
| Pointers | `&variable` / `*p` | Obtain an address or access its target |

Distinguish `=` from `==`. Use parentheses to make complex expressions clear, and avoid crowding calls and side effects into a single statement. Avoid division by zero and out-of-bounds array accesses. `sizeof` gives a size in bytes; `offsetof` gives a structure member's offset.

## 6. Branches and loops
{{CODE:4}}

`break` leaves a loop or switch, `continue` starts the next iteration, and `return` leaves a function. Use the explicit `fallthrough;` statement when deliberately continuing from one switch case into the next; implicit fall-through is diagnosed. See the complete `gb_control.c` example.

## 7. Functions, arrays and structures
{{CODE:5}}

Array indexes begin at zero: a four-element array has indexes 0 through 3. `player.x` selects a member; `pointer->x` accesses a member through a pointer. Structures, unions and enums are parsed, but layout depends on types and `__packed` / `__aligned` attributes. Check `sizeof` before sharing data with hardware or binary formats.

The default Legacy ABI places arguments and local storage at fixed locations. Do not assume desktop-style recursion or interrupt reentrancy. `__stackcall` and `--abi=stack` are advanced calling-convention choices. When combining conventions, inspect ABI reports and verify execution.

## 8. Multiple files and the preprocessor
Put types, constants and declarations in headers and function bodies in `.c` files. Use `#pragma once` or include guards to prevent repeated inclusion. Conditional compilation supports `#define`, `#undef`, `#if`, `#ifdef`, `#ifndef`, `#elif`, `#else` and `#endif`.

{{CODE:6}}

`-I` adds a header search directory. Including a library header does not link its implementation: list the required `.c` files in the build command. Select the units you need; indiscriminately adding all library sources can duplicate register definitions or interrupt handlers.

## 9. ROM, memory and banks
ROM stores code and constants, WRAM stores variables, VRAM stores graphics and OAM stores sprite descriptions. Banking changes which physical memory appears at a CPU address. A 16-bit pointer alone cannot identify data in another bank.

{{CODE:7}}

`__prg_rom` places data in ROM. Attributes such as `__location(0xFF40)` choose a fixed address, while `__wram` / `__hram` select memory regions. When using `#pragma bank` or `#pragma fixed_bank`, inspect the map and ensure that code and data used by interrupts remain accessible.

{{CODE:8}}

`--cgb=dmg` declares DMG-oriented software, `--cgb=cgb` declares dual-mode software, and `--cgb=cgb_only` declares CGB-only software. Dual-mode games must detect hardware before using CGB-only features. A header flag does not implement dual-mode behavior inside your game.

## 10. Safe graphics updates
VBlank is the gap between display frames. Unscheduled VRAM and OAM writes can cause corruption or lost updates. Load initial assets while the display is off; use safe intrinsics or the VRAM queue for regular updates. Functions marked `_unsafe` or `_fast` require the caller to provide a safe transfer interval.

Align the OAM DMA buffer to a 256-byte boundary. On GB, `__oam_dma` takes the source address. The FC intrinsic with the same name takes no arguments: keep these APIs separate.

## 11. Build commands and outputs
`-o` selects the output, `-O0` / `-O1` select optimization, and `--profile=dev|release|test` chooses a group of settings. `--no-disasm` suppresses disassembly output. `--debug-out=...` and `--trace-out=...` choose investigation output locations. Use the amount of output appropriate for a fast build or a detailed investigation.

{{CODE:9}}

`.map` records names and placement; `.funcsizes.txt` records function sizes; `.dbg2.json` / `.source_map.txt` connect execution positions to source; `.build_report.json` summarizes the build. Explicitly producing `--emit-ai-metadata` JSON makes the path into SARAKURA easier to follow.

## 12. Read errors from the beginning
Read the filename, line and KQ diagnostic number at the first error. Later errors may be consequences of the first syntax mistake. For an undefined symbol, check its declaration, implementation and inclusion in the build. For ROM overflow, inspect asset sizes, function sizes and bank placement.

{{CODE:10}}

## 13. Inline assembly
`__asm { ... }` accepts KITAQGB's instruction names. It is not a promise to accept arbitrary source written for another GB assembler. Internal spellings include names such as `LD_A_IMM`. Understand arguments, return values, preserved registers and stack behavior before using inline assembly. The appendix lists instruction spellings and operand forms.

{{CODE:11}}
