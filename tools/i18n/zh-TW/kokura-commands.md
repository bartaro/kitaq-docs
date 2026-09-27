## 13. 命令操作範例與精確參數語法

請在各儲存庫資料夾共同的上層目錄執行以下 PowerShell 命令。先用 `New-Item -ItemType Directory -Force out` 建立輸出目錄，再將 `out/game.gb` 換成自己的 ROM。KOKURA 將選項放在 ROM 路徑之後，不使用 KUROSAKI 的 `run` 子命令。`--help` 可列出目前安裝的執行檔所支援的選項。

### 13.1 選擇操作與影格上限

| 參數 | 用途與行為 |
| --- | --- |
| `ROM` | 一般執行所用的 ROM 檔。工作或測試矩陣也可自行提供 ROM。 |
| `--hardware auto`, `dmg`, `cgb` | 選擇硬體，預設為 `auto`。雙模式遊戲應明確指定兩種模式分別測試。 |
| `--run-frames 120` | 直接執行的影格數上限，預設為 1。停止條件可能使執行提早結束；輸入序列也有各自的持續時間。 |
| `--job out/test.json` | 執行 JSON 工作。影格上限放在 `run.frames`；ROM、狀態、輸入與擷取設定來自工作內容。工作內的相對路徑以工作檔所在位置為基準。 |
| `--dump-report out/run.json` | 儲存結果 JSON 報告。未指定輸出目的地時，一般執行會將報告寫至標準輸出。 |
| `--regression-matrix out/matrix.json` | 執行附有預期觀測值的工作。請檢查 JSON 中各案例的結果：矩陣命令成功執行不代表每個案例都通過。 |

每次呼叫請選擇一種操作。分派優先順序為反編譯、反組譯、迴歸測試矩陣、連線工作、命令列直接指定的連線工作階段，最後才是一般執行。同時指定多種模式不會使它們依序全部執行。

{{COMMAND:0}}

此命令最多推進 120 個模擬影格，並儲存最終畫面與報告。解讀圖片前，請先查看報告中的實際影格數和停止原因。

### 13.2 持續按鍵或提供定時輸入序列

| 選項 | 語法與用法 |
| --- | --- |
| `--input "A,RIGHT"` | 在直接執行期間持續按住兩個按鍵。名稱不區分大小寫；`NONE` 表示放開所有按鍵。 |
| `--input-seq "NONE:30;A:1;NONE:89"` | 依序執行以分號分隔的 `BUTTONS:FRAMES` 區段。此例先放開 30 影格、按 A 一影格，再放開 89 影格。 |
| `--input-script "NONE:30;A:1;NONE:89"` | 接受相同的序列文字，不是檔名。兩種序列選項都指定時，以 `--input-script` 為準。 |

按鍵名稱為 `RIGHT,LEFT,UP,DOWN,A,B,SELECT,START`。十六進位遮罩為 RIGHT=0x01、LEFT=0x02、UP=0x04、DOWN=0x08、A=0x10、B=0x20、SELECT=0x40、START=0x80。這些是 KOKURA 的輸入遮罩，請勿套用 NES 控制器遮罩。在 PowerShell 中，請以引號括住整段序列。測試新按下的瞬間時，須安排放開按鍵的區段，並讓序列涵蓋要觀察的完整時間範圍。

{{COMMAND:1}}

對按鍵計數範例而言，這應使計數增加一次。僅憑靜態圖片無法判斷長按重複是否正常；請比較持續按住與分次按下的結果。

### 13.3 擷取畫面、動態影像與聲音

