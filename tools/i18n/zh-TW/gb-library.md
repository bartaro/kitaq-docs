## 1. 使用函式庫
這套函式庫是建立在 KITAQGB `__` 內建函式之上的可重用 C 原始碼，涵蓋畫面控制、物理、3D 和通訊等功能。

{{CODE:0}}

{{CODE:1}}

每個API項目都列出宣告、標頭、實作與使用範例。引數傳遞片段示範API的呼叫方式，其中使用的緩衝區與物件須由呼叫端準備。完整程式章節提供可直接建置為ROM的範例。

## 2. 組織遊戲的一個影格
`system_init` 初始化影格管理；`system_wait_vblank` 等待後推進軟體影格數。GB 的 VBlank 回呼由等待函式以協作方式呼叫，註冊回呼不等於安裝硬體中斷處理常式。

1. 更新輸入一次。
2. 計算移動、碰撞和遊戲狀態。
3. 準備繪圖命令與 OAM。
4. 在 VBlank 期間套用更新。
5. 依選定的驅動方案推進音樂。

連用 `vram_flush`、`sprite_flush_oam` 等等待操作，可能讓一次遊戲更新等上兩個影格。若已自行等待，可考慮對應的 `_now` 操作，但必須保證其時序條件。

## 3. 輸入與重複輸入
`input_down(mask)` 檢查按住，`input_pressed(mask)` 檢查新按下，`input_released(mask)` 檢查放開，`input_repeat(mask)` 提供選單式重複輸入。狀態由 `input_update()` 更新；同一影格反覆呼叫，可能遺失剛按下的邊緣資訊。

| 按鈕 | 遮罩 |
| --- | --- |
| 右、左、上、下 | 0x01 / 0x02 / 0x04 / 0x08 |
| A、B、SELECT、START | 0x10 / 0x20 / 0x40 / 0x80 |

`gb_input.c` 計算 A 按下次數。先確認長按不會持續累加，再將 `input_pressed` 換成 `input_down`，觀察差異。

## 4. 背景、文字與 VRAM
`vram_queue_bg_tile` 排入一個圖塊，`vram_queue_bg_rect` 排入矩形填滿，`vram_queue_bg_block` 排入陣列傳輸。檢查傳回值和 `vram_get_overflowed()`，及早發現容量溢位。若佇列保留來源指標，套用完成前須保持內容不變、記憶體有效、bank 可存取。

`text.c`、`menu.c` 實作 `rpg.h` 宣告的文字、選項與視窗功能。文字到圖塊的對應須符合載入 VRAM 的字型，不會自動採用手冊 `m_text` 的對應。

## 5. 精靈與動畫
從 `sprite_init`、`sprite_alloc`、`sprite_set_tile`、`sprite_set_pos` 開始。GB 共允許 40 個精靈，每條掃描線最多 10 個，因此除了總數，也要考慮橫向集中程度。可用 `sprite_warn_scanline_overflow`、`sprite_max_scanline_count` 檢查配置。

`MetaSpritePart` 描述相對 OBJ 位置；`SpriteAnim` 描述圖塊影格與更新間隔。`metasprite_draw` 繪製的部件應與配置的 OBJ 槽位相符。`gb_sprite.c` 以字母 A 示範將字元圖塊當成精靈。

## 6. 色彩、捲動、光柵效果與鏡頭
`cgb_bg_rgb`、`cgb_obj_rgb` 的 RGB 引數範圍是 0～31，不是 0～255。`CGB_RGB15` 將分量封裝到 16 位元容器。高階 CGB 調色盤輔助函式在 DMG 上設計為不執行操作。

`Scroll_SetBg` 設定背景位置，`Scroll_SetWindow` 設定視窗位置，camera 從世界座標計算可見區域。請區分鏡頭的定點單位和畫面的整數像素。

`raster.c` 建立分段捲動表與逐掃描線水平扭曲。`Scroll_SplitCommit` 使用 VBlank／STAT 向量。不要讓音樂和捲動的獨立處理常式各自占用同一向量；必要時採用共用分派器。

