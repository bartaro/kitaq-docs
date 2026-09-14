# 使用 KITAQGB、KOKURA 和 SARAKURA 开发游戏

填写需求后，将本文完整交给 AI。命令假定 `kitaqgb`、`kitaqfc`、`kokura`、`kurosaki`、`sarakura`、`kitaq-docs` 仓库与 `game-gb` 或 `game-fc` 项目位于同一父目录。请从该父目录运行，并按实际环境调整路径。

## 需求

- 游戏名称：<填写>
- 类型与核心玩法：<填写>
- 操作方式及成功、失败条件：<填写>
- 必需的界面、关卡、敌人和道具：<填写>
- 画面风格、背景音乐和音效：<填写，并注明所提供素材的路径>
- 存档、通信、外设及其他要求：<填写，或无>
- 项目目录：<填写>
- 再分发要求：<例如，自编代码和原创素材可按 MIT 许可公开>

- 目标机型：<初代 Game Boy / GB 与 CGB 双兼容 / 仅 CGB>
- 性能目标：<例如，正常游玩时每秒更新游戏逻辑 60 次；注明高负载场景的可接受表现>

## 请执行的任务

请使用 KITAQGB 及其库实现游戏。使用 KOKURA 运行和调试，使用 SARAKURA 整理诊断并比较修复前后的结果。

不断重复以下过程，直到满足验收标准：明确规格 → 实现一个小改动 → 构建 → 输入操作并观察 → 调查原因 → 修复 → 在相同条件下复测。不能以写出计划、提供代码或编译成功作为完成依据。

### 确认环境和验收标准

1. 阅读工作目录的说明、各工具的 README、HTML 手册，以及所用库的头文件和实现。记录可执行文件路径及版本或 SHA-256；以实际 `--help` 输出核对命令，以源码核对 API。
2. 为输入、画面、声音、游戏进程和更新频率制定可判断的验收标准。例如，按下并松开 START 后开始游戏；碰撞扣除一条生命；暂停时指定声音静音，恢复后继续播放。
3. 只就重要歧义提问，常规、可撤销的实现决策请自主推进。不得擅自降低需求或验收标准。
4. 先用一个随附的小示例走通编译器、模拟器和 SARAKURA。它只能证明工具之间能衔接，不能代表所需游戏已经完成。

### 先实现一个可玩的最小流程

- 使用 KITAQGB 的 C 方言和 `void main()`。不要假定桌面 C 或 GBDK API 可以直接使用。除声明外，还要把所需 `.c` 实现纳入构建；检查初始化顺序、单位、符号、范围、缓冲区生命周期和 ROM 分库。
- 规划 VRAM/OAM 更新、VBlank、中断、栈、ROM/WRAM 分库和图块、精灵数量限制。传输队列的总容量、剩余容量与物理 VRAM 的容量、空闲空间不是同一概念。
- DMG 游戏不得依赖 CGB 专用功能。双兼容游戏必须分别测试两种硬件模式。
- 字母、数字和符号使用所提供的原创 `ascii.c` 字体，并检查字符与图块的对应关系。

- 先连通启动、标题界面、可控制角色、成功或失败及重新开始，再扩充内容。
- 保留可编辑的图形、音乐、音效源文件及生成步骤，确认构建实际读取了导出数据。
- 源码注释用英文，进度报告用简体中文。SARAKURA 的标准报告保持英文。

### 将每次构建与运行对应起来

使用 `out/iter-001` 等目录区分每轮输出。记录命令、退出码及源码、素材、工具、ROM、元数据的哈希。构建失败后，不得运行遗留的旧 ROM。映射文件、源码映射和调试信息必须与 ROM 来自同一次构建。

下面是基本的 DMG 检查示例。请准备 `main.c` 和所需库实现文件，并按游戏调整选项和输入序列。

```powershell
$iteration = '.\game-gb\out\iter-001'
New-Item -ItemType Directory -Force $iteration | Out-Null

# Include all additional implementation units required by the game.
& '.\kitaqgb\kitaqgb.exe' '.\game-gb\src\main.c' `
  -I '.\kitaqgb\lib' -o "$iteration\game.gb" `
  --profile=dev --rst-disable --stack-bank=fixed --no-disasm `
  "--emit-ai-metadata=$iteration\build.json"
if ($LASTEXITCODE -ne 0) { throw 'Build failed; inspect the build log.' }

