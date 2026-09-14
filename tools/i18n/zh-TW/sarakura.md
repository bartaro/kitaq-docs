## 已建置的 Windows CLI
儲存庫根目錄提供 Windows x64 版 `sarakura.exe`。下載 ZIP 時請一併保留授權聲明。執行無須 Rust、Python 或 .NET；以下步驟用於從原始碼重新建置。獨立專案程式碼由 DAISUKE OBA 以 MIT 授權提供，相依條件保留於 `BINARY_NOTICES.md` 和 `licenses/`。

## 1. SARAKURA 負責什麼
SARAKURA 結合編譯器建置資訊與模擬器診斷事件，整理成有助修復和複測的資料。它不是執行 ROM 的模擬器，也不會默默改動你的 C 原始碼。

## 2. 建置工具
{{CODE:0}}

簡寫 `sarakura` 假設已加入 PATH；否則請使用執行檔路徑。GB 選擇 `gb analyze`，FC 選擇 `fc analyze`。

## 3. 第一次分析
需要兩類輸入：`--metadata` 是建置時 JSON，`--events` 是執行時診斷 JSONL。JSONL 每行放一個 JSON 物件。

{{CODE:1}}

在瀏覽器開啟輸出的 `report.html`。讀取個別診斷前，先確認目標、觀察影格數、錯誤數和警告數。`--frames` 描述分析條件，不是要求 SARAKURA 執行那麼多影格的 ROM。

## 4. 先檢查輸入
{{CODE:2}}

調查遊戲行為前，先分清楚檔案無法讀取、平台不符、事件類型不支援等問題。把一般模擬器報告當成事件檔傳入，不會使它變成有效診斷輸入。

## 5. 解讀診斷
error 值得優先調查，warning 是否有問題視情境而定，info 則提供背景。嚴重程度有助安排優先順序，但無法完全理解遊戲意圖。例如只看重複 PC，未必能區分正常標題等待迴圈和當機。

請搭配 ROM 雜湊、輸入序列、場景、畫面、聲音與原始碼位置判斷。修復前後條件應相同，否則診斷變少可能只是換了場景。

## 6. 輸出檔案
內建說明、診斷提示與修復指引採英文，HTML 宣告 `lang="en"`。使用者字串和事件 ID 不會自動翻譯。預設遮蔽處理會替換部分專案標籤及路徑，但不保證匿名化所有位址或觀察內容。公開私有輸入的分析結果前，請檢查報告。

| 檔案 | 用途 |
| --- | --- |
| ai_diagnostics.json | 自動處理用的正規化診斷 |
| diagnostic_summary.json | 數量統計與摘要 |
| report.html | 適合閱讀的報告 |
| repair_prompt.md | 開始修復調查所需的背景 |
| repair_plan.json / .md | 修復順序與對象 |
| automation_plan.json / .md | 依工具能力安排的工作計畫 |
| retest_plan.json | 複測計畫 |
| repro_bundle.zip | 重現資料包 |

產生計畫不等於執行計畫。修改 C 原始碼或 ROM 後，須重新執行編譯器、模擬器與 SARAKURA。

## 7. 規則目錄、篩選與涵蓋情況
{{CODE:3}}

`catalog` 列出診斷規則，`pack-plan` 依領域分組，`coverage` 檢查對應事件是否曾被觀察到。目錄中有規則，不保證目前模擬器會產生該事件。

{{CODE:4}}

`--diagnostic-rule` 選擇事件名稱或規則 ID，`--phase` 選階段，`--diagnostic-pack` 選領域。篩掉診斷不等於解決問題。

## 8. 比較修改前後
{{CODE:5}}

結果分為新增、已解決、改善、持續存在和退步。請區分原有問題與新引入問題。比較時固定輸入、影格數及診斷篩選條件。

## 9. 格式驗證與 CI
{{CODE:6}}

持續整合會自動執行可重現的檢查。`ci-summary` 只有加上 `--enforce` 才改變程序結束碼，否則需讀取 JSON 判定。analyze 的 `--fail-on error` 在有錯誤時傳回非零結束碼；預設 `never` 不會因診斷而失敗，因此 CI 要明確選擇政策。選擇 `warn` 時，警告也會觸發失敗。

```powershell
sarakura ci-summary --diagnostics .\out\report --fail-on error --enforce
if ($LASTEXITCODE -ne 0) { throw "The diagnostic failure condition was met" }
```

結構描述驗證成功，只確認了資料格式。遊戲是否符合設計，仍需要輸入、畫面和聲音測試。

## 10. 處理重現資料
`normalize-events` 正規化事件紀錄，`inspect-repro` 檢查重現包。分享前請確認資料屬於目標 ROM，且包含必要輸入步驟。`--allow-project-labels` 會明確保留專案衍生標籤與識別碼。

## 11. 最小練習輸入
手冊附有小型 GB／FC 建置中繼資料與事件範例。可開啟 [GB 合成報告](verification/sarakura-gb-synthetic.html)或 [FC 合成報告](verification/sarakura-fc-synthetic.html)。`samples/sarakura_demo.ps1` 示範分析流程。這些是為學習格式而構造的輸入，不是從真實 ROM 擷取的證據；實測應使用 KOKURA 或 KUROSAKI 記錄的事件。

## 12. 一次修復與複測循環
1. 以同一 ROM 和輸入重現問題，保留日誌與畫面。
2. 用 SARAKURA 整理候選原因，閱讀相關原始碼。
3. 針對原因做集中修改。
4. 重新建置並執行相同操作。
5. 將 baseline-delta 與圖像、聲音、遊戲行為一起比較。

每輪維持小範圍，才能清楚理解各項修改與結果的關係。