## 7. 音樂與音效
依序編譯 `audio_hwregs_gb.c`、`audio.c`、遊戲原始碼。遊戲已定義 NR10～NR52 時，不要加入重複定義。`Audio_Init` 後通常每影格呼叫一次 `Audio_Update`。

`Audio_PlayMusic(bank,song)` 明確指定樂曲 bank；`Audio_PlaySFXBanked` 播放另一 bank 的音效。共用實體通道的音效依優先順序協調。GB 只有 CH1、CH2、CH3、CH4 四個實體音訊通道。

音樂串流命令 `AUDIO_CMD_NOTE`、`AUDIO_CMD_SET_INST` 使用以下通道編號：**0=CH1、1=CH2、2=CH4、3=CH3**。不要與一般 API 通道常數混淆。目前標頭定義 `AUDIO_NOTE_MAX=67`。

基本 CH1 音效串流每影格讀取音符／音量配對，以音符 0 結束。CH3 採用不同標記和格式，請看 `gb_sound.c`。淡入淡出由 `Audio_Update` 推進，停止更新也會停止漸變。

## 8. VBlank IRQ 音樂
`audio_vblank.c` 使用獨立的播放格式。帶有時間資訊的記錄由5個位元組組成：`delay, ch2_note, ch1_note, ch3_note, ch4_noise_param`。驅動程式可以讀取可直接定址的樂曲，也可以從WRAM佇列取出資料。公開函式庫不包含佇列補充函式，遊戲需要自行提供資料產生端，並協調其寫入與ISR的執行。`LOOP` 僅用於直接定址模式，`IMMEDIATE` 僅用於佇列模式。一般 `audio.c` 的資料流不能原樣傳入。

{{CODE:2}}

修補步驟設定 0x0040 的 VBlank 向量並更新檢查碼，只能用於為此驅動設計的 ROM。請檢查與自訂 VBlank ISR、分割捲動的向量占用關係。建置成功不代表音樂已正確播放；應以 KOKURA 錄音，確認樂曲確實前進。

## 9. 定點數、物理與 3D
`fixed.h` 的 Q8.8 中，256 代表 1.0，128 代表 0.5。`gb_fixed.c` 示範 `fix_from_int`、`fix_mul`、`fix_to_int`。先規劃數值範圍，再實作計算，以免溢位。

`physics2d` 處理矩形，`physics2d_circle` 處理圓，`physics3d` 處理三維AABB。由呼叫端準備並初始化world和body陣列，設定速度或重力後再呼叫step。位置與每步速度應採用一致的單位；函式庫不會自動換算成像素。圓形範例使用位置40、速度2。逆質量為0表示靜態物體。各係數的表示方式與中間計算的數值範圍請參閱標頭檔。尤其要注意，`kq2d_body_apply_friction` 會將係數轉成帶正負號的8位元數值，因此128～255會變成負數，不能當作一般無正負號Q8衰減係數使用。完整的單步範例見 `gb_circle.c`。

`wire3d_dmg` 是適用於Game Boy的黑白線框繪圖函式庫。128×96畫面使用 `wire3d_dmg_96.c`，128×120畫面使用 `wire3d_dmg.c`，函式統一採用 `Wire3DDMG_*` 名稱。`wire3d` 與 `dmg3d` 也可分別作為96行與120行設定的入口，每個程式只編譯一個入口。`wire3d_cgb` 是專供彩色顯示使用的繪圖引擎。請明確預留各繪圖引擎使用的RAM、VRAM與畫面區域。兩種黑白引擎會直接略過跨越深度範圍邊界的邊，不會加以裁切。場景遮蔽也只是利用面的包圍矩形與線上5個取樣點進行近似判斷，並非逐像素深度測試。 CGB路徑使用雙倍速與DMA，需要 `--cgb=cgb_only`。

`Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=96`) 會清空繪圖緩衝區。`Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=120`) 則只重設遮蔽狀態，DMG3D的暫存資料在上傳至VRAM時才會清除。差異圖塊傳輸也會處理上一影格的圖塊，以清除舊像素。輔助傳輸與主緩衝區共用部分記憶體，並非獨立緩衝區。請依所用引擎安排每影格的呼叫順序。