# This sequence presses START once, with released intervals on both sides.
& '.\kokura\kokura-cli.exe' "$iteration\game.gb" `
  --hardware dmg --run-frames 300 `
  --input-seq 'NONE:60;START:1;NONE:239' `
  --png "$iteration\frame.png" --record-wav "$iteration\audio.wav" `
  --dump-report "$iteration\run.json" `
  --emit-diagnostics "$iteration\events.jsonl"
if ($LASTEXITCODE -ne 0) { throw 'Emulator run failed; inspect the run log.' }

& '.\sarakura\sarakura.exe' gb analyze `
  --metadata "$iteration\build.json" --events "$iteration\events.jsonl" `
  --frames 300 --out "$iteration\analysis" --fail-on error
if ($LASTEXITCODE -ne 0) { throw 'Inspect the analysis report and fix the cause.' }
```


`--hardware dmg` 选择初代 GB。测试 CGB 或双兼容时，需匹配 ROM 头部和模拟器机型设置。示例输入在两个松开区间之间按一次 START。运行 300 帧不能代表完成整个游戏的测试。

### 检查画面、声音、状态和性能

- 保存输入场景，区分按下、按住和松开。覆盖规格中的全部路径：启动、开始、移动、动作、碰撞、滚动、关卡切换、游戏结束、重新开始、暂停，以及适用的存档和通信。
- 保存关键帧 PNG、输入、运行报告、诊断 JSONL、WAV 和必要的状态、内存观测。检查实际到达帧数与停止原因。真正打开图像查看；一张截图不能证明运动或输入响应。将计数器、坐标和状态变化与预期值对照，同时检查画面边缘、图块和属性边界及精灵密集场景。
- 检查音乐、音效、同时发声、断音、暂停和恢复。仅生成 WAV 不能证明声音正确。无法试听时，应区分已完成的波形、数值检查与尚未确认的听感。
- 测量高负载场景的目标 CPU 工作量、游戏更新及传输量，FC 还需计入 NMI 工作。宿主机上模拟器的运行速度不等于游戏更新频率，也不是实机速度证明。使用 `--allow-unimplemented` 后能继续运行，不代表未实现功能已受支持。

### 分析、修复并复测

- 向 SARAKURA 提交被测 ROM 的构建元数据和该次运行的诊断 JSONL。CPU 跟踪或普通运行报告不能替代它。`--frames` 指定分析条件；SARAKURA 不执行 ROM，也不自动修改源码。
- 阅读 `report.html`、`ai_diagnostics.json`、`repair_prompt.md`、`retest_plan.json`，与复现步骤、画面、声音和源码核对。区分推测的源码位置、原因与已确认事实，并区分正常等待循环与卡死。逐项判断警告，记录未支持事件和分析范围限制。不要通过过滤警告或缩短测试来获得通过结果。
- 把问题缩减为最小复现，修复原因后重新构建。若根因在编译器或模拟器，应与游戏代码问题分离，并为工具修复补充回归验证。
- 复测时保持输入、随机种子、机型和视频制式、Mapper、观测帧和诊断设置一致。新 ROM 使用对应元数据；代码或 RAM 布局变化后，不得盲目复用即时存档。

```powershell
& '.\sarakura\sarakura.exe' baseline-delta `
  --baseline '.\game-gb\out\iter-001\analysis' `
  --current '.\game-gb\out\iter-002\analysis' `
  --out '.\game-gb\out\delta.json' --markdown '.\game-gb\out\delta.md' `
  --fail-on-new error --fail-on-regression error --enforce
```


诊断差异应与操作、画面和声音的验收结果结合使用。相同失败反复出现时，应重审证据与假设，不要无依据地继续修改。

### 完成条件与交付内容

用交付源码和设置构建最终 ROM，再执行全部必需场景。仅使用无敌状态、自动测试输入或另一种 Mapper，不能证明最终版本的正常游玩。提供需求与测试对应表，说明剩余警告的原因，明确未验证、未支持项目。未做实机测试时标注“实机未验证”。

交付源码、工具和库的标识信息、可编辑素材、可复现的构建与测试脚本、ROM、最终验证证据，以及说明安装、操作和已知限制的 README。按需附上回放和测试驱动程序。仅在明确授权范围内发布或向外部发送文件。验证后删除不必要的中间构建和临时跟踪，但保留源码、素材、最终成果及必要的回归证据。

若环境或权限阻碍必需检查，应报告准确的复现步骤和所需操作，不得标记为完成。
