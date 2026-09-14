# KITAQ SERIES手册

[English](README.md#english) | [日本語](README.md#japanese) | **简体中文**

<!-- ai-prompts:start -->
## 生成式 AI 游戏开发提示词

填写需求后，将完整提示词交给 AI。内容涵盖实现、模拟器测试、SARAKURA 分析以及修复后的复测。

[KITAQGB](https://bartaro.github.io/kitaq-docs/zh-CN/loop-engineering.html#gb) · [KITAQFC](https://bartaro.github.io/kitaq-docs/zh-CN/loop-engineering.html#fc)
<!-- ai-prompts:end -->

## 直接打开各工具的手册

下列链接直接进入相应工具的简体中文分册。

| 分册 | 内容 |
| --- | --- |
| [KITAQGB](https://bartaro.github.io/kitaq-docs/zh-CN/kitaqgb.html) | Game Boy语法、内建操作与构建。 |
| [KITAQGB库](https://bartaro.github.io/kitaq-docs/zh-CN/gb-library.html) | Game Boy支持库。 |
| [KOKURA](https://bartaro.github.io/kitaq-docs/zh-CN/kokura.html) | 执行、输入、观察与记录。 |
| [KITAQFC](https://bartaro.github.io/kitaq-docs/zh-CN/kitaqfc.html) | Famicom/NES语法、内建操作与构建。 |
| [KITAQFC库](https://bartaro.github.io/kitaq-docs/zh-CN/fc-library.html) | Famicom/NES支持库。 |
| [KUROSAKI](https://bartaro.github.io/kitaq-docs/zh-CN/kurosaki.html) | 执行、保存与分析。 |
| [SARAKURA](https://bartaro.github.io/kitaq-docs/zh-CN/sarakura.html) | 诊断与复测。 |
| [验证记录](https://bartaro.github.io/kitaq-docs/zh-CN/verification.html) | 实际构建、运行及图像比较结果。 |

## HTML手册

本套手册以2026年9月14日的源码为依据，共七册，提供九种语言版本。各语言版均包含相同的1,053个API条目和47个完整示例程序。简体中文请打开 `zh-CN/index.html`，英文打开 `en/index.html`，日文打开 `index.html`。每册均可切换语言。验证记录列明了测试所用的源码、可执行文件和条件。

原始源码摘录和实际捕获的工具输出保持原文不变。另请参阅[仓库获取与目录布局](GITHUB_SETUP.md)及[发布检查记录](PUBLICATION_CHECKS.md)。HTML支持离线阅读、册内搜索、代码复制和打印。

总目录和第一册开头说明了KITAQGB名称的双重含义，并致谢NORCAL。英文字母、数字和符号使用指定的 `samples/assets/ascii.c`。GB资源按ASCII顺序重新排列，FC资源转换为NES位平面格式；字形不作修改。

正文、补充示例和生成工具采用MIT许可证。2026年9月12日，作者确认所提供的92个字形为原创作品，可以按MIT公开。来自原软件的摘录保留其著作权声明。再分发时请同时附上[第三方声明](THIRD_PARTY_NOTICES.md)及适用许可证。

手册包含[英文许可证原文](LICENSE)和[日文参考译文](LICENSE.ja)。[第三方声明](THIRD_PARTY_NOTICES.md)也链接了各工具的日文许可证。若译文与原文有差异，以英文原文为准。软件二进制发行还需遵守依赖项各自的许可证。允许公开这些手册，并不等于所有工具和依赖项都能仅按MIT再分发。

## 构建示例

将各仓库clone到同一个父目录下，使它们成为同级目录，然后从该父目录运行以下命令。布局详见 [GITHUB_SETUP.md](GITHUB_SETUP.md)。可使用所附编译器，也可按手册重新构建；本版包含编译器修复。

```powershell
.\kitaq-docs\samples\build.ps1 -Only gb_hello,fc_hello
.\kitaq-docs\samples\build.ps1
```

若源码位于其他位置，请指定 `-Root "源码树的绝对路径"`。可用 `-GbCompiler` 和 `-FcCompiler` 选择其他目录中的编译器。生成的ROM与日志默认放在 `samples/out/<sample-id>`。本手册包不包含编译器可执行文件、商业ROM或BIOS。

`samples/api-fragments` 是需要放入已完成初始化、并提供有效参数的程序中的代码片段。ROM批量构建覆盖 `samples/manifest.json` 中的47个完整程序。各册明确区分只有声明的API、未执行的片段和未在实机验证的功能。

## 发布到GitHub

1. 将本目录内容放在仓库根目录或 `docs` 目录。
2. 一并上传 `index.html`、七册正文、`verification.html`、`loop-engineering.html`、`prompts`、语言目录、`assets`、`samples`、`reference`、`verification`、README和许可声明。请包含 `.nojekyll`。
3. 在GitHub的 Settings → Pages → Build and deployment 中，将Source设为 Deploy from a branch。
4. 选择已上传的分支，以及对应布局的 `/ (root)` 或 `/docs`，然后保存。
5. 发布完成后，打开Pages中显示的地址，检查总目录和各分册的链接。

详见[GitHub发布源设置说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。`manual/_manual_work` 是本地构建与验证工作区，不属于发布内容。

## 编辑与更新

日文正文位于 `tools/chapters.py`，英文正文位于 `tools/en/*.md`。`tools/generate_en.py` 生成英文版，`tools/generate.py` 包含API字典和页面生成逻辑，`assets/manual.css` 定义样式。使用Python更新手册：

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

源码收集和构建需要原始源码树及相应工具。字体转换和像素比较使用Pillow。阅读HTML不需要Python或服务器。每次验证都应记录所用源码与可执行文件的哈希值。另请参阅[编译器修复记录](verification/compiler_fixes.md)和[第三方声明](THIRD_PARTY_NOTICES.md)。

## 本次源码公开范围

KOKURA-GUI、KUROSAKI-GUI和PLITA不在本次上传范围内。公开源码和手册涵盖命令行工具、核心及集成API。
