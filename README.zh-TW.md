# KITAQ SERIES 手冊

[English](README.md#english) | [日本語](README.md#japanese) | **繁體中文**

## 直接開啟各工具手冊

以下連結會直接開啟對應工具的繁體中文分冊。

| 分冊 | 內容 |
| --- | --- |
| [KITAQGB](https://bartaro.github.io/kitaq-docs/zh-TW/kitaqgb.html) | Game Boy 語法、內建操作與建置。 |
| [KITAQGB 程式庫](https://bartaro.github.io/kitaq-docs/zh-TW/gb-library.html) | Game Boy 支援程式庫。 |
| [KOKURA](https://bartaro.github.io/kitaq-docs/zh-TW/kokura.html) | 執行、輸入、觀察與記錄。 |
| [KITAQFC](https://bartaro.github.io/kitaq-docs/zh-TW/kitaqfc.html) | Famicom／NES 語法、內建操作與建置。 |
| [KITAQFC 程式庫](https://bartaro.github.io/kitaq-docs/zh-TW/fc-library.html) | Famicom／NES 支援程式庫。 |
| [KUROSAKI](https://bartaro.github.io/kitaq-docs/zh-TW/kurosaki.html) | 執行、儲存與分析。 |
| [SARAKURA](https://bartaro.github.io/kitaq-docs/zh-TW/sarakura.html) | 診斷與重新測試。 |
| [驗證紀錄](https://bartaro.github.io/kitaq-docs/zh-TW/verification.html) | 實際建置、執行與影像比較結果。 |

## HTML 手冊

七冊正文提供九種語言版本，原始碼說明已更新至 2026 年 9 月 14 日。各語言版均收錄相同的 1,053 個 API 項目與 47 個完整範例程式。本機閱讀時，繁體中文版請開啟 `zh-TW/index.html`，英文版開啟 `en/index.html`，日文版開啟 `index.html`。各分冊均可切換語言。保留的歷史建置與執行紀錄只對應當時的版本；更新原始碼說明不代表已重新完成這些測試。

原始碼摘錄與實際擷取的工具輸出保持原文。另請參閱[儲存庫取得方式與目錄配置](GITHUB_SETUP.md)及[發行檢查紀錄](PUBLICATION_CHECKS.md)。HTML 支援離線閱讀、冊內搜尋、複製程式碼與列印。

總目錄與第一冊開頭說明 KITAQGB 名稱的雙重意義，並向 NORCAL 致謝。英文字母、數字和符號使用指定的 `samples/assets/ascii.c`。GB 素材依 ASCII 順序重新排列，FC 素材則轉為 NES 位元平面格式，字形本身不作修改。

正文、補充範例與產生工具採用 MIT 授權條款。作者已於 2026 年 9 月 12 日確認，所提供的 92 個字形為自行創作，可依 MIT 授權公開。摘錄自原軟體的內容保留其著作權聲明。再散布時，請一併附上[第三方聲明](THIRD_PARTY_NOTICES.md)及適用的授權條款。

手冊包含[英文授權原文](LICENSE)與[日文參考譯文](LICENSE.ja)。[第三方聲明](THIRD_PARTY_NOTICES.md)亦連結至各工具的日文授權條款；譯文若與原文有差異，以英文原文為準。軟體二進位檔發行仍須遵守各相依項目的授權。手冊可公開，並不表示所有工具與相依項目都能僅依 MIT 條款再散布。

## 建置範例

請將各儲存庫複製到同一個上層目錄，形成同層級目錄，再從該上層目錄執行以下指令。配置方式見 [GITHUB_SETUP.md](GITHUB_SETUP.md)。可使用隨附編譯器，也可依手冊自行建置；本版包含編譯器修正。

```powershell
.\kitaq-docs\samples\build.ps1 -Only gb_hello,fc_hello
.\kitaq-docs\samples\build.ps1
```

若原始碼位於其他位置，請指定 `-Root "原始碼樹的絕對路徑"`。可用 `-GbCompiler` 與 `-FcCompiler` 選擇其他目錄中的編譯器。ROM 與紀錄檔預設輸出至 `samples/out/<sample-id>`。本手冊套件不包含編譯器執行檔、商業 ROM 或 BIOS。

`samples/api-fragments` 是程式碼片段，須放入已完成初始化的程式，並提供有效參數後才能使用。ROM 批次建置涵蓋 `samples/manifest.json` 中的 47 個完整程式。各冊會明確標示僅有宣告的 API、未執行的片段與尚未在實機驗證的功能。

## 發佈至 GitHub

1. 將本目錄內容放在儲存庫根目錄或 `docs` 目錄。
2. 一併上傳 `index.html`、七冊正文、`verification.html`、語言目錄、`assets`、`samples`、`reference`、`verification`、README 與授權聲明，並保留 `.nojekyll`。
3. 在 GitHub 的 Settings → Pages → Build and deployment，將 Source 設為 Deploy from a branch。
4. 選取已上傳的分支，以及符合目錄配置的 `/ (root)` 或 `/docs`，然後儲存。
5. 發佈完成後，開啟 Pages 顯示的網址，檢查總目錄與各分冊連結。

詳見 [GitHub 發佈來源設定說明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。`manual/_manual_work` 是本機建置與驗證工作區，不屬於發行內容。

## 編輯與更新

日文正文位於 `tools/chapters.py`，英文正文位於 `tools/en/*.md`。`tools/generate_en.py` 產生英文版，`tools/generate.py` 包含 API 字典與頁面產生邏輯，`assets/manual.css` 則定義樣式。使用 Python 更新手冊：

```powershell
python -B kitaq-docs/tools/collect.py
python -B kitaq-docs/tools/make_samples.py
python -B kitaq-docs/tools/catalog.py
python -B kitaq-docs/tools/generate.py
python -B kitaq-docs/tools/generate_en.py
foreach ($language in @('ko','zh-CN','zh-TW','es','pt','fr','de')) {
    python -B kitaq-docs/tools/generate_i18n.py --language $language
    if ($LASTEXITCODE -ne 0) { throw "Manual generation failed: $language" }
}
python -B kitaq-docs/tools/check_site.py
python -B kitaq-docs/tools/check_bilingual.py
```

收集原始碼與建置範例需要原始專案樹及對應工具。字型轉換與像素比較使用 Pillow。閱讀 HTML 不需要 Python 或伺服器。修改原始碼或執行檔後，不應將舊驗證結果當作新版本的證明。另請參閱[編譯器修正紀錄](verification/compiler_fixes.md)與[第三方聲明](THIRD_PARTY_NOTICES.md)。

## 本次原始碼公開範圍

KOKURA-GUI、KUROSAKI-GUI 與 PLITA 不在本次上傳範圍內。公開原始碼與手冊涵蓋命令列工具、核心及整合 API。
