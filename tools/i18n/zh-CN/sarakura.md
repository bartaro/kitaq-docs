## 已构建的 Windows CLI
仓库根目录提供 Windows x64 版 `sarakura.exe`。下载 ZIP 时请连同许可声明一起保留。运行无需 Rust、Python 或 .NET，下面的构建步骤用于重新编译源码。独立项目代码由 DAISUKE OBA 以 MIT 许可提供，依赖条件保留在 `BINARY_NOTICES.md` 和 `licenses/`。

## 1. SARAKURA 负责什么
SARAKURA 汇总编译器构建信息和模拟器诊断事件，将其整理成有助于修复与复测的资料。它不是运行 ROM 的模拟器，也不会悄悄修改你的 C 源码。

## 2. 构建工具
{{CODE:0}}

简写命令 `sarakura` 假定已加入 PATH，否则请使用可执行文件路径。GB 选择 `gb analyze`，FC 选择 `fc analyze`。

## 3. 第一次分析
需要两类输入：`--metadata` 是构建时 JSON，`--events` 是运行时诊断 JSONL。JSONL 每行存放一个 JSON 对象。

{{CODE:1}}

在浏览器打开输出的 `report.html`。阅读单项诊断前，先确认目标、观察帧数、错误数和警告数。`--frames` 描述分析条件，并不是要求 SARAKURA 执行这么多帧的 ROM。

## 4. 先检查输入
{{CODE:2}}

研究游戏行为之前，应先区分文件无法读取、平台不匹配、事件类型不支持等问题。把普通模拟器报告当作事件文件传入，不会使它成为有效诊断输入。

## 5. 理解诊断
error 值得优先调查，warning 是否是问题取决于情境，info 提供背景。严重级别有助于分流，却无法完全理解游戏意图。例如仅凭重复 PC，未必能区分正常标题等待循环和死机。

请结合 ROM 哈希、输入序列、场景、画面、声音与源码位置判断。修复前后的条件应一致，否则诊断减少可能仅仅是因为运行了别的场景。

## 6. 输出文件
内置说明、诊断提示与修复指引使用英语，HTML 声明 `lang="en"`。用户字符串和事件 ID 不会自动翻译。默认隐藏处理会替换部分项目标签和路径，但不保证匿名化所有地址或观察内容。公开私人输入的分析结果前，应检查报告。

| 文件 | 用途 |
| --- | --- |
| ai_diagnostics.json | 供自动处理的规范化诊断 |
| diagnostic_summary.json | 数量统计与摘要 |
| report.html | 便于阅读的报告 |
| repair_prompt.md | 开始调查修复所需的上下文 |
| repair_plan.json / .md | 修复顺序和对象 |
| automation_plan.json / .md | 按工具能力组织的工作计划 |
| retest_plan.json | 复测计划 |
| repro_bundle.zip | 复现资料包 |

生成计划不等于执行计划。修改 C 源码或 ROM 后，需要重新运行编译器、模拟器和 SARAKURA。

## 7. 规则目录、筛选与覆盖情况
{{CODE:3}}

`catalog` 列出诊断规则，`pack-plan` 按领域分组，`coverage` 检查对应事件是否被观察到。目录中存在规则，不保证当前模拟器会生成该事件。

{{CODE:4}}

`--diagnostic-rule` 选择事件名或规则 ID，`--phase` 选择阶段，`--diagnostic-pack` 选择领域。筛掉一条诊断并不等于解决问题。

## 8. 比较修改前后
{{CODE:5}}

结果分为新增、已解决、改善、持续存在和退化。应区分遗留问题与新引入的问题。比较时固定输入、帧数和诊断过滤条件。

## 9. 格式验证与 CI
{{CODE:6}}

持续集成用于自动执行可复现的检查。`ci-summary` 只有带 `--enforce` 才改变进程退出码，否则应读取 JSON 判定。analyze 的 `--fail-on error` 在有错误时返回非零退出码；默认 `never` 不会因为诊断而失败，因此 CI 必须明确选择策略。选择 `warn` 时，警告也会造成失败。

```powershell
sarakura ci-summary --diagnostics .\out\report --fail-on error --enforce
if ($LASTEXITCODE -ne 0) { throw "The diagnostic failure condition was met" }
```

模式验证成功只验证了数据格式。游戏是否符合设计，还需要输入、画面和声音测试。

## 10. 处理复现资料
`normalize-events` 规范化事件记录，`inspect-repro` 检查复现包。分享前请确认资料对应目标 ROM，并包含所需输入步骤。`--allow-project-labels` 会明确保留项目派生标签与标识符。

## 11. 最小练习输入
手册附有小型 GB/FC 构建元数据与事件示例。可打开 [GB 合成报告](verification/sarakura-gb-synthetic.html)或 [FC 合成报告](verification/sarakura-fc-synthetic.html)。`samples/sarakura_demo.ps1` 演示分析流程。这些资料是为学习格式而人工构造的，不是从真实 ROM 捕获的证据；实测应使用 KOKURA 或 KUROSAKI 记录的事件。

## 12. 一次修复与复测循环
1. 用同一 ROM 和输入复现问题，保留日志和画面。
2. 用 SARAKURA 整理候选原因，查看相关源码。
3. 针对原因做集中修改。
4. 重新构建并执行同样的操作。
5. 将 baseline-delta 与图像、声音、游戏行为一起比较。

保持每轮规模较小，才能清楚理解每项修改与结果的关系。
