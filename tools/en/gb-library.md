## 1. Use the library
The library is a collection of reusable C source built on KITAQGB's `__` intrinsics. It ranges from screen control to physics, 3D and communication.

{{CODE:0}}

{{CODE:1}}

Each API entry identifies its declaration, header, implementation and usage example. Functions without an existing example have a new argument-passing fragment. The caller must supply the buffers and objects used by such fragments. Use the complete-program section for examples that can be built into ROMs directly.

## 2. Build one game frame
`system_init` initializes frame management. `system_wait_vblank` waits and advances the software frame number. On GB, the VBlank callback is called cooperatively by that wait function; registering it does not install a hardware interrupt handler.

1. Update input once.
2. Calculate movement, collisions and game state.
3. Prepare drawing commands and OAM.
4. Apply updates during VBlank.
5. Advance music using the selected driver arrangement.

Combining waiting operations such as `vram_flush` and `sprite_flush_oam` can wait for two frames during one game update. After waiting yourself, a corresponding `_now` operation may be appropriate, provided you guarantee its timing requirements.

## 3. Input and repeat
`input_down(mask)` tests a held button, `input_pressed(mask)` tests a new press, `input_released(mask)` tests a release, and `input_repeat(mask)` provides menu-style repeat. These states update on `input_update()`. Calling update repeatedly within one frame can erase a press edge.

| Buttons | Masks |
| --- | --- |
| Right, Left, Up, Down | 0x01 / 0x02 / 0x04 / 0x08 |
| A, B, SELECT, START | 0x10 / 0x20 / 0x40 / 0x80 |

`gb_input.c` counts A presses. Verify that holding A does not continuously increment the count, then replace `input_pressed` with `input_down` to explore the difference.

## 4. Backgrounds, text and VRAM
`vram_queue_bg_tile` queues one tile, `vram_queue_bg_rect` queues a rectangle, and `vram_queue_bg_block` queues an array transfer. Check return values and `vram_get_overflowed()` for capacity overflow. If a queued operation retains a source pointer, keep its data unchanged, its memory valid and its bank accessible until flushing finishes.

`text.c` and `menu.c` implement the text, choice and window services declared in `rpg.h`. Match the text-to-tile mapping to the font you load into VRAM. It is not automatically the same mapping used by this manual's `m_text` helper.

## 5. Sprites and animation
Start with `sprite_init`, `sprite_alloc`, `sprite_set_tile` and `sprite_set_pos`. GB allows 40 sprites overall and 10 on a scanline, so account for horizontal concentration as well as total count. `sprite_warn_scanline_overflow` and `sprite_max_scanline_count` help inspect a layout.

`MetaSpritePart` describes relative OBJ placement. `SpriteAnim` describes tile frames and update intervals. Match the parts drawn by `metasprite_draw` to the OBJ slots you allocated. The A in `gb_sprite.c` demonstrates using a character tile as a sprite.

## 6. Color, scrolling, raster effects and cameras
RGB arguments to `cgb_bg_rgb` and `cgb_obj_rgb` range from 0 to 31, not 0 to 255. `CGB_RGB15` packs those components into a 16-bit container. The high-level CGB palette helpers are designed to do nothing on DMG.

`Scroll_SetBg` positions the background, `Scroll_SetWindow` positions the window, and the camera module derives a viewport from world coordinates. Keep camera fixed-point units separate from integer screen pixels.

`raster.c` constructs banded scroll tables and per-line horizontal distortion. `Scroll_SplitCommit` operations use VBlank/STAT vectors. Do not let separate music and scrolling handlers independently own the same vector; use a common dispatcher where needed.

## 7. Music and sound effects
Compile `audio_hwregs_gb.c`, then `audio.c`, then the game source. Do not add duplicate NR10-NR52 register definitions if the game already supplies them. After `Audio_Init`, normally call `Audio_Update` once per frame.

`Audio_PlayMusic(bank,song)` explicitly names the music bank. `Audio_PlaySFXBanked` plays an effect from another bank. Priorities arbitrate effects sharing physical channels. GB has four physical sound channels: CH1, CH2, CH3 and CH4.

The music-stream commands `AUDIO_CMD_NOTE` and `AUDIO_CMD_SET_INST` retain a historical order: **0=CH1, 1=CH2, 2=CH4, 3=CH3**. Do not confuse it with ordinary API channel constants. The header currently defines `AUDIO_NOTE_MAX=67`.

