## 1. 使用库
库是在 KITAQGB 的 `__` 内建函数之上编写的可复用 C 源码，涵盖画面控制、物理、3D 和通信等功能。

{{CODE:0}}

{{CODE:1}}

每个API条目列出声明、头文件、实现和使用示例。参数传递片段展示API的调用方式，其中使用的缓冲区和对象需由调用方准备。完整程序一节提供可直接构建为ROM的示例。

## 2. 组织游戏的一帧
`system_init` 初始化帧管理；`system_wait_vblank` 等待后推进软件帧数。GB 的 VBlank 回调由这个等待函数协作调用，注册回调不等于安装硬件中断处理程序。

1. 更新输入一次。
2. 计算移动、碰撞和游戏状态。
3. 准备绘图命令与 OAM。
4. 在 VBlank 中应用更新。
5. 按选定驱动方案推进音乐。

把 `vram_flush`、`sprite_flush_oam` 等等待操作连用，可能在一次游戏更新中等待两帧。若已经自行等待，可考虑对应的 `_now` 操作，但必须保证其时序条件。

## 3. 输入与重复输入
`input_down(mask)` 检查按住，`input_pressed(mask)` 检查新按下，`input_released(mask)` 检查松开，`input_repeat(mask)` 提供菜单式重复。状态由 `input_update()` 更新；一帧中反复调用，可能丢掉按下沿。

| 按钮 | 掩码 |
| --- | --- |
| 右、左、上、下 | 0x01 / 0x02 / 0x04 / 0x08 |
| A、B、SELECT、START | 0x10 / 0x20 / 0x40 / 0x80 |

`gb_input.c` 统计 A 的按下次数。先确认长按不会连续累加，再把 `input_pressed` 换成 `input_down`，观察二者差别。

## 4. 背景、文字与 VRAM
`vram_queue_bg_tile` 排入一个图块，`vram_queue_bg_rect` 排入矩形填充，`vram_queue_bg_block` 排入数组传输。检查返回值和 `vram_get_overflowed()` 以发现容量溢出。若队列保留源指针，刷出完成前必须保持内容不变、内存有效且 bank 可访问。

`text.c`、`menu.c` 实现 `rpg.h` 声明的文字、选项和窗口功能。文字到图块的映射必须与载入 VRAM 的字体一致，不会自动采用手册 `m_text` 的映射。

## 5. 精灵与动画
从 `sprite_init`、`sprite_alloc`、`sprite_set_tile`、`sprite_set_pos` 开始。GB 总共允许 40 个精灵，每条扫描线最多 10 个，所以除了总数，也要考虑横向聚集。可用 `sprite_warn_scanline_overflow`、`sprite_max_scanline_count` 检查布局。

`MetaSpritePart` 描述相对 OBJ 位置；`SpriteAnim` 描述图块帧与更新间隔。`metasprite_draw` 绘制的部件应与分配的 OBJ 槽位匹配。`gb_sprite.c` 用字母 A 演示把字符图块当成精灵。

## 6. 颜色、滚动、光栅效果与镜头
`cgb_bg_rgb`、`cgb_obj_rgb` 的 RGB 参数是 0～31，不是 0～255。`CGB_RGB15` 将分量打包到 16 位容器。高级 CGB 调色板辅助函数在 DMG 上设计为不执行操作。

`Scroll_SetBg` 设置背景位置，`Scroll_SetWindow` 设置窗口位置，camera 从世界坐标计算可见范围。请区分镜头的定点单位和屏幕的整数像素。

`raster.c` 构建分段滚动表和逐扫描线水平扭曲。`Scroll_SplitCommit` 使用 VBlank/STAT 向量。不要让音乐和滚动的独立处理程序各自占用同一向量；需要时应采用共同分派器。

## 7. 音乐与音效
依次编译 `audio_hwregs_gb.c`、`audio.c`、游戏源码。游戏已经定义 NR10～NR52 时，不要再加入重复定义。`Audio_Init` 后通常每帧调用一次 `Audio_Update`。

