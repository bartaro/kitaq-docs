## 已建置的 Windows CLI
儲存庫根目錄包含 `kokura-cli.exe`。下載 ZIP 後，請將授權聲明與執行檔一起保留。這個 Windows x64 CLI 執行時不必安裝 Rust、Python 或 .NET。以下建置步驟用於從原始碼重新產生程式。獨立專案程式碼由 DAISUKE OBA 以 MIT 授權提供；相依套件條件保留於 `BINARY_NOTICES.md` 和 `licenses/`。

## 1. KOKURA 的用途
KOKURA 模擬 GB/CGB 軟體，記錄圖像、音訊、CPU 執行、記憶體、bank、輸入與診斷事件。命令列工具的執行檔為 `kokura-cli.exe`。

## 2. 建置並執行第一個 ROM
{{CODE:0}}

安裝 Rust 和 Cargo。只需 CLI 時，建置指定 crate 即可。先使用第 1 卷的 hello ROM。預設只執行一個影格，請用 `--run-frames` 指定到達目標場景所需的影格數。這是模擬影格數，不是實際等待秒數。

## 3. 選擇 DMG 或 CGB
`--hardware auto` 是預設值，也能明確選擇 `dmg` 或 `cgb`。雙模式 ROM 應在兩種模式下測試。CGB 專用 ROM 拒絕以 DMG 啟動，本身不代表模擬器故障。

{{CODE:1}}

## 4. 提供輸入
`--input` 持續按住同時輸入的按鈕組合，`--input-seq` 則依時間給出輸入序列。按鈕名稱是 `A,B,START,SELECT,UP,DOWN,LEFT,RIGHT`；放開區段使用 `NONE`。PowerShell 中含分號的序列須加引號。

{{CODE:2}}

測試「新按下」時要包含放開的區段。按住 A 120 個影格，與按 A 120 次不同。輸入計數課程中，上述序列應只增加一次計數。

## 5. 圖像、影片與音訊
`--png` 儲存最後畫面；`--screenshot` 配合 `--screenshot-frames` 擷取指定影格；`--record-video` 錄製影片，`--record-wav` 錄製音訊。不使用 APU 的 hello 程式產生無聲 WAV，是正常結果。

{{CODE:3}}

範圍寫成 `start:end`。保留報告，才能區分載入狀態的累計影格編號和本次執行位置。是否有聲音、音高、斷音與削波應分別檢查。模擬器錄音無法證明與實機逐取樣一致。

## 6. 儲存與恢復狀態
{{CODE:4}}

通常應使用相同 ROM 和模擬器版本。模擬器狀態不同於遊戲本身的存檔；CLI 的 KQS 和 C API 的 JSON 狀態也不是同一格式，改副檔名無法互換。

## 7. 觀察符號與記憶體
ROM 旁的 `.map`、`.source_map.txt`、`.dbg2.json`、`.build_report.json` 可自動辨識。請保留與 ROM 同次建置的輔助檔案，其他建置的資料可能誤導觀察。

{{CODE:5}}

`wram` 是觀察視窗名稱，0xC000 是起始位址，0x40 是長度。較小的視窗有助於找出變動的變數。`--watch-baseline-mode` 選擇與初始值、上一個影格或具名基準比較。

## 8. 停止條件、重播與逆向分析
`--breakpoint`、`--watchpoint`、`--run-until`、`--snapshot-at` 依條件停止或儲存。各選項的參數語法不同，請查看下方參考及實際說明輸出。

{{CODE:6}}

先找出第一次分歧，再縮小到附近區間。`--decompile-out` 產生虛擬碼和控制流程資訊，`--disassemble-out` 顯示 CPU 指令。反編譯無法完整還原原始 C 程式碼或變數名稱。

## 9. 將診斷交給 SARAKURA
{{CODE:7}}

KOKURA 的 `--emit-diagnostics` 接收 **JSONL 檔名**，例如 `out/gb_events.jsonl`。一般執行報告 JSON、CPU 追蹤 JSONL 都不等於診斷事件輸入。

## 10. 通訊工作
`pair` 模擬兩台機器；`four_player_adapter` 是由主機選擇通訊對象的邏輯結構；`dmg07` 模擬實體 DMG-07 協定。使用 `--link-job` 傳入工作 JSON，或以 `--link-topology`、`--link-session` 設定工作階段。

{{CODE:8}}

各 ROM 必須實作通訊。執行兩個一般 hello 程式，不算是通訊函式庫測試。請記錄各階段的 ROM、槽位、輸入與狀態，並註明哪些實際裝置行為尚未驗證。

## 11. 外部應用程式整合
公開 C ABI 位於 `kokura-capi`；Python 可透過提供的橋接程式和 Python crate 存取。調查整合行為前，先建立最小 CLI 重現步驟。

## 12. 依順序閱讀報告
先確認執行影格數和停止原因，再檢查畫面、輸入結果、聲音、錯誤與警告，最後看效能剖析。沒有輸入而長時間停在標題畫面，可能自然產生靜止畫面或重複 PC 警告。請依預期場景判斷，不要將每條警告一律視為故障。
