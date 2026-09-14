## 1. KITAQFC 與 GB 編譯器的關係
KITAQFC 使用 KITAQGB 的前端，為 NES／FC 的 6502 系列 CPU 產生程式碼。它不會把 GB ROM 轉成 NES ROM；程式仍須依目標機器的畫面、聲音、記憶體與 mapper 設計。

紀錄中的檢查已執行結構複製和一般函式呼叫範例，但 **NES 的 do-while 與 switch 會回報不支援的程式碼產生錯誤**。剖析器能辨識語法，不足以證明該語法可用於這個目標。

## 2. 開發環境與建置
{{CODE:0}}

安裝 .NET Framework 4.8 Developer Pack 及 Visual Studio Build Tools，使用 Developer PowerShell。後續命令採用複製到 `kitaqfc` 儲存庫的執行檔；若位置不同，請調整路徑。CHR 圖像與 C 原始碼是不同輸入。手冊的 `font.chr` 是由作者 `ascii.c` 轉成的 8 KiB 檔案。

## 3. 第一個程式
{{CODE:1}}

{{CODE:2}}

範例顯示 HELLO WORLD 和 042。`m_wait` 提交 VRAM 佇列、等待 NMI，再還原捲動畫面的位置。透過 PPUADDR 傳輸會影響內部捲動狀態，若漏掉還原，文字可能偏向邊緣。請熟悉「關閉顯示、準備素材、開啟顯示、與 NMI 同步」的順序。

## 4. 語言入門
GB 卷的敘述與運算式是共同基礎。FC 接受 `unsigned char`、`unsigned short`；`core.h` 定義 `u8`、`u16`、`s8`、`s16`，`fc.h` 是統整用標頭。這裡可使用無引數入口 `void main(void)`。

{{CODE:3}}

整數應在 8 或 16 位元範圍內使用，陣列索引從 0 開始。`fc_aggregate.c` 示範函式、指標、結構，`fc_arithmetic.c` 示範算術，`fc_control.c` 示範迴圈。不要加入 CGB 暫存器或 GB 專用內建函式。

## 5. 改寫不支援的結構
{{CODE:4}}

要取代 do-while，可先執行一次迴圈主體再判斷離開條件。簡單 switch 分派可改為 if/else 串接。上方只是說明片段，須自行提供 `update` 和狀態函式；完整 ROM 範例請使用 `fc_control.c`。

不要假設遞迴、間接函式呼叫和可變引數具有桌面環境的支援程度。目前部分 scene/entity 回呼介面只儲存函式指標，不會間接呼叫。

## 6. 記憶體與 PPU
NES CPU 內部 RAM 位於 0x0000～0x07FF；0x0800 以上的鏡射區域不是額外 RAM。6502 堆疊使用第 1 頁，OAM 影子緩衝區與佇列也會保留其他區域。`--nes-local-ram=START:LENGTH`、`--nes-temp-ram=START:LENGTH` 是需要檢查配置的進階設定。

PPU 有獨立位址空間。CHR 提供圖樣，名稱表安排圖塊，屬性表選擇調色盤群組，調色盤存放色彩編號。背景屬性通常套用至 16×16 像素區域，與 GB 圖塊屬性不同。

## 7. NMI 與 VRAM 佇列
NMI 是與顯示影格邊界相關的中斷。顯示期間直接大量寫入 PPU，可能破壞畫面。初始化應在關閉顯示時直接完成；平常更新則用 `__vramq_put`、`__vramq_copy`、`__vramq_fill` 並提交佇列。

{{CODE:5}}

檢查佇列容量和來源資料的生命週期。預設 NMI 會處理佇列。自行編寫 `__nes_nmi` 時，須保留必要的佇列執行、OAM 工作和暫存器保存。

## 8. Mapper 與 ROM 配置
| 選項 | 常見入門用途 |
| --- | --- |
| nrom | 小型固定 ROM 教學程式 |
| uxrom / cnrom / axrom | 簡單 PRG 或 CHR 切換 |
| mmc1 / mmc3 / mmc5 | 大型程式與 mapper 專屬功能 |
| vrc6 / vrc7 / fme7 | 分頁及相應擴充功能 |
| fds | 磁碟映像檔輸出 |

這些是編譯器選項，不是硬體或模擬器的完成度表。`--board=surom512` 選擇特定 MMC1 電路板配置；只把檔案填充到 512 KiB，並不會建立該配置。請搭配 KUROSAKI 的電路板檢查。

{{CODE:6}}

確認 `--battery` / `--no-battery`、CHR 容量、PRG 配置與跨 bank 呼叫符合電路板要求。變更 mapper 或鏡射方式後，除了產生 ROM，也要測試啟動、捲動和資料切換。

## 9. FDS、擴充音源與周邊
FDS 涉及磁碟檔案配置、啟動、覆疊載入及儲存。請參閱 `fds_manifest_sample.json` 與 FDS 標頭。執行所需的 BIOS 必須自行準備，公開套件不含 BIOS。

呼叫 VRC6 或 VRC7 音源操作不會變更 ROM 的 mapper 設定，兩者必須搭配。周邊裝置應分別驗證輸入值、連線狀態，以及對一般控制器讀取路徑的影響。

## 10. 診斷與建置結果
KQ 診斷和 `symfind`、`src2asm`、`romdiff` 等開發命令與 GB 類似，但繼承的 GB 說明選項未必都對應已實作的 NES 功能。FC 辭典另外從 FC 原始碼與標頭收集。

即使是關閉顯示時的初始化，也可能出現直接 PPU 操作警告，例如 KQ2421。不要為了消除警告而破壞安全初始化；應檢查顯示時序和執行日誌。「沒有錯誤」與「沒有警告」是兩種結果。

## 目錄調整後的原始碼位置
編譯器原始碼現位於各儲存庫的同名子目錄。API 參考保留 9 月 12 日的歷史路徑。對照請看[目錄調整說明](../GITHUB_SETUP.md)，根目錄執行檔與函式庫路徑不變。
