## Welcome
KITAQGB began as a **fork of NORCAL**, the NES C compiler associated with Zachtronics. It develops that foundation into a C-family compiler for Game Boy and Game Boy Color, with code generation, memory, video, audio and ROM banking adapted to those machines. We acknowledge the original project and its author, Keith Holman.

{{ORIGIN}}

NORCAL was developed in connection with the NES version of HACK*MATCH. See the author's introductions to [NORCAL: A C Compiler for the NES](https://keithholman.net/nes-compiler.html) and [HACK*MATCH for the NES](https://trashworldnews.com/hack-match/). The project history and name explanation follow the README supplied by the author.

## How to use these manuals
Like an early computer manual, this collection starts with short programs you can type, build and run. You can learn the machinery after seeing the result; you do not need to memorize every term first.

1. Start with the first program in Volume 1 for GB or Volume 4 for FC.
2. Use Volume 2 or Volume 5 to add input, graphics and sound.
3. Observe execution with KOKURA or KUROSAKI, then organize diagnostics with SARAKURA.
4. Search the volume or its API dictionary when you already know a function name.

Language syntax, compiler intrinsics, library functions and command-line operations are separate kinds of reference entries. The compiler volumes also contain CPU instruction indexes. Similar GB and FC names do not guarantee identical arguments or behavior.

## The seven volumes
| Volume | Input | Output or purpose |
| --- | --- | --- |
| KITAQGB | C source and assets | GB/CGB ROMs, maps and build information |
| KITAQGB library | Calls from game code | Graphics, sound, input, communication and game services |
| KOKURA | GB/CGB ROMs | Execution, pictures, audio, state and observations |
| KITAQFC | C source and CHR assets | NES/FDS output and build information |
| KITAQFC library | Calls from game code | NES graphics, sound and device services |
| KUROSAKI | NES/FDS images | Execution, recording and analysis |
| SARAKURA | Build information and diagnostic events | Reports, repair plans and retest plans |

## The supplied font
The 26 uppercase letters, 10 digits, 26 lowercase letters and 30 symbols come from the author's [ascii.c](samples/assets/ascii.c). No additional glyph shapes were invented. The original 92 glyphs are preserved; see the [conversion map](verification/font_conversion.json) and [tile atlas](verification/font_source_atlas.png). Space uses an empty tile. Backslash and the vertical bar are absent from the supplied font and display as blanks. `gb_font.c` and `fc_font.c` display every supplied glyph.

## Edition and verification
This edition is based on the **local source snapshot of September 12, 2026**. “Latest” refers to that snapshot, not automatic tracking of future GitHub changes. The reference inventory records source and executable fingerprints. Historical README claims about support or verification are not automatically treated as current guarantees.

A successful build means a ROM was produced. An execution check means an emulator advanced through the specified frames. Pixel comparisons, input behavior and sound checks are recorded separately. This is not a guarantee of compatibility with every peripheral or physical console; warnings remain visible in the logs.

The current public source release excludes KOKURA GUI frontends, KUROSAKI GUI and PLITA. Use the published cores, CLIs and integration APIs now.

## Prepare a working directory
Examples use **Windows PowerShell**. Save C files as UTF-8 text. The current directory is the folder in which you run a command. Quote paths containing spaces and invoke an executable with `& "path"` when needed. Clone the repositories as siblings, following [GitHub setup](../GITHUB_SETUP.md), and run cross-project commands from their parent folder.

{{CODE:0}}

Replace `game.c`, `game.gb` and `game.nes` with your filenames. Angle brackets such as `<ROM>` mark placeholders; do not type the brackets. Commands are generally presented on one line. Bash's backslash line continuation is not PowerShell syntax.

## Compiler fixes used by this edition
Building the examples exposed a KITAQGB internal local-label collision and KITAQFC problems preserving intermediate values and return values across calls. The recorded manual checks used the corrected compilers, including the GB object-pool example and FC functions and structures. These fixes do not establish support for every C construct. Consult each example's [verification record](verification.html).

## Read, print and publish the HTML
Open `index.html` from the downloaded folder to read offline. Styles, search, examples and verification pictures use local files; no external CDN is required. Keep the directory together rather than copying individual HTML files. The print button produces a layout without the navigation column.

The `kitaq-docs` repository holds the manual website. GitHub normally displays HTML source in the repository browser; GitHub Pages serves the rendered website. See the repository README for publication and checkout instructions. This English edition contains the same seven volumes, API entries, sample programs and verification references as the Japanese edition. Original source excerpts and recorded tool output retain their original wording where translation would obscure the exact source or command response.
