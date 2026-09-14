## 已构建的 Windows CLI
仓库根目录包含 `kokura-cli.exe`。下载仓库 ZIP，并把许可声明与可执行文件一起保留。这个 Windows x64 CLI 运行时不需要安装 Rust、Python 或 .NET。下面的构建步骤用于从源码重新生成程序。独立项目代码由 DAISUKE OBA 以 MIT 许可提供；依赖条件保留在 `BINARY_NOTICES.md` 和 `licenses/` 中。

## 1. KOKURA 的用途
KOKURA 模拟 GB/CGB 软件，记录图像、音频、CPU 执行、内存、bank、输入和诊断事件。命令行工具的可执行文件为 `kokura-cli.exe`。

## 2. 构建并运行第一个 ROM
{{CODE:0}}

安装 Rust 和 Cargo。只需要 CLI 时，构建指定 crate 即可。先使用第 1 卷的 hello ROM。默认只运行一帧，应通过 `--run-frames` 指定到达目标场景所需帧数。这里计算的是模拟帧，不是实际等待秒数。

## 3. 选择 DMG 或 CGB
`--hardware auto` 是默认设置，也可明确选择 `dmg` 或 `cgb`。双模式 ROM 应在两种模式下测试。CGB 专用 ROM 拒绝在 DMG 模式启动，本身并不构成模拟器故障。

{{CODE:1}}

## 4. 提供输入
`--input` 持续按住同时输入的按钮组合，`--input-seq` 按时间提供一串输入。按钮名称为 `A,B,START,SELECT,UP,DOWN,LEFT,RIGHT`；松开区间使用 `NONE`。PowerShell 中含分号的输入序列要加引号。

{{CODE:2}}

测试“新按下”时应包含松开区间。按住 A 120 帧与按 A 120 次并不相同。输入计数课程中，上述序列应只让计数增加一次。

## 5. 图像、视频和音频
`--png` 保存最终画面；`--screenshot` 配合 `--screenshot-frames` 捕获指定帧；`--record-video` 记录视频，`--record-wav` 记录音频。不使用 APU 的 hello 程序生成无声 WAV 是正常情况。

{{CODE:3}}

范围写作 `start:end`。请保留报告，以区分已加载状态中的累计帧号和本次运行位置。声音是否可听、音高、断音、削波要分别检查。模拟器录音不证明与实机逐样本一致。

## 6. 保存与恢复状态
{{CODE:4}}

通常应使用相同 ROM 和模拟器版本。模拟器状态不同于游戏自身存档；CLI 的 KQS 与 C API 的 JSON 状态也不是同一种格式，改扩展名不能使它们互换。

## 7. 观察符号与内存
ROM 旁的 `.map`、`.source_map.txt`、`.dbg2.json`、`.build_report.json` 可被自动识别。请保留与 ROM 同次构建的辅助文件，其他构建的文件会误导观察。

{{CODE:5}}

`wram` 是观察窗口名称，0xC000 是起始地址，0x40 是长度。较小窗口更容易找到变化的变量。`--watch-baseline-mode` 选择与初始值、前一帧或命名基准比较。

## 8. 停止条件、重放与逆向分析
`--breakpoint`、`--watchpoint`、`--run-until`、`--snapshot-at` 按条件停止或保存。它们各自的参数小语法不同，请看下方参考和实际帮助。

{{CODE:6}}

先找到第一次分歧，再缩小到附近区间。`--decompile-out` 产生伪代码与控制流信息，`--disassemble-out` 显示 CPU 指令。反编译不能完整恢复原来的 C 代码和变量名。

## 9. 将诊断交给 SARAKURA
{{CODE:7}}

KOKURA 的 `--emit-diagnostics` 接收 **JSONL 文件名**，例如 `out/gb_events.jsonl`。普通运行报告 JSON、CPU 跟踪 JSONL 都不等于诊断事件输入。

## 10. 通信工作
`pair` 模拟两台机器；`four_player_adapter` 是主机选择通信伙伴的逻辑结构；`dmg07` 模拟物理 DMG-07 协议。通过 `--link-job` 传入工作 JSON，或使用 `--link-topology`、`--link-session` 配置会话。

{{CODE:8}}

各 ROM 必须实现通信。运行两个普通 hello 程序，并不构成通信库测试。记录各会话的 ROM、槽位、输入和状态，并注明哪些实际设备行为仍未验证。

## 11. 外部应用集成
公开 C ABI 位于 `kokura-capi`；Python 可通过提供的桥接代码和 Python crate 访问。调查集成问题前，先建立最小 CLI 复现步骤。

## 12. 按顺序阅读报告
先检查执行帧数与停止原因，再看画面、输入结果、声音、错误与警告以及性能分析。无输入地长时间停留在标题画面，可能自然产生静止画面或重复 PC 警告。应结合目标场景判断，不要机械地把每条警告当作故障。
