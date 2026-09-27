# KITAQ 系列手册

<!-- readme-language-links:start -->
[English](README.md#english) | [日本語](README.md#japanese) | [한국어](README.ko.md) | **简体中文** | [繁體中文](README.zh-TW.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md)
<!-- readme-language-links:end -->

[打开简体中文总目录](https://bartaro.github.io/kitaq-docs/zh-CN/index.html)

这套手册从第一个可运行的程序开始，介绍语言语法、构建命令、库和编译器内建函数，并为示例说明用途、预期结果和使用条件。初学者可以先完成构建和运行，再逐步查阅所需的功能。

## 直接打开各分册

| 分册 | 内容 |
| --- | --- |
| [KITAQGB](https://bartaro.github.io/kitaq-docs/zh-CN/kitaqgb.html) | GB/CGB 的语言语法、内建函数和构建 |
| [KITAQGB 库](https://bartaro.github.io/kitaq-docs/zh-CN/gb-library.html) | 图形、输入、音频、通信和游戏辅助功能 |
| [KOKURA](https://bartaro.github.io/kitaq-docs/zh-CN/kokura.html) | GB/CGB 的运行、输入、观察、记录和调试命令 |
| [KITAQFC](https://bartaro.github.io/kitaq-docs/zh-CN/kitaqfc.html) | NES/FDS 的语言语法、内建函数和构建 |
| [KITAQFC 库](https://bartaro.github.io/kitaq-docs/zh-CN/fc-library.html) | NES 图形、音频、物理、线框和外设功能 |
| [KUROSAKI](https://bartaro.github.io/kitaq-docs/zh-CN/kurosaki.html) | NES/FDS 的运行、保存和分析 |
| [SARAKURA](https://bartaro.github.io/kitaq-docs/zh-CN/sarakura.html) | 诊断报告、修复计划和复测 |

## 阅读方式

手册提供英文、日文和简体中文版，可在每册顶部切换到同一分册的其他语言。下载完整目录后，打开 `zh-CN/index.html` 即可离线阅读；请保留目录结构，以便加载样式、示例和图片。支持卷内搜索、复制代码和打印。

原始源码摘录和工具输出保留原文。已确认的模拟器画面与示例说明一同展示。请结合预期结果判断；单张画面不能证明声音、输入、外设或实机运行正确。

## 游戏开发提示词

填写需求后，将完整提示词交给 AI。提示词涵盖实现、模拟器测试、SARAKURA 分析和修复后的复测，作为编译器分册中的参考示例提供。

[KITAQGB 参考提示词](https://bartaro.github.io/kitaq-docs/zh-CN/kitaqgb.html#loop-prompts) · [KITAQFC 参考提示词](https://bartaro.github.io/kitaq-docs/zh-CN/kitaqfc.html#loop-prompts)

## 完整游戏的程序解说

[《はらぺこしろへび》简体中文指南](https://bartaro.github.io/kitaq-docs/apps/harapeko_shirohebi/guide-zh-CN.html)介绍流程图、白蛇的运动与身体跟随算法，以及 KITAQGB 库的使用方法。[源码与构建说明](https://github.com/bartaro/kitaqgb/blob/main/apps/harapeko_shirohebi/README.zh-CN.md)。

## 许可证

[MIT 许可证](LICENSE) · [日文参考译文](LICENSE.ja) · [第三方声明](THIRD_PARTY_NOTICES.md)