`Audio_PlayMusic(bank,song)` 显式指定乐曲 bank；`Audio_PlaySFXBanked` 播放另一 bank 的音效。共享物理通道的音效由优先级仲裁。GB 只有 CH1、CH2、CH3、CH4 四个物理音频通道。

音乐流命令 `AUDIO_CMD_NOTE`、`AUDIO_CMD_SET_INST` 使用以下通道编号：**0=CH1、1=CH2、2=CH4、3=CH3**。不要与一般 API 通道常量混淆。当前头文件定义 `AUDIO_NOTE_MAX=67`。

基本 CH1 音效流每帧读取音符/音量对，以音符 0 结束。CH3 使用不同标记和格式。请看 `gb_sound.c`。淡入淡出由 `Audio_Update` 推进，停止更新也会停止渐变。

## 8. VBlank IRQ 音乐
`audio_vblank.c` 使用独立的播放格式。带时间信息的记录由5个字节组成：`delay, ch2_note, ch1_note, ch3_note, ch4_noise_param`。驱动可以读取可直接寻址的乐曲，也可以从WRAM队列取出数据。公开库不包含队列补充函数，游戏需要自行提供数据生产端，并协调其写入与ISR的执行。`LOOP` 仅用于直接寻址模式，`IMMEDIATE` 仅用于队列模式。普通 `audio.c` 的数据流不能原样传入。

{{CODE:2}}

补丁设置 0x0040 的 VBlank 向量并更新校验和，只适用于为该驱动设计的 ROM。检查与自定义 VBlank ISR、分屏滚动之间的向量占用关系。构建成功不代表已经听到正确音乐；请用 KOKURA 录音并确认乐曲确实推进。

## 9. 定点数、物理与 3D
`fixed.h` 的 Q8.8 中，256 表示 1.0，128 表示 0.5。`gb_fixed.c` 演示 `fix_from_int`、`fix_mul`、`fix_to_int`。先规划数值范围，再实现计算，避免溢出。

`physics2d` 处理矩形，`physics2d_circle` 处理圆，`physics3d` 处理三维AABB。由调用方准备并初始化world和body数组，设置速度或重力后再调用step。位置和每步速度应使用一致的单位；库不会自动换算为像素。圆形示例使用位置40、速度2。逆质量为0表示静态物体。各系数的表示方法和中间计算的取值范围请查看头文件。尤其要注意，`kq2d_body_apply_friction` 会将系数转换为有符号8位数，因此128～255会变成负数，不能当作常规无符号Q8衰减系数使用。完整的单步示例见 `gb_circle.c`。

`wire3d_dmg` 是面向Game Boy的黑白线框渲染库。128×96画面使用 `wire3d_dmg_96.c`，128×120画面使用 `wire3d_dmg.c`，函数统一采用 `Wire3DDMG_*` 名称。`wire3d` 和 `dmg3d` 也可分别作为96行与120行配置的入口，每个程序只编译一个入口。`wire3d_cgb` 是专门用于彩色显示的渲染器。请明确预留各渲染器使用的RAM、VRAM和屏幕区域。两种黑白渲染器会直接舍弃跨越深度范围边界的边，而不会裁剪它们。场景遮挡也只是利用面的包围矩形及线上5个采样点进行近似判断，并非逐像素深度测试。 CGB路径使用双速与DMA，要求 `--cgb=cgb_only`。

`Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=96`) 会清空绘图缓冲区。`Wire3DDMG_BeginFrame` (`WIRE3D_DMG_HEIGHT=120`) 则只重置遮挡状态，DMG3D的暂存数据在上传到VRAM时才会被清除。脏图块传输还会处理上一帧的图块，以擦除旧像素。辅助传输与主缓冲区共享部分内存，并非独立缓冲区。请根据所用渲染器安排每帧的调用顺序。

