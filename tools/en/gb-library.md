## 1. Use the library
The library is a collection of reusable C source built on KITAQGB's `__` intrinsics. It ranges from screen control to physics, 3D and communication.

{{CODE:0}}

{{CODE:1}}

Each API entry identifies its declaration, header, implementation and usage example. Argument-passing fragments show how to call the API; the caller must prepare the buffers and objects they use. The complete-program section contains examples that can be built directly into ROMs.

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

The music-stream commands `AUDIO_CMD_NOTE` and `AUDIO_CMD_SET_INST` use this channel encoding: **0=CH1, 1=CH2, 2=CH4, 3=CH3**. Do not confuse it with ordinary API channel constants. The header currently defines `AUDIO_NOTE_MAX=67`.

The basic CH1 effect stream reads note/volume pairs per frame and ends on note 0. CH3 uses a different marker and format. See `gb_sound.c`. Fades advance during `Audio_Update`; stopping updates also stops a fade.

## 8. VBlank IRQ music
`audio_vblank.c` uses a separate playback format. Timed records contain five bytes: `delay, ch2_note, ch1_note, ch3_note, ch4_noise_param`. The driver reads directly addressable songs or consumes a WRAM queue; the public library does not include a queue-refill routine. Your game must supply the producer and coordinate its writes with the ISR. `LOOP` is recognized only in direct streams, and `IMMEDIATE` only in queue mode. Ordinary `audio.c` streams cannot be passed unchanged.

{{CODE:2}}

The patch sets the VBlank vector at 0x0040 and updates the checksum. Apply it only to a ROM designed for this driver. Check ownership against custom VBlank ISRs and split scrolling. Build success alone does not establish audible playback: record with KOKURA and verify that the song advances.

## 9. Fixed point, physics and 3D
In `fixed.h` Q8.8 arithmetic, 256 means 1.0 and 128 means 0.5. `gb_fixed.c` demonstrates `fix_from_int`, `fix_mul` and `fix_to_int`. Design value ranges before implementing calculations to avoid overflow.

`physics2d` handles rectangles, `physics2d_circle` circles, and `physics3d` 3D AABBs. Initialize caller-owned world/body arrays, set velocity or gravity, then step the simulation. Use consistent position and per-step velocity units; the library performs no implicit pixel conversion. The circle example uses position 40 and velocity 2. A zero inverse mass denotes a static body. Check each coefficient and intermediate arithmetic range in the headers. In particular, `kq2d_body_apply_friction` casts its coefficient to a signed byte: values 128–255 are negative, not ordinary unsigned Q8 damping. See `gb_circle.c` for a complete step example.

`wire3d_dmg` is a monochrome wireframe renderer for Game Boy. Select 128 × 96 with `wire3d_dmg_96.c`, or 128 × 120 with `wire3d_dmg.c`, and use `Wire3DDMG_*`. `wire3d` and `dmg3d` provide alternative entry points for the 96-line and 120-line profiles, respectively. Compile one entry point per program. `wire3d_cgb` is the dedicated color renderer. Reserve each renderer's RAM, VRAM and display regions explicitly. The two monochrome renderers reject depth-crossing edges rather than clipping them. Their scene occlusion uses face bounding rectangles and five samples along each line, so it is an approximation rather than per-pixel depth testing. The CGB path uses double speed and DMA and requires `--cgb=cgb_only`.

`Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=96`) clears the stage. `Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=120`) only resets occlusion state: DMG3D consumes and clears staged bytes during upload. Dirty transfer includes the previous frame's tiles to erase old pixels. Its auxiliary transfer shares part of the main stage; it is not an independent buffer. Match the frame sequence to the renderer you use.

For CGB lines, use colors 1, 2 and 3. Normal 128 × 96 lines combine color bits, so overlapping colors 1 and 2 become color 3. Color 0 does not erase a line. Clear the frame or use the dedicated erasing functions. Normal `Wire3DCGB_DrawLine2D` and model drawing do not record sparse upload bounds: use `Wire3DCGB_DrawLineClipped2D` for lines that need this tracking, or call `Wire3DCGB_InvalidateFrameHistory` to include the entire viewport in the next sparse upload.

The 160 × 144 mode allocates at most 127 tiles per frame. An allocation failure or an out-of-range coordinate in its fast line path sets `Wire3DCGB_GetFullScreenOverflow()` and suppresses further pixel writes until the next frame reset. Keep vertices within the selected viewport. Triangle-mask padding stops at X=127 in 128 × 96 mode and X=159 in full-screen mode. Follow the API notes for WRAM bank mapping, especially when using full-screen or FastMap functions.

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

`vram_get_queue_capacity()` returns the total number of command slots (32 by default). `vram_get_queue_free()` returns the number of unused slots, and `vram_get_queue_used()` returns the occupied count. One queued operation takes one slot regardless of its transfer size. These queries describe the transfer queue, not unused hardware VRAM.
