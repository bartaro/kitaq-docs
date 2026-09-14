## 1. Select the required components
`fc.h` collects declarations, `core.h` defines types, and `intrinsics.h` declares compiler operations. Ordinary C library functions require their corresponding `.c` implementation. Header-only macros and intrinsics may not require a same-named source file.

{{CODE:0}}

Do not point `-I` at the similarly named GB library. For example, NES `__oam_dma()` takes no argument, unlike the GB pointer-taking operation.

## 2. Runtime and system
`runtime.c` supplies C helpers for PPU registers, the OAM shadow and VRAM queues. Intrinsic paths such as `__vramq_*` also exist. Check which data the NMI handler consumes instead of mixing separate queues with similar names.

`system_init` initializes frame state and enables NMI. `system_wait_vblank` waits for NMI and increments the software frame count. **FC `system_set_vblank_callback` stores the value, but the current wait function does not execute the callback.** Do not place all game updates in that callback assuming GB behavior.

## 3. PPU, tiles, attributes and palettes
`ppu_direct.h` provides direct PPU operations, `vram_queue.h` provides NMI updates, `tilemap` / `nametable_asset` handle tables and assets, `attribute` updates attributes, and `palette` handles palettes. Separate initial loading from per-frame work.

Background and sprite palettes each occupy a 16-byte group. Palette values are NES color codes, not RGB components. Attributes select colors for groups of tiles, so changing a single tile's apparent palette can affect nearby tiles.

Some declarations in `ppu.h` do not match implementation names in `ppu.c`. Entries marked **declaration only** have no implementation found in the collected scope and are not used as direct calls in beginner examples. The runnable lessons use verified intrinsics. A declaration alone is not evidence of a completed, linkable feature.

## 4. OAM, metasprites and fair display
NES supports up to 64 sprites, normally eight per scanline. Nine or more enemies or bullets on one line cannot all appear simultaneously. Metasprites combine multiple OBJs into one image; check allocation boundaries and terminator formats.

`oam_fair.h` and `oam_fair_impl.h` rotate candidate ordering while maintaining priorities. They can prioritize a player or HUD and rotate less important objects over time. Reordering OAM does not change the hardware scanline limit.

## 5. Input, repeat and peripherals
`input.c` converts raw NES button values into GB-style `BTN_*` masks. **Raw NES A is 0x01; library BTN_A is 0x10.** Do not pass BTN_A directly to KUROSAKI's `--pad1` option.

`pad` reads basic input; `input_repeat` implements held-button repeat. `zapper`, `keyboard`, `rob`, `mic` and `midi` expose low-level device interfaces. A zero read from an absent device is not evidence of successful operation: check the device's connection requirements.

## 6. Sound
After `nes_apu_init`, use `nes_sfx_square1`, `nes_sfx_square2`, `nes_sfx_triangle` or `nes_sfx_noise` for built-in sound. A period argument is a hardware timer period, not a frequency in hertz. `fc_sound.c` is a minimal pulse-sound example.

DMC samples have address, length, alignment and rate constraints. Inspect map placement before supplying a pointer. DMC DMA can also create controller-read interference candidates, so combine safe controller reads with KUROSAKI diagnostics.

VRC6 provides extra pulse and saw channels, VRC7 exposes FM registers, and FDS provides wavetable sound. Use a matching mapper and record the result. These APIs are separate from the GB `Audio_*` driver.

## 7. Scenes, actors and entities
`actor` and `entity` store game objects in fixed arrays; `scene` stores scene state. Detect capacity exhaustion and stop using destroyed IDs. Some FC APIs currently register callbacks without calling them. For beginner programs, explicitly dispatch state-specific update functions from the main loop.

`chain` stores coordinate history; `collision` tests contact between shapes such as rectangles. A consistent move, collide, draw order avoids collision decisions that lag by a frame.

## 8. Mathematics and physics
`fixed.h` provides Q8.8 arithmetic, `math_fast` / `math_fixed` provide numeric operations, and `math_lut` provides table-based calculations. The current `physics2d.h` supplies **Q5.3 types and constants**, not an integration-function or update-macro implementation. It is not the GB world/body physics API.

Q5.3 fractions represent eighths of a pixel. Keep integer coordinates, fractional parts, velocity and direction separately and perform addition and carry handling in game code. `fc_subpixel.c` adds 2/8 pixel eight times, moving from pixel 40 to pixel 42. Do not reuse the Q8.8 representation 256 unchanged as Q5.3.

## 9. Assets, mappers and FDS
`bank` and `asset` describe PRG banks and assets. Whether an operation in `mapper.h` is effective depends on the mapper chosen at build time. Design scroll IRQ configuration, enable, acknowledgment and disable as one coherent sequence.

FDS services are divided among `fds_file`, `fds_overlay`, `fds_save` and `fds_sound`. Loading an overlay replaces code at an existing address, so pay attention to return targets and data lifetimes. Do not assume ordinary cartridge far-call behavior.

## 10. Reference entries and examples
The dictionary below follows public headers and distinguishes functions, function-like macros and aliases. Full headers also expose structures and constants. Declaration-only APIs, stored-only callbacks and specialized device interfaces are identified separately from verified ordinary operations. Source comments are retained verbatim for accurate comparison with the implementation.

`vram_get_queue_capacity()` returns the total command-buffer capacity (128 bytes). `vram_get_queue_free()` returns the remaining bytes: total capacity minus `vram_get_queue_used()`. These are encoded command bytes, including metadata, not available space in hardware VRAM. A single-tile write needs 4 bytes, a fill needs 5, and a pointer-based copy needs 6. Check space before committing; NMI can consume a committed queue asynchronously.