CGB版的线条请使用颜色编号1、2、3。普通128 × 96模式会叠加颜色位，因此颜色1与颜色2重叠后会变成颜色3。颜色0不能用来擦除线条；请清空帧缓冲区或使用专用擦除函数。普通 `Wire3DCGB_DrawLine2D` 和模型绘制不会记录差分传输范围。若希望绘制线条时同时记录范围，请使用 `Wire3DCGB_DrawLineClipped2D`；若需要在下一次差分传输中包含整个视口，请调用 `Wire3DCGB_InvalidateFrameHistory`。

160 × 144模式每帧最多分配127个图块。高速线条绘制路径遇到图块分配失败或屏幕范围外的坐标时，`Wire3DCGB_GetFullScreenOverflow()` 会返回非零值，并停止写入像素，直到下一帧重新初始化。请将顶点限制在所选视口内。三角形遮挡掩码的右侧余量在128 × 96模式下最多扩展到X=127，全屏模式下最多到X=159。使用全屏或FastMap功能时，尤其要遵守API说明中的WRAM存储体映射要求。

## 10. 场景、对象池与弹幕
`scene` 管理标题、游戏、暂停等状态，`entity` 提供固定容量对象池，`chain` 保存蛇、列车、绳索的坐标历史。使用 `entity_get` 返回的指针前，先检查 0xFF 等分配失败值。

`danmaku` 提供定点弹池、定向和扇形发射、命中与擦弹。CGB 背景合成路径避开一般 OBJ 数量限制，但帧处理时间和背景传输带宽仍有限。应测量每帧处理时间，而不只追求弹数。

## 11. RPG、冒险、策略与保存
`rpg.h` 汇总随机数、标志、任务、压缩、文字、菜单、脚本、地图、保存、寻路声明，实现分散在 `rng.c`、`flags.c`、`rle.c`、`text.c` 等文件。按字典选择需要的实现单元。

固定 `rng_seed` 可获得可复现的测试序列。检查范围函数是否包含上界。`flag_get`、`flag_set` 操作位集合。`save.c` 采用 MBC5 式 SRAM 访问，ROM 头的 RAM 容量要与保存区域匹配。

`slg.h` 的棋盘、合法行动列表和撤销，以及 `slg_path.c` 的寻路，应与游戏专属规则和评估分开。宽、高、工作数组除了满足参数条件，还须符合库的上限。

## 12. 通信
`link.c` 提供串行字节传输，`link_packet.c` 是可选包层。先链接 `link_hwregs_gb.c`。轮询和中断模式需要不同调用；中断模式还要求游戏连接 0x0058 向量。

逻辑 `Link4_*` 与真实 Nintendo DMG-07 的 `LinkDmg07_*` 是两套不同系统。DMG-07 使用外部时钟，应频繁调用 `LinkDmg07_Poll`，每帧调用一次 `LinkDmg07_TickFrame`。每帧只轮询一次可能达不到时序要求。使用 KOKURA pair/dmg07 工作时，应分别测试连接、启动、断开和重连。

## 13. Bank、素材与调试
`BankPtr` 同时保存 bank 编号和指针；`far_data_read` 将其他 bank 的素材读入 RAM。asset 为 ID 关联描述符，数据寿命、bank、大小仍由游戏负责。

`debug_trace_u8`、`debug_trace_u16` 把值记入 RAM，`debug_assert_fail` 记录诊断码。这不是向 PC 控制台输出的 `printf`。请通过模拟器内存观察查看记录。`gb_debug.c` 记录 HP=42。

`vram_get_queue_capacity()` 返回命令队列的总槽位数（默认为32），`vram_get_queue_free()` 返回空闲槽位数，`vram_get_queue_used()` 返回已用槽位数。无论传输多少数据，一项排队操作都占用一个槽位。这些函数查询的是传输队列的容量，并非实际 VRAM 中的空闲空间。
