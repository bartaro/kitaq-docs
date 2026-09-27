## 1. 选择需要的组件
`fc.h` 汇总声明，`core.h` 定义类型，`intrinsics.h` 声明编译器操作。普通 C 库函数需要对应的 `.c` 实现；仅头文件宏和内建函数未必需要同名源文件。

{{CODE:0}}

不要把 `-I` 指向名字相似的 GB 库。例如 NES 的 `__oam_dma()` 无参数，GB 的同名操作却接收指针。

## 2. Runtime 与 system
`runtime.c` 为 PPU 寄存器、OAM 影子缓冲及 VRAM 队列提供 C 辅助函数，也存在 `__vramq_*` 等内建路径。先确认 NMI 实际消费的数据，不要混用同名或近似名称的独立队列。

`system_init` 初始化帧状态并启用 NMI。`system_wait_vblank` 等待 NMI，递增软件帧计数，再同步调用已注册回调一次。向 `system_set_vblank_callback` 传零可移除回调。回调在等待函数的调用方上下文中运行，不在 NMI 处理程序内部。

## 3. PPU、图块、属性与调色板
`ppu_direct.h` 提供直接 PPU 操作，`vram_queue.h` 用于 NMI 更新，`tilemap` / `nametable_asset` 管理表与素材，`attribute` 更新属性，`palette` 管理调色板。初始加载与每帧处理应分开。

背景和精灵调色板各占 16 字节。值是 NES 颜色编号，不是 RGB 分量。属性为一组图块选择颜色，改变某个图块的视觉调色板时可能也影响邻近图块。

`ppu.h` 和 `ppu.c` 提供画面控制、32 字节调色板传送及完整名称表初始化。`nes_ppu_seek_bytes(hi,lo)` 重置地址锁存器，并用两个字节设置地址。可与 `runtime.c` 中接收单个字参数的 `nes_ppu_seek(address)` 一起链接。传送和初始化前请关闭渲染。

## 4. OAM、组合精灵与轮换显示
NES 最多有 64 个精灵，通常每条扫描线最多显示 8 个。九个以上敌人或子弹集中在一行时，无法同时全部显示。组合精灵用多个 OBJ 拼成一张图像；请检查分配边界和终止标记格式。

`oam_fair.h` 与 `oam_fair_impl.h` 在保留优先级的同时轮换候选顺序。例如让玩家和 HUD 优先显示，较不重要对象轮流显示。重排 OAM 不会改变硬件扫描线限制。

## 5. 输入、连发与外设
`input.c` 把 NES 原始按钮值转换成 GB 风格的 `BTN_*` 掩码。**NES 原始 A 是 0x01，库的 BTN_A 是 0x10。** 不能将 BTN_A 直接传给 KUROSAKI 的 `--pad1`。

`pad` 读取基本输入，`input_repeat` 处理长按重复。`zapper`、`keyboard`、`rob`、`mic`、`midi` 提供底层外设接口。未连接设备时读到 0，并不能证明操作成功；应检查该设备的连接要求。

## 6. 声音
`audio_vblank.h` 提供由 NMI 驱动的四通道音乐。其参考条目说明 RAM 队列补充、音符保持与停止、循环播放，并附完整示例的录音。

调用 `nes_apu_init` 后，可通过 `nes_sfx_square1`、`nes_sfx_square2`、`nes_sfx_triangle`、`nes_sfx_noise` 使用内置音源。period 参数是硬件计时周期，不是赫兹频率。`fc_sound.c` 是最小脉冲音示例。

DMC 样本受地址、长度、对齐和速率限制，传递指针前应查看映射布局。DMC DMA 还可能干扰手柄读取，应同时采用安全读取方式与 KUROSAKI 诊断。

VRC6 提供额外脉冲及锯齿波通道，VRC7 提供 FM 寄存器，FDS 提供波表音源。使用匹配的 mapper 并记录结果。这些 API 与 GB 的 `Audio_*` 驱动不同。

## 7. 场景、actor 与 entity
`actor` 和 `entity` 在固定数组中保存游戏对象，`scene` 管理场景状态。必须检测容量用尽，并停止使用已销毁的 ID。场景切换、更新和绘制会同步调用已注册回调。请检查各 API 的调用顺序和重入限制。

`chain` 通过 `ChainBody` 提供关节跟随，通过 `Chain` 保存位置历史；`collision` 判断矩形等形状的接触。保持“移动、碰撞、绘制”的固定顺序，可避免碰撞结果落后一帧。

## 8. 数学与物理
`fixed.h` 提供 Q8.8 运算，`math_fast` / `math_fixed` 提供数值操作，`math_lut` 提供查表计算。`physics2d` 处理方框积分、重力、AABB 接触和表面响应；`physics3d` 处理不旋转的三维方框、反弹和冲击值。分配 world 和 body 数组，初始化并设置参数，再调用 step。位置和速度使用调用方选择的一致整数单位。

Q5.3 的小数单位是 1/8 像素。请分别保存整数坐标、小数部分、速度和方向，在游戏代码中完成加法与进位。`fc_subpixel.c` 将 2/8 像素累加八次，从像素 40 移动到 42。不能把 Q8.8 中的 256 原样当作 Q5.3 的 1。

## 9. 素材、mapper 与 FDS
`bank`、`asset` 描述 PRG bank 和素材。`mapper.h` 的操作是否有效，取决于构建时选择的 mapper。滚动 IRQ 的配置、开启、应答和关闭应作为一套完整流程设计。

FDS 服务分布在 `fds_file`、`fds_overlay`、`fds_save`、`fds_sound`。载入覆盖模块会替换已有地址的代码，因此必须考虑返回地址和数据寿命，不能假定等同于普通卡带的远调用。

## 10. 参考条目与示例
下方字典依公开头文件整理，区分函数、函数式宏和别名。完整头文件还包含结构体与常量。各条目分别说明具体实现、调用条件和验证范围；编译器内建函数的实现由编译器生成，不要求同名 C 函数体。源码注释保持原文，以便准确对照实现。

`vram_get_queue_capacity()` 返回命令缓冲区的总容量，即128字节。`vram_get_queue_free()` 返回剩余字节数，等于总容量减去 `vram_get_queue_used()`。这里统计的是包含地址等管理信息的命令大小，并非实际 VRAM 的空闲空间。写入单个图块需要4字节，填充需要5字节，通过指针复制需要6字节。commit 后 NMI 可能消耗队列内容，因此请在 commit 前检查剩余空间。
