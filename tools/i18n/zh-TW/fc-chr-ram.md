### 8.1 使用 CHR RAM 更新圖形

`--nes-chr-ram` 會建置使用 8 KiB 可寫入 CHR RAM 的卡匣 ROM。ROM 檔案不儲存 CHR 資料，因此程式必須在初始化時將圖塊圖樣上傳至 PPU。`wire3d.c` 繪圖器使用此模式。

{{BUILD}}

`--nes-chr=tiles.chr` 或 `--chr-rom=tiles.chr` 會將準備好的圖樣納入 CHR ROM。這兩個選項都不能與 `--nes-chr-ram` 同時使用。CNROM 設定也不接受 CHR RAM 模式。請確認目標映射器與電路板具備所需的 CHR RAM。

省略所有 CHR 選項時，編譯器會加入空白的 8 KiB CHR ROM。執行期間上傳圖樣的範例，必須明確指定 `--nes-chr-ram`。CHR RAM 與 CPU 端的 PRG RAM 是不同的記憶體；線框繪圖的暫存緩衝區也需要另外配置 PRG RAM。