The basic CH1 effect stream reads note/volume pairs per frame and ends on note 0. CH3 uses a different marker and format. See `gb_sound.c`. Fades advance during `Audio_Update`; stopping updates also stops a fade.

## 8. VBlank IRQ music
`audio_vblank.c` is a separate driver arrangement. Each event contains five bytes: `delay, ch2_note, ch1_note, ch3_note, ch4_noise_param`. It supports directly referenced fixed-bank songs and banked songs replenished into a WRAM queue. Ordinary `audio.c` streams cannot be passed unchanged.

{{CODE:2}}

The patch sets the VBlank vector at 0x0040 and updates the checksum. Apply it only to a ROM designed for this driver. Check ownership against custom VBlank ISRs and split scrolling. Build success alone does not establish audible playback: record with KOKURA and verify that the song advances.

## 9. Fixed point, physics and 3D
In `fixed.h` Q8.8 arithmetic, 256 means 1.0 and 128 means 0.5. `gb_fixed.c` demonstrates `fix_from_int`, `fix_mul` and `fix_to_int`. Design value ranges before implementing calculations to avoid overflow.

`physics2d` handles rectangles, `physics2d_circle` handles circles, and `physics3d` handles 3D AABBs. Allocate and initialize world/body arrays, set velocity or gravity, then step the simulation. Rectangle positions and velocities use integer pixels and pixels per frame; inverse mass and friction coefficients use Q8. The circle example likewise uses integer position 40 and velocity 2. Inverse mass 0 denotes a fixed body. See `gb_circle.c` and the structure declarations for each coefficient's units.

`wire3d` provides a DMG 128-by-120 wireframe path, `x3d` an X-style 1bpp path, and `wire3d_cgb` a CGB color path. They differ in WRAM, VRAM and transfer requirements. Reserve each renderer's screen and memory regions explicitly rather than combining them blindly. The CGB path uses double speed and DMA and requires `--cgb=cgb_only`.

## 10. Scenes, object pools and bullet patterns
`scene` manages states such as title, play and pause; `entity` provides a fixed-capacity object pool; `chain` stores coordinate history for a snake, train or rope. Check allocation failure values such as 0xFF before using the pointer returned by `entity_get`.

`danmaku` provides fixed-point bullet pools, directional and fan spawning, hits and grazing. Its CGB background-compositing path avoids the ordinary OBJ count limit, but frame time and background-transfer bandwidth remain limited. Measure frame processing time rather than targeting bullet count alone.

## 11. RPG, adventure, strategy and saving
`rpg.h` collects declarations for random numbers, flags, quests, compression, text, menus, scripts, maps, saving and pathfinding. Implementations are split across files such as `rng.c`, `flags.c`, `rle.c` and `text.c`. Use the dictionary to select the required implementation units.

A fixed `rng_seed` produces a repeatable sequence for tests. Check whether each range function includes its upper bound. `flag_get` and `flag_set` operate on bit sets. `save.c` uses an MBC5-style SRAM access arrangement; match the ROM header's RAM capacity to the game's save region.

Keep `slg.h` board, legal-move-list and undo services, and `slg_path.c` pathfinding, separate from game-specific rules and evaluation. Width, height and work arrays must meet library limits as well as individual argument requirements.

## 12. Communication
`link.c` provides serial byte transfers; `link_packet.c` is an optional packet layer. Link `link_hwregs_gb.c` first. Polling and interrupt modes require different calls, and the game must connect vector 0x0058 for interrupt mode.

Logical `Link4_*` operations and physical Nintendo DMG-07 `LinkDmg07_*` operations are separate systems. DMG-07 uses an external clock: call `LinkDmg07_Poll` frequently and `LinkDmg07_TickFrame` once per frame. Polling only once per frame may miss timing requirements. With KOKURA pair/dmg07 jobs, test connection, start, disconnection and reconnection separately.

## 13. Banks, assets and debugging
`BankPtr` combines a bank number with a pointer. `far_data_read` reads another bank's assets into RAM. The asset module associates IDs with descriptors; the game remains responsible for lifetimes, banks and sizes.

`debug_trace_u8` and `debug_trace_u16` record values in RAM; `debug_assert_fail` records a diagnostic code. These are not `printf` calls to a PC console. Inspect the records through emulator memory observation. `gb_debug.c` records HP=42.
