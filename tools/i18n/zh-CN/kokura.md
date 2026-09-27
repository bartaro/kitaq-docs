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

## 13　命令实例与参数详解

以下命令在各仓库共同的父目录中运行，并以 `out/game.gb` 为 ROM。先用 `New-Item -ItemType Directory -Force out` 创建输出目录。KOKURA 的普通运行选项直接写在 ROM 路径后面，不需要 `run` 子命令。不同版本的选项可能不同，请以正在使用的可执行文件的 `--help` 输出为准。

### 13.1　选择运行方式并限制执行时间

| 参数 | 用法与含义 |
| --- | --- |
| ROM 路径 | 普通运行的输入；任务文件或回归矩阵也可自行指定 ROM。 |
| `--hardware auto` | 选择 `auto`、`dmg` 或 `cgb`，默认由 `auto` 自动判断。 |
| `--run-frames 120` | 帧数上限，默认 1 帧。停止条件可以提前结束运行；输入序列也有自己的执行时长。 |
| `--job out/test.json` | 从任务文件读取运行条件。任务可指定 `run.frames`、ROM、状态、输入和捕获设置；相对路径以任务文件所在目录为基准。 |
| `--dump-report out/run.json` | 将运行报告写入文件；未指定时输出到标准输出。 |
| `--regression-matrix out/matrix.json` | 运行回归矩阵。必须检查各个用例的结果，不能仅凭进程退出码判断全部通过。 |

操作分派的优先级为：反编译、反汇编、回归矩阵、联机任务、命令行联机会话、普通运行。一次命令请选择一种操作。

```powershell
.\kokura\kokura-cli.exe out/game.gb --hardware dmg --run-frames 120 --png out/game.png --dump-report out/run.json
```

运行后检查报告中的实际帧数和停止原因，确认程序确实执行了预定区间。

### 13.2　按键与输入序列

`--input "A,RIGHT"` 表示同时按住 A 和方向右。按键名不区分大小写，`NONE` 表示松开全部按键。

`--input-seq "NONE:30;A:1;NONE:89"` 由分号分隔的 `按键:帧数` 片段组成：先等待 30 帧，按 A 1 帧，再松开 89 帧。`--input-script` 接收相同的序列文本，并非脚本文件名；同时指定时它优先于 `--input-seq`。包含分号的整个序列必须加引号。

数值掩码为 RIGHT=1、LEFT=2、UP=4、DOWN=8、A=16、B=32、SELECT=64、START=128。这与 NES 的按键位定义不同。输入序列应覆盖所需的观察区间，并明确安排松开按键的片段。

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 120 --input-seq "NONE:30;A:1;NONE:89" --png out/after-a.png --dump-report out/after-a.json
```

测试“按下一次”时，应比较持续按住与松开后重新按下的结果，确认计数或菜单操作只在预期的时刻发生。

### 13.3　截图、录音与视频

| 参数 | 用法与含义 |
| --- | --- |
| `--png out/final.png` | 保存最终画面的 PNG；与 `--screenshot` 同时指定时优先。 |
| `--screenshot out/screen.png` | 保存截图，也支持 BMP；没有扩展名时使用 PNG。 |
| `--screenshot-frames 30:32` | 保存第 30、31、32 帧，并在文件名中附加帧号；还必须指定截图目标路径。 |
| `--record-wav out/sound.wav` | 保存运行期间的音频。 |
| `--record-wav-frames 1:180` | 录制第 1 至 180 帧，包含两端；单位是视频帧，不是音频采样点。 |
| `--record-video out/play.gif` | 录制 GIF 或 Y4M，默认 GIF；不输出 MP4。 |
| `--record-video-frames 30:120` | 录制第 30 至 120 帧，包含两端。 |
| `--audio-buffer-frames 8192` | 音频缓冲区容量，单位是立体声采样帧，不是视频帧或单声道采样数。 |

捕获帧号从 1 开始，使用十进制。`30` 指一帧，`30:32` 指闭区间；0 和倒序区间无效。帧号属于本次运行，即使从存档恢复也是如此。请保留对应的运行报告，并事先创建输出目录。

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 180 --record-wav out/audio.wav --record-wav-frames 1:180 --record-video out/motion.gif --record-video-frames 30:120
```

连续几张截图可用来判断运动，WAV 可用来检查声音。仅有帧数或文件大小不能证明图像和音频正确。

### 13.4　保存状态与恢复运行

| 参数 | 用法与含义 |
| --- | --- |
| `--save-state out/ready.kqs` | 运行结束后保存 KQS 状态。 |
| `--snapshot out/ready.kqs` | 保存状态的另一入口；同时指定时优先于 `--save-state`。 |
| `--load-state out/ready.kqs` | 执行前载入状态。 |
| `--resume-state out/ready.kqs` | 优先于 `--load-state`，也可以覆盖任务文件中的恢复设置。 |
| `--snapshot-at "frame=60&&frame_end=>out/frame60.kqs"` | 满足条件时保存状态，可重复指定。不写 `=>路径` 时，在当前目录按 ROM 文件名和编号生成路径。 |

