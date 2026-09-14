# 使用 KITAQGB、KOKURA 與 SARAKURA 開發遊戲

填寫需求後，將本文完整交給 AI。命令假設 `kitaqgb`、`kitaqfc`、`kokura`、`kurosaki`、`sarakura`、`kitaq-docs` 儲存庫與 `game-gb` 或 `game-fc` 專案位於同一個上層目錄。請從該目錄執行，並依實際環境調整路徑。

## 需求

- 遊戲名稱：<填寫>
- 類型與核心玩法：<填寫>
- 操作方式及成功、失敗條件：<填寫>
- 必備畫面、關卡、敵人與道具：<填寫>
- 美術風格、背景音樂與音效：<填寫，並註明提供素材的路徑>
- 存檔、通訊、周邊設備及其他需求：<填寫，或無>
- 專案目錄：<填寫>
- 再散布條件：<例如，自行撰寫的程式與原創素材可採 MIT 授權公開>

- 目標機型：<初代 Game Boy / 同時支援 GB 與 CGB / CGB 專用>
- 效能目標：<例如，一般遊玩時每秒更新遊戲邏輯 60 次；註明高負載場景可接受的表現>

## 請執行的工作

請以 KITAQGB 及其函式庫實作遊戲。使用 KOKURA 執行與除錯，使用 SARAKURA 整理診斷並比較修正前後的結果。

持續重複以下流程，直到符合驗收標準：具體化規格 → 實作小幅變更 → 建置 → 輸入操作並觀察 → 調查原因 → 修正 → 在相同條件下重新驗證。不可只因提出計畫、提供程式碼或編譯成功，就認定工作完成。

### 確認環境與驗收標準

1. 閱讀工作目錄的指示、各工具 README、HTML 手冊，以及所用函式庫的標頭檔和實作。記錄執行檔路徑及版本或 SHA-256；以實際 `--help` 輸出確認命令，以原始碼確認 API。
2. 為輸入、畫面、聲音、遊戲流程和更新頻率訂出可判定的驗收標準。例如，按下再放開 START 後開始遊戲；碰撞減少一條命；暫停時指定聲音靜音，繼續後恢復播放。
3. 只針對重要的模糊需求提問，一般可復原的實作決策請自主處理。不得自行降低需求或驗收標準。
4. 先用隨附的小範例串接編譯器、模擬器與 SARAKURA。這只能確認工具銜接，不能代表所需遊戲已完成。

### 先完成可玩的最小流程

- 使用 KITAQGB 的 C 方言與 `void main()`。不要假定桌面 C 或 GBDK API 能直接使用。除了宣告，也要把必要的 `.c` 實作納入建置；確認初始化順序、單位、正負號、範圍、緩衝區生命週期及 ROM 分頁。
- 規劃 VRAM/OAM 更新、VBlank、中斷、堆疊、ROM/WRAM 分頁，以及圖塊與精靈數量限制。傳輸佇列的總容量、剩餘容量，與實體 VRAM 的容量、可用空間是不同概念。
- DMG 遊戲不得依賴 CGB 專用功能。若支援兩者，請分別驗證各硬體模式。
- 英文字母、數字與符號使用提供的原創 `ascii.c` 字型，並確認字元與圖塊的對應關係。

- 先串起開機、標題畫面、可操控角色、成功或失敗與重新開始，再擴充內容。
- 保留可編輯的圖形、音樂、音效原始檔及產生步驟，並確認建置確實讀取匯出的資料。
- 原始碼註解使用英文，進度報告使用繁體中文。SARAKURA 的標準報告維持英文。

### 對應每次建置與執行結果

以 `out/iter-001` 等目錄區分每輪輸出。記錄命令、結束碼，以及原始碼、素材、工具、ROM、中繼資料的雜湊值。建置失敗後，不可執行殘留的舊 ROM。配置映射、原始碼映射與除錯資訊必須和 ROM 來自同一次建置。

以下是基本的 DMG 檢查範例。請準備 `main.c` 和必要的函式庫實作檔，並依遊戲調整選項及輸入序列。

```powershell
$iteration = '.\game-gb\out\iter-001'
New-Item -ItemType Directory -Force $iteration | Out-Null

# Include all additional implementation units required by the game.
& '.\kitaqgb\kitaqgb.exe' '.\game-gb\src\main.c' `
  -I '.\kitaqgb\lib' -o "$iteration\game.gb" `
  --profile=dev --rst-disable --stack-bank=fixed --no-disasm `
  "--emit-ai-metadata=$iteration\build.json"
if ($LASTEXITCODE -ne 0) { throw 'Build failed; inspect the build log.' }

