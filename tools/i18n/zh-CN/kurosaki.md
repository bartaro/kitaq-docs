## 已构建的 Windows CLI
仓库根目录提供 `kurosaki.exe`。下载 ZIP 后，请将可执行文件与许可声明一起保存。Windows x64 CLI 运行时无需 Rust、Python 或 .NET；以下构建步骤用于重新编译源码。独立项目代码由 DAISUKE OBA 以 MIT 许可提供，依赖条件见 `BINARY_NOTICES.md` 和 `licenses/`。

## 1. KUROSAKI 的用途
KUROSAKI 是能够读取 KITAQFC 信息的 NES/FC/FDS 观察型模拟器。CLI 可检查 ROM、运行程序、录音、诊断、保存快照、重放输入、反汇编和反编译候选函数。各 mapper 的实现范围不同，请先查看 ROM 与支持信息。

## 2. 构建与启动
{{CODE:0}}

以下简写 `kurosaki` 假定可执行文件目录已加入 PATH；否则请替换为 `& "可执行文件完整路径"`。

{{CODE:1}}

用第 4 卷的 hello ROM 验证文字显示。`inspect-rom` 检查头部，`run` 推进 CPU/PPU 执行。检查头部成功不代表程序能正常运行。

## 3. 检查 mapper 与电路板
`mapper-list` 列出已注册类型，`mapper-info` 说明某一类型，`audit-board` 检查电路板约束。mapper 编号把 ROM 头与物理接线假设联系起来；仅有名称无法确定容量、CHR-RAM 或固定 bank 行为。

{{CODE:2}}

`--allow-unimplemented` 允许遇到未实现部分后继续观察。使用此选项的运行结果，不是相关功能已受支持的证据。

## 4. 手柄输入
`run --pad1`、`--pad2` 使用 NES 原始位掩码：A=1、B=2、SELECT=4、START=8、UP=16、DOWN=32、LEFT=64、RIGHT=128。同时按键时将对应值相加。

{{CODE:3}}

上例持续按 A 120 帧。标题、开始、确认这类有顺序的动作应使用重放。CLI 的 `replay-record` 示例记录没有交互输入的基准运行，不等于录制人在 GUI 中的操作。

## 5. 快照与重放
{{CODE:4}}

可恢复状态使用版本 2 快照。请保证状态与 ROM SHA-256 对应。`snapshot-resume` 从存储点继续；`snapshot-rebase` 按提供的兼容性契约将状态显式转移到另一兼容 ROM。更改代码或 RAM 布局后，不应无条件复用旧状态，通常应从启动重新执行相同操作。

## 6. 跟踪、诊断与性能分析
{{CODE:5}}

跟踪记录事件顺序，诊断指出匹配规则的观察，性能分析显示执行集中位置。异常附近的几帧通常比漫长完整记录更容易分析。

通过 `--kitaqfc-debug` 传入匹配的构建调试 JSON。缺少源码行信息的观察，不能解释成完整的源码行级跟踪。

## 7. 保存声音与画面
{{CODE:6}}

寄存器变化、PCM 生成和实际声音正确，是三个不同检查。测试内置或扩展音源时，记下 mapper。单张 PNG 无法证明移动或输入行为，应同时保留前后状态和输入。

## 8. 反汇编与反编译
{{CODE:7}}

`disasm` 输出指令序列；`decompile` 输出函数边界候选、CFG、引用与伪代码。存在可切换 bank 时，CPU 地址不足以确定 ROM 的物理位置。必要时通过 `--snapshot` 提供 mapper 状态，再用执行跟踪或注解作为佐证。这不是原始源码的完整恢复。

## 9. 连接 SARAKURA
{{CODE:8}}

KUROSAKI 的 `--emit-diagnostics` 与 KOKURA 相同，接收 **JSONL 文件路径**。请区分 CPU 跟踪和诊断事件文件。

## 10. 公开范围
KUROSAKI-GUI 尚未公开。当前手册涵盖 CLI 与集成 API。

## 11. FDS 与存档 RAM
`fds-inspect` 检查磁盘结构，`export-assets` 导出素材。FDS 的启动、BIOS、磁盘访问条件与 NES 卡带不同，应单独测试。电池存档 `.sav` 与 `.kss.json` 快照用途不同，要采用实现支持的存储布局。

{{CODE:9}}

`battery-export` 从匹配的 ROM 和快照提取原始存档 RAM；`battery-run` 加载该 RAM 并从上电开始，不恢复中断时的 CPU/PPU 执行状态。使用 `--save-out` 指定输出。这些操作需要带存档 RAM 的受支持 ROM，不适用于所有教学 ROM。