状态文件必须与 ROM 及模拟器版本相匹配。KQS 是模拟器状态，不是卡带 SRAM 存档，也不是 C API 的 JSON 状态格式。

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 120 --save-state out/title.kqs
.\kokura\kokura-cli.exe out/game.gb --resume-state out/title.kqs --input START --run-frames 30 --png out/started.png --snapshot out/started.kqs
```

### 13.5　观察变量和内存

| 参数 | 用法与含义 |
| --- | --- |
| `--symbols game.map` | 载入与 ROM 对应的符号文件。 |
| `--source-map game.source-map.txt` | 载入源码映射。 |
| `--toolchain-metadata game.dbg2.json` | 载入工具链元数据；匹配的关联文件也可自动识别。 |
| `--watch-window "player:0xC700:16"` | 观察命名的内存区域，可重复指定。观察窗口本身不会触发停止。 |
| `--watch-baseline-mode initial` | 基准可选 `initial`、`previous-frame` 或 `named`。 |
| `--watch-baseline-tag ready` | 选择命名基准。 |
| `--capture-watch-baseline "ready=>frame=30&&frame_end"` | 满足条件时记录基准，可重复指定。 |
| `--watch-fields preview,diff` | 选择字段；支持 `hash`、`activity`、`preview`、`baseline`、`diff`、`insights` 和 `all`。`preview` 只显示有限预览，不是完整内存转储。 |
| `--report-sections cpu,watched_memory` | 选择报告分区；仍保留 `meta` 和 `schema_version`。未知名称不会产生新的分区。 |
| `--report-minimal cpu,watched_memory` | 优先于 `--report-sections`，必须给出分区列表，并非布尔开关。 |

地址和长度可用十进制或 `0x` 前缀的十六进制。`0xC700` 只是示例地址，实际变量的位置应由本次构建的映射文件确定。

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 60 --watch-window "player:0xC700:16" --watch-fields preview,diff --report-sections cpu,watched_memory --dump-report out/watch.json
```

### 13.6　断点、写入监视与停止条件

| 参数 | 用法与含义 |
| --- | --- |
| `--breakpoint "pc:0x0150"` | 在指定 PC 停止；也支持 `symbol:main@bank:2`。 |
| `--watchpoint "player@0xC700+4"` | 在区域被写入时停止。名称可省略，长度默认 1。 |
| `--stop-on-mmio "scroll@0xFF43"` | 在指定内存映射 I/O 事件发生时停止。 |
| `--stop-on-irq "vblank:serviced"` | 阶段可选 `requested`、`serviced`、`blocked` 或 `any`；只写阶段时匹配任意中断源。 |
| `--stop-on-dma oam_start` | 支持 `oam_start`、`oam_complete`、`hdma_start`、`hdma_block`、`hdma_complete`、`hdma_cancel`、`gdma_stall`、`hdma_deferred` 和 `hdma_ignored`。 |
| `--run-until "frame=60&&frame_end"` | 所有条件同时成立时停止，可重复指定。 |

断点中的 `pc:`、`symbol:`、`@bank:` 区分大小写；地址和 bank 可用十进制或 `0x` 十六进制。即使设置了停止条件，也应保留帧数上限，避免条件始终不满足而持续运行。

条件之间使用 `&&`，但这不是 C 表达式解析器。可用条件包括 `frame=`、`ly=`、`pc=`、`bank=`、`bank_pc=bank:pc`、`symbol=`、`source=`、`event=`、`ppu_mode=`（或 `mode=`）和 `basis=`。`frame` 与 `ly` 使用十进制；`symbol`、`source` 和 `event` 接收文本。`basis` 可选 `frame_start`、`frame_end`、`step`、`event`、`trace`、`snapshot`、`stop`。还可直接使用 `frame_start`、`frame_end`、`stop`、`vblank`。不能把 `hp<10` 这类任意表达式作为条件。

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 120 --breakpoint "pc:0x0150" --snapshot out/entry.kqs --dump-report out/entry.json
.\kokura\kokura-cli.exe out/game.gb --run-frames 120 --stop-on-mmio "scroll@0xFF43" --dump-report out/scroll-write.json
```

请检查报告，确认停止原因就是指定的断点或事件，而非仅仅用完帧数。

### 13.7　时间线、回放与差异定位

| 参数 | 用法与含义 |
| --- | --- |
| `--trace-point "frame=60&&frame_end"` | 在条件满足时记录观察点，可重复指定。 |
| `--timeline-out out/timeline.jsonl` | 输出时间线；`--trace-jsonl` 同时指定时优先。时间线不是完整的逐指令跟踪。 |
| `--timeline-format jsonl` | 可选 `jsonl` 或 `csv`，默认 `jsonl`；格式由选项决定，不由扩展名决定。 |
| `--replay-interval 1` | 设置回放检查点间隔，默认 1。 |
| `--replay-max-checkpoints 120` | 保留的检查点上限，默认 16。 |
| `--rewind-on-stop-frames 10` | 停止后向前回退 10 帧；必须有相应的历史记录。 |
| `--stop-on-divergence` | 发现回放分歧时停止。 |
| `--dump-replay-tape out/baseline.json` | 输出回放记录，需启用回放。 |
| `--compare-replay-tape out/baseline.json` | 对比回放记录；ROM、输入和初始状态应保持一致。 |
| `--compare-replay-watch-only` | 仅比较观察内存，不代表整台模拟机器的状态一致。 |
| `--snapshot-on-replay-mismatch out/mismatch` | 发生不一致时按指定前缀保存状态。 |

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 60 --replay-interval 1 --replay-max-checkpoints 60 --dump-replay-tape out/baseline.json --dump-report out/baseline-report.json
.\kokura\kokura-cli.exe out/game.gb --run-frames 60 --replay-interval 1 --replay-max-checkpoints 60 --compare-replay-tape out/baseline.json --dump-report out/compare.json
```