| 選項 | 語法與用法 |
| --- | --- |
| `--png out/final.png` | 儲存最終畫面；與 `--screenshot` 同時指定時，此選項優先。 |
| `--screenshot out/frame.png` | 另一種畫面儲存目的地。支援 PNG 和 BMP；未含副檔名的路徑會加上 `.png`。 |
| `--screenshot-frames 30:32` | 儲存每個選定影格，並在輸出檔名中加入影格編號。必須另行指定畫面儲存目的地。 |
| `--record-wav out/audio.wav` | 將聲音錄製為 WAV。請使用確實會發聲的 ROM 與時間區間。 |
| `--record-wav-frames 1:180` | 選擇含首尾的錄音區間；數值是影格編號，不是取樣數。 |
| `--record-video out/motion.gif` | 以 GIF 或 Y4M 記錄動態影像。未含副檔名的路徑會加上 `.gif`；不接受 MP4 格式。 |
| `--record-video-frames 30:120` | 選擇含首尾的影像記錄區間。 |
| `--audio-buffer-frames 8192` | 以立體聲取樣影格為單位設定音訊緩衝容量，不是模擬畫面的影格數，也不是個別左、右聲道的取樣數。 |

擷取範圍使用從 1 起算的十進位編號：`30` 選取單一影格，`30:32` 包含第 30、31、32 影格。0 或逆序範圍會被拒絕。擷取索引以本次執行為基準，因此從先前狀態恢復時請保留報告。擷取前請先建立上層目錄。

{{COMMAND:2}}

請用多個影格評估捲動或動畫，用 WAV 評估聲音。畫面上顯示完成數字，並不能證明預期聲道確實發聲。

### 13.4 儲存與恢復機器狀態

| 選項 | 用途與優先順序 |
| --- | --- |
| `--save-state out/checkpoint.kqs` | 在執行結束時儲存機器狀態。 |
| `--snapshot out/checkpoint.kqs` | 相同用途的狀態輸出，優先於 `--save-state`。 |
| `--load-state out/checkpoint.kqs` | 執行前載入 KQS 狀態。 |
| `--resume-state out/checkpoint.kqs` | 優先於 `--load-state`，也可覆寫工作中的輸入狀態。 |
| `--snapshot-at "frame=60&&frame_end=>out/frame60.kqs"` | 觀測條件符合時儲存。可重複指定多筆要求。若省略 `=>path`，會在目前目錄依 ROM 名稱產生帶編號的檔名。 |

請使用與 ROM 和模擬器版本相符的狀態。KQS 是機器狀態，不是卡匣存檔 RAM，也不是 C API 的 JSON 序列化資料。

{{COMMAND:3}}

### 13.5 觀察具名記憶體區域

| 選項 | 語法與用法 |
| --- | --- |
| `--symbols out/game.map` | 載入同一版編譯輸出的符號。 |
| `--source-map out/game.source_map.txt` | 將執行位置與原始碼位置對應。 |
| `--toolchain-metadata out/game.dbg2.json` | 載入結構化工具鏈中繼資料。ROM 旁相符的附屬檔也可能自動被偵測。 |
| `--watch-window "player:0xC700:16"` | 以 player 為標籤觀察從 0xC700 開始的 16 位元組。可重複指定不同區域；此功能觀察記憶體，本身不會停止執行。 |
| `--watch-baseline-mode initial` | 與初始值比較。`previous-frame` 比較相鄰影格；`named` 選用明確擷取的基準值。 |
| `--watch-baseline-tag ready` | 使用具名比較時，選擇基準名稱。 |
| `--capture-watch-baseline "ready=>frame=30&&frame_end"` | 條件符合時擷取具名基準。可重複指定其他基準。 |
| `--watch-fields preview,diff` | 選擇觀察欄位群組：`hash`、`activity`、`preview`、`baseline`、`diff`、`insights` 或 `all`。預覽位元組只有有限範圍，不是無上限的記憶體傾印。 |
| `--report-sections cpu,watched_memory` | 保留指定的報告區段。`meta` 與 `schema_version` 一律保留。未知名稱不會建立新區段。 |
| `--report-minimal cpu,watched_memory` | 另一個接受區段清單的選項，優先於 `--report-sections`。需要以逗號分隔的值，不是布林開關。 |

地址與大小接受十進位或帶 `0x` 的十六進位。請用目前建置的符號找出變數位置；以下 0xC700 只是範例地址，不是玩家資料的標準位置。

{{COMMAND:4}}

### 13.6 在執行條件或硬體事件發生時停止

