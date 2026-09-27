## 1. KITAQFC 与 GB 编译器的关系
KITAQFC 使用 KITAQGB 的前端，为 NES/FC 的 6502 系列 CPU 生成代码。它不把 GB ROM 转换成 NES ROM；程序仍需针对目标机器的画面、声音、内存和 mapper 编写。

KITAQFC 支持结构体复制、普通函数调用、for、while 和 do-while。do-while 先执行循环体至少一次，再检查条件；continue 进入末尾条件判断，break 退出循环。switch 选择 0..255 范围内的 case 常量，没有匹配时执行 default，选择表达式只求值一次。break 退出最内层循环或 switch；switch 内的 continue 推进外层循环。

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

### 表达式结果与求值
比较运算符 `==`、`!=`、`<`、`<=`、`>`、`>=` 和逻辑运算符 `!`、`&&`、`||` 以 0 表示假、1 表示真。结果可存入 `u16`、传参、返回或参加算术。例如 `score = 500 + (lives != 0);` 在还有生命时得到 501，否则为 500。

`&&` 左操作数为零时跳过右操作数；`||` 左操作数非零时跳过右操作数。在 `pointer != 0 && pointer->active != 0` 中，空指针会阻止成员访问。16 位值的两个字节都参加真值判断，因此 256 为真。按位 `&` 和 `|` 不短路。

`++value` 返回更新后的值，`value++` 返回原值，也可操作数组元素、解引用指针及结构体成员。`buffer[index()]++` 只调用一次 `index()`。对于 `u16 *p`，`p++` 前进两字节到下一个元素，`(*p)++` 则递增所指向的值。

`sizeof(array)` 给出整个数组的字节数，`sizeof(pointer)` 为 2。对于 `u16 values[9];`，`sizeof(values)` 为 18。此规则涵盖 ROM 数组、局部数组及数组成员。`sizeof(function())` 检查返回类型，不调用函数。

函数声明和定义的参数类型及顺序必须一致，参数名可以不同；函数体使用定义中的名称。例如 `u8 next(u8 input);` 可定义为 `u8 next(u8 value) { return (u8)(value + 1); }`。参数和局部变量会遮蔽同名全局变量。

用 `?:` 选择数组或字符串，会产生指向所选元素类型的指针，可直接传参，例如 `show(ready ? "READY" : "WAIT");`。对于 u16 数组 a 和 b，`(ready ? a : b) + 1` 前进两字节，指向所选数组的第二个元素，不复制数组。

`condition ? yes : no` 先计算条件，再只计算选中的分支。条件和分支可含可变移位数，例如 `on = (pattern & (0x80 >> bit)) != 0 ? 4 : 2;` 根据所选位得到四或二。被 `&&` 或 `||` 跳过的右操作数中的函数也不会调用。for 循环中的 continue 先执行一次更新表达式，再重算条件；while 和 do ... while 中则进入条件判断。

## 5. 循环与状态分派
{{CODE:4}}

这些片段展示至少更新一次的循环，以及为当前状态选择处理函数的分支。请在程序中定义 update、condition、state 和各状态处理函数。完整循环示例见 `fc_control.c`；完整场景管理 ROM 见库的帧与场景示例。

注册 scene、entity 和 system 回调时，请匹配声明要求的参数和返回类型。库会在相应更新、绘制或帧等待操作中调用已注册处理函数。遵守各 API 的 ROM 存储体及映射要求，不要假定递归或可变参数具有桌面级支持。

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

普通的 ROM 数组下标读取和 C 指针引用会使这些数组放入公共存储体 0，除非 `#pragma fixed_bank` 明确固定了位置。这样，调用方位于可切换存储体时，数据仍然可见。显式远访问应在同一次调用中传入数组名及同名的 `__bankof`，例如 `__farpeek8(__bankof(table), table)`。仅查询存储体编号，不会请求公共存储体放置。固定存储体数据和汇编内引用仍要求自行维护正确映射；这是基于语法的放置检查，不是指针流分析。公共存储体仍有容量限制。

## 9. FDS、扩展音源与外设
FDS 涉及磁盘文件布局、启动、覆盖加载和保存。请参阅 `fds_manifest_sample.json` 与 FDS 头文件。需要的 BIOS 应自行准备在运行环境中，公开包不含 BIOS。

调用 VRC6 或 VRC7 音源操作不会改变 ROM 的 mapper 设置，二者必须匹配。外设应分别验证输入值、连接状态以及对普通手柄路径的影响。

## 10. 诊断与构建结果
KQ 诊断以及 `symfind`、`src2asm`、`romdiff` 等开发命令与 GB 类似，但继承的 GB 帮助选项未必都对应已实现的 NES 功能。FC 字典单独从 FC 源码与头文件收集。

关闭显示的初始化也可能产生直接 PPU 操作警告，例如 KQ2421。不要为消除警告而破坏安全初始化；应检查显示时机与运行日志。“没有错误”和“没有警告”是两种不同结果。

## 源码位置
编译器源码和项目文件位于仓库内的同名子目录，可执行文件位于仓库根目录，库文件位于 `lib/`。项目路径和构建要求请参阅[目录结构说明](../GITHUB_SETUP.md)。
