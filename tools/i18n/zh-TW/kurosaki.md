## 已建置的 Windows CLI
儲存庫根目錄提供 `kurosaki.exe`。下載 ZIP 後，請將執行檔與授權聲明一同保存。Windows x64 CLI 執行時無須 Rust、Python 或 .NET；以下步驟用於從原始碼重新建置。獨立專案程式碼由 DAISUKE OBA 以 MIT 授權提供，相依條件見 `BINARY_NOTICES.md` 與 `licenses/`。

## 1. KUROSAKI 的用途
KUROSAKI 是能讀取 KITAQFC 資訊的 NES／FC／FDS 觀察型模擬器。CLI 可檢查 ROM、執行程式、錄音、診斷、保存快照、重播輸入、反組譯，以及反編譯候選函式。各 mapper 實作範圍不同，請先查看 ROM 與支援資訊。

## 2. 建置與啟動
{{CODE:0}}

以下簡寫 `kurosaki` 假設執行檔目錄已加入 PATH；否則請換成 `& "執行檔完整路徑"`。

{{CODE:1}}

使用第 4 卷的 hello ROM 驗證文字顯示。`inspect-rom` 檢查標頭，`run` 推進 CPU／PPU 執行。標頭檢查成功不代表程式能正常執行。

## 3. 檢查 mapper 與電路板
`mapper-list` 列出已註冊類型，`mapper-info` 說明特定類型，`audit-board` 檢查電路板限制。mapper 編號將 ROM 標頭與實體接線假設連結起來；只有名稱無法確定容量、CHR-RAM 或固定 bank 的行為。

{{CODE:2}}

`--allow-unimplemented` 允許遇到未實作部分後繼續觀察。使用此選項的執行結果，不能證明相關功能已受支援。

## 4. 控制器輸入
`run --pad1`、`--pad2` 使用 NES 原始位元遮罩：A=1、B=2、SELECT=4、START=8、UP=16、DOWN=32、LEFT=64、RIGHT=128。同時按鍵時將對應值相加。

{{CODE:3}}

上例持續按 A 120 個影格。標題、開始、確認等有順序的動作應使用重播。CLI `replay-record` 範例記錄沒有互動輸入的基準執行，不等同錄下人在 GUI 中的操作。

## 5. 快照與重播
{{CODE:4}}

可恢復的狀態使用第 2 版快照。請保持狀態與 ROM SHA-256 相符。`snapshot-resume` 從儲存點繼續；`snapshot-rebase` 依提供的相容性契約，明確將狀態移轉到另一個相容 ROM。更動程式碼或 RAM 配置後，不應無條件沿用舊狀態；通常應從啟動重新執行相同操作。

## 6. 追蹤、診斷與效能剖析
{{CODE:5}}

追蹤記錄事件順序，診斷指出符合規則的觀察，效能剖析呈現執行集中位置。異常附近的幾個影格，通常比冗長的完整紀錄更容易分析。

以 `--kitaqfc-debug` 傳入相符的建置除錯 JSON。缺少原始碼行號資訊的觀察，不能解讀為完整的原始碼逐行追蹤。

## 7. 儲存聲音與畫面
{{CODE:6}}

暫存器變化、PCM 產生與聲音實際正確，是三項不同檢查。測試內建或擴充音源時，請記錄 mapper。單張 PNG 無法證明移動或輸入行為，應同時保留前後狀態與輸入。

## 8. 反組譯與反編譯
{{CODE:7}}

`disasm` 輸出指令序列；`decompile` 輸出函式邊界候選、CFG、參照與虛擬碼。有可切換 bank 時，CPU 位址不足以確定 ROM 實體位置。必要時透過 `--snapshot` 提供 mapper 狀態，並以執行追蹤或註解佐證。這不是完整還原原始碼。

## 9. 連接 SARAKURA
{{CODE:8}}

KUROSAKI 的 `--emit-diagnostics` 與 KOKURA 一樣，接收 **JSONL 檔案路徑**。請區分 CPU 追蹤與診斷事件檔。

## 10. 公開範圍
KUROSAKI-GUI 尚未公開。目前手冊涵蓋 CLI 和整合 API。

## 11. FDS 與存檔 RAM
`fds-inspect` 檢查磁碟結構，`export-assets` 匯出素材。FDS 的啟動、BIOS、磁碟存取條件與 NES 卡匣不同，應另外測試。電池存檔 `.sav` 和 `.kss.json` 快照用途不同，須採用實作支援的儲存配置。

{{CODE:9}}

`battery-export` 從相符的 ROM 與快照擷取原始存檔 RAM；`battery-run` 載入該 RAM 並從開機開始，不恢復中斷時的 CPU／PPU 執行狀態。使用 `--save-out` 指定輸出。這些操作需要具有存檔 RAM 的受支援 ROM，不適用於所有教學 ROM。