| 選項 | 語法與用途 |
| --- | --- |
| `--breakpoint "pc:0x0150"` | 在 CPU 地址停止。`symbol:main` 使用符號；附加 `@bank:2` 可限制記憶體庫。 |
| `--watchpoint "player@0xC700+4"` | 在四位元組範圍發生記憶體寫入時停止。前面的名稱可省略；省略 `+size` 時只監看一位元組。 |
| `--stop-on-mmio "scroll@0xFF43"` | 寫入指定的 MMIO 暫存器時停止，此例為 SCX。 |
| `--stop-on-irq "vblank:serviced"` | 選擇中斷來源與階段：`requested`、`serviced`、`blocked` 或 `any`。只指定階段時，可符合任意來源。 |
| `--stop-on-dma oam_start` | 選擇 DMA 事件。接受的名稱為 `oam_start`、`oam_complete`、`hdma_start`、`hdma_block`、`hdma_complete`、`hdma_cancel`、`gdma_stall`、`hdma_deferred`、`hdma_ignored`。 |
| `--run-until "frame=60&&frame_end"` | 觀測條件的所有項目均符合時停止。可重複指定此選項以加入其他要求。 |

中斷點標記 `pc:`、`symbol:` 和 `@bank:` 區分大小寫。記憶體地址與記憶體庫可用十進位或帶 `0x` 的十六進位。即使指定了停止條件，也應保留影格上限，以免條件始終未發生。

觀測條件使用 `&&` 表示 AND，不是 C 運算式。支援的項目為 `frame=`、`ly=`、`pc=`、`bank=`、`bank_pc=bank:pc`、`symbol=`、`source=`、`event=`、`ppu_mode=`（或 `mode=`）以及 `basis=`。影格與 LY 值使用十進位。符號、來源與事件項目以文字比對。basis 值包含 `frame_start`、`frame_end`、`step`、`event`、`trace`、`snapshot`、`stop`；也接受單獨的 `frame_start`、`frame_end`、`stop`、`vblank`。`hp<10` 之類的比較不屬於此語法。

{{COMMAND:5}}

第一個命令用來檢查進入點，第二個用來找出改變水平捲動的程式碼。請確認要求的停止確實發生。

### 13.7 記錄觀測點並比較執行結果

| 選項 | 用途 |
| --- | --- |
| `--trace-point "frame=30&&frame_end"` | 條件符合時記錄觀測值。可重複指定多個觀測點。 |
| `--timeline-out out/timeline.jsonl` | 儲存觀測時間軸。 |
| `--trace-jsonl out/timeline.jsonl` | 另一種時間軸輸出目的地，優先於 `--timeline-out`。這不是要求追蹤每一條指令。 |
| `--timeline-format jsonl` | 選擇 `jsonl`（預設）或 `csv`；請自行搭配正確的副檔名。 |
| `--replay-interval 1` | 啟用重播檢查點，並選擇以影格計的間隔。 |
| `--replay-max-checkpoints 120` | 限制保留的檢查點數；重播預設保留 16 個，間隔為 1。 |
| `--rewind-on-stop-frames 10` | 要求停止後利用保留的重播歷史倒回。 |
| `--stop-on-divergence` | 啟用重播控制器在結果分歧時停止的行為。 |
| `--dump-replay-tape out/baseline.json` | 匯出已記錄的重播資料；須先啟用重播記錄。 |
| `--compare-replay-tape out/baseline.json` | 與匯出的重播資料比較。請使用相同的 ROM、輸入與初始狀態，以便進行確定性的比較。 |
| `--compare-replay-watch-only` | 將比較限制在受觀察記憶體的觀測值，不將它視為整台機器的完整比較。 |
| `--snapshot-on-replay-mismatch out/mismatch` | 比較發現不一致時，指定調查用產物的檔名前綴。 |

{{COMMAND:6}}

請檢查報告中的比較結果與第一個不一致處。僅產生兩個檔案不代表比較通過。

### 13.8 診斷與可重現的調查