CGB版的線條請使用色彩編號1、2、3。一般128 × 96模式會疊加色彩位元，因此色彩1與色彩2重疊後會變成色彩3。色彩0不能用來擦除線條；請清空影格緩衝區或使用專用擦除函式。一般 `Wire3DCGB_DrawLine2D` 與模型繪製不會記錄差分傳輸範圍。若要在繪製線條時一併記錄範圍，請使用 `Wire3DCGB_DrawLineClipped2D`；若要讓下一次差分傳輸包含整個顯示區域，請呼叫 `Wire3DCGB_InvalidateFrameHistory`。

160 × 144模式每個影格最多配置127個圖塊。高速線條繪製路徑遇到圖塊配置失敗或畫面範圍外的座標時，`Wire3DCGB_GetFullScreenOverflow()` 會傳回非零值，並停止寫入像素，直到下一個影格重新初始化。請將頂點限制在所選顯示區域內。三角形遮擋遮罩的右側餘量，在128 × 96模式下最多延伸到X=127，全畫面模式下最多到X=159。使用全畫面或FastMap功能時，尤其要遵守API說明中的WRAM記憶體庫映射要求。

## 10. 場景、物件池與彈幕
`scene` 管理標題、遊戲、暫停等狀態，`entity` 提供固定容量物件池，`chain` 保存蛇、列車、繩索的座標歷史。使用 `entity_get` 傳回的指標前，先檢查 0xFF 等配置失敗值。

`danmaku` 提供定點彈池、定向和扇形發射、命中與擦彈。CGB 背景合成路徑能避開一般 OBJ 數量限制，但影格處理時間與背景傳輸頻寬仍有限。請量測每影格耗時，而不只追求子彈數量。

## 11. RPG、冒險、策略與儲存
`rpg.h` 統整亂數、旗標、任務、壓縮、文字、選單、腳本、地圖、儲存、尋路宣告；實作分散於 `rng.c`、`flags.c`、`rle.c`、`text.c` 等檔案。依辭典選擇需要的實作單元。

固定 `rng_seed` 可重現測試數列。請確認範圍函式是否包含上限。`flag_get`、`flag_set` 操作位元集合。`save.c` 使用 MBC5 式 SRAM 存取，ROM 標頭的 RAM 容量須與儲存區域相符。

`slg.h` 的棋盤、合法行動清單和復原，以及 `slg_path.c` 的尋路，應與遊戲專屬規則和評估分開。寬、高、工作陣列除了符合個別參數條件，也須符合函式庫上限。

## 12. 通訊
`link.c` 提供序列位元組傳輸，`link_packet.c` 是選用的封包層。先連結 `link_hwregs_gb.c`。輪詢與中斷模式需要不同呼叫；中斷模式還要求遊戲連接 0x0058 向量。

邏輯 `Link4_*` 與實體 Nintendo DMG-07 的 `LinkDmg07_*` 是不同系統。DMG-07 使用外部時脈，應頻繁呼叫 `LinkDmg07_Poll`，每影格呼叫一次 `LinkDmg07_TickFrame`。每影格只輪詢一次可能不符時序要求。使用 KOKURA pair/dmg07 工作時，請分別測試連線、啟動、斷線與重新連線。

## 13. Bank、素材與除錯
`BankPtr` 結合 bank 編號與指標；`far_data_read` 將其他 bank 的素材讀入 RAM。asset 為 ID 關聯描述資料，但資料生命週期、bank 和大小仍由遊戲負責。

`debug_trace_u8`、`debug_trace_u16` 將數值記入 RAM，`debug_assert_fail` 記錄診斷碼。這不是向電腦主控台輸出的 `printf`，請透過模擬器記憶體觀察來讀取。`gb_debug.c` 記錄 HP=42。

`vram_get_queue_capacity()` 傳回命令佇列的總槽位數（預設為32），`vram_get_queue_free()` 傳回可用槽位數，`vram_get_queue_used()` 傳回已用槽位數。不論傳輸多少資料，一項排入佇列的操作都占用一個槽位。這些函式查詢的是傳輸佇列的容量，並非實際 VRAM 中的可用空間。