比较结果应检查首次不一致的位置。生成了回放文件，并不等于比较通过。

### 13.8　诊断事件和复现资料

| 参数 | 用法与含义 |
| --- | --- |
| `--emit-diagnostics out/events.jsonl` | 输出诊断事件。普通运行中，它优先于另一入口 `--diagnostics-jsonl`。 |
| `--repro-bundle out/repro.zip` | 打包报告、事件和清单。ROM 元数据记录路径引用，不会将 ROM 嵌入压缩包；截图、状态和跟踪也不会全部自动收集。 |
| `--break-on-diagnostic all` | 根据最终诊断报告决定是否保存相关资料，不是在第一条违规指令处立即停止 CPU。非空筛选条件可能因最终报告中的任意诊断而触发捕获。 |
| `--png-on-diagnostic out/diagnostic` | 保存最终画面，例如 `diagnostic_000001.png`。 |
| `--snapshot-on-diagnostic out/diagnostic` | 保存最终状态，例如 `diagnostic_000001.kqs`；这不是诊断事件发生瞬间的状态。 |
| `--diagnostic-pack NAME` | 参数可被解析，但尚未应用于诊断处理。 |
| `--diagnostic-rule RULE` | 可重复指定；参数可被解析，但尚未应用。 |
| `--diagnostic-summary-limit N` | 参数可被解析，但尚未应用。 |

```powershell
.\kokura\kokura-cli.exe out/game.gb --run-frames 180 --emit-diagnostics out/events.jsonl --dump-report out/run.json --break-on-diagnostic all --png-on-diagnostic out/diagnostic-images --snapshot-on-diagnostic out/diagnostic-states --repro-bundle out/repro.zip
```

若需要准确停在某个访问或中断上，请使用 13.6 节的停止条件。分析警告时，还应区分标题画面等待、正常空闲和实际故障，结合运行场景判断。

### 13.9　反汇编与反编译

| 参数 | 用法与含义 |
| --- | --- |
| `--disassemble-out out/code.txt` | 输出反汇编，不执行普通运行。 |
| `--disassemble-range "0:0100-0150"` | 范围格式为 `BANK:START-END`，三部分均按十六进制解释，即使没有 `0x` 前缀；可重复指定。 |
| `--disassemble-format text` | 可选 `text`（默认）、`markdown` 或 `json`。 |
| `--decompile-out out/functions.json` | 输出反编译结果。 |
| `--decompile-format json` | 可选 `json`（默认）、`markdown` 或 `text`。 |
| `--decompile-function main` | 选择函数，可重复指定；符号文件有助于定位。 |
| `--decompile-all` | 处理所有具名函数。 |
| `--decompile-annotations out/annotations.json` | 载入反编译注解 JSON。 |
| `--decompile-trace out/trace.json` | 载入反编译所需的跟踪 JSON，不能任意使用诊断 JSONL 代替。 |

```powershell
.\kokura\kokura-cli.exe out/game.gb --disassemble-range "0:0100-0150" --disassemble-out out/entry.txt --disassemble-format text
.\kokura\kokura-cli.exe out/game.gb --symbols out/game.map --decompile-function main --decompile-out out/main.md --decompile-format markdown
```

反编译结果不是原始 C 源码的逐字还原。符号、映射文件和元数据都应来自同一份 ROM 构建。

### 13.10　联机任务

`--link-job out/pair.json` 从文件载入联机任务，相对路径以任务文件目录为基准。`--link-topology` 可选 `pair`、`four_player_adapter` 或 `dmg07`。使用 `--link-session` 在命令行定义会话时，至少需要两个会话，并用引号括住包含竖线分隔符的整段参数。`--link-initial-peer-slot 1` 指定初始对端槽位。

会话字段包括 `name`、`slot`、`rom`、`symbols`、`source_map`、`toolchain_metadata`、`load_state`、`save_state`、`input`、`input_sequence`、`audio_buffer_frames` 和 `watch_window`。其中 `rom` 必填。观察窗口可写为 `a:0xC700:4,b:0xC710:4`。

联机验证应检查实际收发的数据和双方状态的变化。两台模拟器都显示了画面，并不能证明通信协议正确。