| 選項 | 實際行為 |
| --- | --- |
| `--emit-diagnostics out/events.jsonl` | 匯出供 SARAKURA 使用的診斷事件。 |
| `--diagnostics-jsonl out/events.jsonl` | 直接執行時的另一個診斷輸出目的地；`--emit-diagnostics` 優先。 |
| `--repro-bundle out/repro.zip` | 將報告、診斷事件與清單打包。ROM 和中繼資料以路徑參照，不嵌入套件；畫面、狀態與追蹤資料不會自動納入。 |
| `--break-on-diagnostic all` | 比對最終報告中的診斷，以擷取調查資料。這**不會**在第一條出問題的指令處停止 CPU。只要篩選器非空，任一最終診斷都可能進入擷取流程。 |
| `--png-on-diagnostic out/diagnostic-images` | 診斷擷取時儲存最終畫面的目錄；檔名為 `diagnostic_000001.png`。 |
| `--snapshot-on-diagnostic out/diagnostic-states` | 儲存 `diagnostic_000001.kqs` 的目錄。擷取反映目前的最終狀態，而非各事件原本發生的瞬間。 |
| `--diagnostic-pack NAME` | 接受此參數，但執行路徑不會套用診斷套件。 |
| `--diagnostic-rule RULE` | 可重複指定的參數，但執行路徑不會套用所選規則。 |
| `--diagnostic-summary-limit N` | 接受此參數，但執行路徑不會套用此摘要上限。 |

{{COMMAND:7}}

若要在特定指令或寫入動作處停止，請使用 13.6 節的除錯器選項。閱讀診斷時須考慮情境：刻意保持閒置的標題畫面也可能產生觀測結果，不一定是遊戲缺陷。

### 13.9 反組譯指令或檢查虛擬碼

| 選項 | 語法與用途 |
| --- | --- |
| `--disassemble-out out/code.txt` | 解碼 ROM 指令，不執行一般模擬工作。 |
| `--disassemble-range "0:0100-0150"` | 選擇 `BANK:START-END`；可重複指定其他範圍。**三個數字一律為十六進位**，即使沒有 `0x` 也相同。 |
| `--disassemble-format text` | `text`（預設）、`markdown` 或 `json`。 |
| `--decompile-out out/functions.json` | 產生虛擬碼與控制流程資訊。 |
| `--decompile-format json` | `json`（預設）、`markdown` 或 `text`。 |
| `--decompile-function main` | 選擇函式；可重複指定更多函式。相符的符號有助於識別。 |
| `--decompile-all` | 納入反編譯器已知的所有具名函式。 |
| `--decompile-annotations out/annotations.json` | 讀取反編譯器 JSON 格式的註解資料。 |
| `--decompile-trace out/trace.json` | 讀取反編譯器追蹤中繼資料；任意 JSONL 診斷日誌不能代替它。 |

{{COMMAND:8}}

反組譯有助於檢查產生的指令，虛擬碼有助於理解控制流程；兩者都無法精確還原原始 C 程式。請保留同一次 ROM 建置產生的符號與中繼資料。

### 13.10 執行多台連線機器

| 選項 | 語法與用途 |
| --- | --- |
| `--link-job out/pair.json` | 從 JSON 連線工作讀取拓樸與工作階段；相對路徑以工作目錄為基準。 |
| `--link-topology pair` | 為命令列直接指定的工作階段選擇 `pair`、`four_player_adapter` 或 `dmg07`。 |
| `--link-session SPEC` | 加入一個工作階段。至少需要兩個。在 PowerShell 中，請用引號括住以豎線分隔的完整字串。 |
| `--link-initial-peer-slot 1` | 拓樸支援選擇對端時，指定初始對端。 |

工作階段欄位包含 `name`、`slot`、`rom`、`symbols`、`source_map`、`toolchain_metadata`、`load_state`、`save_state`、`input`、`input_sequence`、`audio_buffer_frames` 和 `watch_window`；其中 `rom` 為必填。觀察欄位可包含以逗號分隔的多個區域，例如 `a:0xC700:4,b:0xC710:4`。請使用確實交換序列資料的程式；兩個畫面都在執行，並不能單獨證明通訊成功。