# This sequence presses START once, with released intervals on both sides.
& '.\kokura\kokura-cli.exe' "$iteration\game.gb" `
  --hardware dmg --run-frames 300 `
  --input-seq 'NONE:60;START:1;NONE:239' `
  --png "$iteration\frame.png" --record-wav "$iteration\audio.wav" `
  --dump-report "$iteration\run.json" `
  --emit-diagnostics "$iteration\events.jsonl"
if ($LASTEXITCODE -ne 0) { throw 'Emulator run failed; inspect the run log.' }

& '.\sarakura\sarakura.exe' gb analyze `
  --metadata "$iteration\build.json" --events "$iteration\events.jsonl" `
  --frames 300 --out "$iteration\analysis" --fail-on error
if ($LASTEXITCODE -ne 0) { throw 'Inspect the analysis report and fix the cause.' }
```


`--hardware dmg` 選用初代 GB。測試 CGB 或雙機型支援時，應讓 ROM 標頭與模擬器機型設定一致。範例輸入在兩段放開按鈕的時間之間按一次 START。執行 300 影格不代表測試完整個遊戲。

### 檢查畫面、聲音、狀態與效能

- 保存輸入情境，區分按下、按住與放開。走過規格中的全部路徑：開機、開始、移動、動作、碰撞、捲動、關卡切換、遊戲結束、重新開始、暫停，以及適用的存檔與通訊。
- 保留關鍵影格 PNG、輸入資料、執行報告、診斷 JSONL、WAV 和必要的狀態、記憶體觀測。確認實際到達的影格數與停止原因。務必開啟圖片查看；一張截圖無法證明移動或輸入反應。將計數器、座標與狀態變化和預期值比對，也要檢查畫面邊緣、圖塊與屬性邊界及精靈密集情境。
- 檢查音樂、音效、同時發聲、斷音、暫停與恢復。僅產生 WAV 不能證明聲音正確。無法試聽時，請區分已執行的波形、數值檢查與尚未確認的聽感。
- 測量高負載場景的目標 CPU 工作量、遊戲更新與傳輸量；FC 還要計入 NMI 工作。主機上模擬器的執行速度不等於遊戲更新頻率，也不能證明實機速度。使用 `--allow-unimplemented` 後能繼續執行，不代表未實作功能已受支援。

### 分析、修正並重新驗證

- 將待測 ROM 的建置中繼資料與該次執行的診斷 JSONL 交給 SARAKURA。CPU 追蹤或一般執行報告不能取代它。`--frames` 指定分析條件；SARAKURA 不會執行 ROM，也不會自動修改原始碼。
- 閱讀 `report.html`、`ai_diagnostics.json`、`repair_prompt.md`、`retest_plan.json`，並與重現步驟、畫面、聲音及原始碼核對。區分推測的位置、原因與已確認事實，也要區分正常等待迴圈與當機。逐項判讀警告，記錄未支援事件與分析限制。不可透過隱藏警告或縮短測試來取得通過結果。
- 將問題縮減成最小重現案例，修正原因後重新建置。若根源在編譯器或模擬器，應與遊戲程式問題分開確認，並為工具修正加入回歸驗證。
- 重新驗證時，保持輸入、亂數種子、機型與影像制式、Mapper、觀測影格及診斷設定一致。新 ROM 使用相符的中繼資料；程式或 RAM 配置變更後，不可直接沿用即時存檔。

```powershell
& '.\sarakura\sarakura.exe' baseline-delta `
  --baseline '.\game-gb\out\iter-001\analysis' `
  --current '.\game-gb\out\iter-002\analysis' `
  --out '.\game-gb\out\delta.json' --markdown '.\game-gb\out\delta.md' `
  --fail-on-new error --fail-on-regression error --enforce
```


診斷差異應搭配操作、畫面與聲音的驗收結果判斷。相同失敗反覆發生時，請重新檢視證據與假設，不要漫無根據地繼續修改。

### 完成條件與交付內容

以交付的原始碼與設定建置最終 ROM，再執行所有必要情境。僅使用無敵狀態、自動測試輸入或另一種 Mapper，無法驗證最終版本的正常遊玩。提供需求與測試對照表，說明剩餘警告的原因，明列未驗證、未支援項目。未做實機測試時，請標註「實機未驗證」。

交付原始碼、工具與函式庫識別資訊、可編輯素材、可重現的建置與測試指令稿、ROM、最終驗證證據，以及說明安裝、操作與已知限制的 README。視需要附上重播資料和測試驅動程式。只在明確授權範圍內公開或對外傳送檔案。驗證後刪除不必要的中間建置與暫存追蹤，但保留原始碼、素材、最終成果及必要的回歸證據。

若環境或權限阻礙必要檢查，請回報確切的重現步驟與所需處理，不得標記為完成。
