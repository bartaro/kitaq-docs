## 1. KITAQFC 与 GB 编译器的关系
KITAQFC 使用 KITAQGB 的前端，为 NES/FC 的 6502 系列 CPU 生成代码。它不把 GB ROM 转换成 NES ROM；程序仍需针对目标机器的画面、声音、内存和 mapper 编写。

记录中的检查运行了结构体复制和普通函数调用示例，但 **NES 的 do-while 和 switch 会报代码生成不支持错误**。解析器能识别语法，并不足以证明该语法可用于这个目标。

## 2. 开发环境与构建
{{CODE:0}}

安装 .NET Framework 4.8 Developer Pack 与 Visual Studio Build Tools，使用 Developer PowerShell。后续命令使用复制到 `kitaqfc` 仓库中的可执行文件；若位置不同，请调整路径。CHR 图像与 C 源码是不同的输入。手册的 `font.chr` 是由作者 `ascii.c` 转换而来的 8 KiB 文件。

## 3. 第一个程序
{{CODE:1}}

{{CODE:2}}

示例显示 HELLO WORLD 和 042。`m_wait` 提交 VRAM 队列、等待 NMI，并恢复滚动。通过 PPUADDR 传输会影响内部滚动状态，遗漏恢复可能使文字偏向边缘。请熟悉“关闭显示、准备素材、开启显示、与 NMI 同步”的顺序。

## 4. 语言入门
GB 卷的语句和表达式是共同基础。FC 接受 `unsigned char`、`unsigned short`；`core.h` 定义 `u8`、`u16`、`s8`、`s16`，`fc.h` 是汇总头文件。这里可以使用无参数入口 `void main(void)`。

{{CODE:3}}

整数应在 8 位或 16 位范围内使用，数组下标从 0 开始。`fc_aggregate.c` 演示函数、指针和结构体，`fc_arithmetic.c` 演示算术，`fc_control.c` 演示循环。不要加入 CGB 寄存器或 GB 专用内建函数。

## 5. 改写不支持的结构
{{CODE:4}}

要替代 do-while，可先执行一次循环体，再检查退出条件。简单的 switch 分派可改为 if/else 链。以上只是说明片段，需要自行提供 `update` 和状态函数；完整 ROM 示例请用 `fc_control.c`。

不要假定递归、间接函数调用和可变参数具有桌面级支持。当前部分 scene/entity 回调接口只保存函数指针，并不间接调用它。

## 6. 内存与 PPU
NES CPU 内部 RAM 位于 0x0000～0x07FF；0x0800 以上的镜像不是额外 RAM。6502 栈使用第 1 页，OAM 影子缓冲和队列还会保留其他区域。`--nes-local-ram=START:LENGTH`、`--nes-temp-ram=START:LENGTH` 是需要检查映射文件的高级设置。

PPU 有独立地址空间。CHR 提供图案，名称表安排图块，属性表选择调色板组，调色板保存颜色编号。背景属性通常作用于 16×16 像素区域，与 GB 图块属性不同。

## 7. NMI 与 VRAM 队列
NMI 是与显示帧边界相关的中断。显示期间直接大量写 PPU 可能破坏画面。初始化应在关闭显示时直接完成；平时更新使用 `__vramq_put`、`__vramq_copy`、`__vramq_fill` 并提交队列。

{{CODE:5}}

检查队列容量和源数据寿命。默认 NMI 负责执行队列。自定义 `__nes_nmi` 时，须保留所需队列处理、OAM 工作与寄存器保护。

## 8. Mapper 与 ROM 布局
| 选项 | 常见起步用途 |
| --- | --- |
| nrom | 小型固定 ROM 教学程序 |
| uxrom / cnrom / axrom | 简单 PRG 或 CHR 切换 |
| mmc1 / mmc3 / mmc5 | 大程序及 mapper 专用功能 |
| vrc6 / vrc7 / fme7 | 分页及相应扩展功能 |
| fds | 磁盘镜像输出 |

这些是编译器选项，不是硬件或模拟器功能完成度表。`--board=surom512` 选择特定 MMC1 电路板配置；仅填充文件使其达到 512 KiB，不能建立这种配置。请配合 KUROSAKI 的电路板审查。

{{CODE:6}}

检查 `--battery` / `--no-battery`、CHR 容量、PRG 布局和跨 bank 调用的电路板要求。更改 mapper 或镜像方式后，除生成 ROM 外，还要测试启动、滚动和数据切换。

## 9. FDS、扩展音源与外设
FDS 涉及磁盘文件布局、启动、覆盖加载和保存。请参阅 `fds_manifest_sample.json` 与 FDS 头文件。需要的 BIOS 应自行准备在运行环境中，公开包不含 BIOS。

调用 VRC6 或 VRC7 音源操作不会改变 ROM 的 mapper 设置，二者必须匹配。外设应分别验证输入值、连接状态以及对普通手柄路径的影响。

## 10. 诊断与构建结果
KQ 诊断以及 `symfind`、`src2asm`、`romdiff` 等开发命令与 GB 类似，但继承的 GB 帮助选项未必都对应已实现的 NES 功能。FC 字典单独从 FC 源码与头文件收集。

关闭显示的初始化也可能产生直接 PPU 操作警告，例如 KQ2421。不要为消除警告而破坏安全初始化；应检查显示时机与运行日志。“没有错误”和“没有警告”是两种不同结果。

## 目录调整后的源码位置
编译器源码现位于各仓库中的同名子目录。API 参考保留 9 月 12 日的历史路径。对应关系见[目录调整说明](../GITHUB_SETUP.md)，根目录可执行文件与库路径不变。
