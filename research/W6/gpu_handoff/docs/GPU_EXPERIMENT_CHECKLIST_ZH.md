# GPU 实验工作清单：拿到机器后按关卡推进

状态：2026-10-04 交付的是可运行采集/分析脚手架与 CPU 合成测试。真实 GPU、真实服务、DC 仪表、PCC、电网实测均未执行。GPU 硬件兼容性与测量充分性仍待检验。先做最小识别，缺关键通道就停，不直接开始“节能结论”实验。

## 0. 最低硬件/权限清单

- 单张独占 NVIDIA GPU；记录型号、UUID 的 SHA256、显存、驱动、固件、MIG/vGPU 状态。若分区/虚拟化改变测量边界，先拒绝整卡推断；不得将其他租户负载并入本任务
- 模型与 tokenizer 的本地路径或已启动服务、revision/hash、精度、engine 版本、CUDA/runtime 版本、采样设置、停止规则；用户自行准备权重，工具不下载模型、不安装驱动
- 主机 CPU、PSU、供电拓扑、时钟来源/boot ID、传感器与 engine 是否同一 monotonic 域、磁盘容量和日志位置；不用 wall clock 直接计算短间隔
- 已获机器管理者允许的 cap 范围、设备原始 cap、温度/错误停止阈值、冷却策略、最长实验时间、人工停机与恢复方法；示例 100–150 W、75°C 仅占位，绝非通用安全值
- 若有 DC 仪表：合格人员安装；全部必要 GPU rails、量程、带宽、抗混叠、标定证书、时钟同步、误差上界、触发标记与安全隔离
- 若有 PCC：由设施电气人员确认真正边界、仪器量程/绝缘/校准、P/Q/V/I/f、UPS/电池/转换器模式、背景负载。禁止自行接入带电线路或在生产设施随意激励

## 1. 三种资源等级，结论严格分开

### A. 只有 GPU 与已运行模型服务

能做：只读 NVML 能量/功率/温度/时钟；命令 API 延迟；客户端 chunk/finish reason；引擎输出 token IDs 的 host 可见时间；隔离任务的完整遥测返回。可描述记录域能量和服务相关性。

不能做：把 cap 当 actual p；用 NVML 相邻差分证明连续 slew；给出自然 EOS 的 device 时间；把 1 秒平均读数的高频轮询当物理带宽；证明真实 burn 或 DC/PCC 安全。用 `validate --purpose descriptive`，不应通过 `w6-dc`。

### B. GPU + 经标定的外部 DC 参考仪

新增：同一任务、同一时钟变换下的全 rail DC 功率与不确定度；实际功率区域、干预响应、NVML 滤波差异、全周期能量。engine/device 完成 instrumentation 经验证后，可分解 true EOS、controller 可见延迟、命令延迟与物理返回。

仍不能做：GPU→PCC 映射与电网频率结论。即使本套件 `w6-dc` 声明性字段检查通过，也不是硬件认证。传感器/时钟/actuator/envelope 的证据仍须人工审计。

### C. 以上 + 同步 PCC / 电气仪器

新增：在获准的设施模式与激励范围内识别 ΔP_PCC = g*p + eP，记录 Q/V/I/f 与背景负载；用实际电气拓扑解释边界。整机 AC、rack AC 不自动等于设施 PCC。

网侧约束观察到 GPU p=0 之后完整零输入尾部；须有稳定衰减/尾部误差证据。仅有有限窗口图不能证明全时域安全。0.05 Hz 是模型研究预算，不应写成当地监管标准或用户设备允许值。

## 2. 阶段 I：识别 / 可证伪 pilot

1. 固定 GPU/model/precision、phase、context、batch=1、单任务无并发，禁用会混淆条件的投机解码/动态 batch，或把它们记录成不同 strata
2. 先稳定 idle，单独记录模型加载和 warmup。记录 warmup_start/end；warmup 不悄悄进入 primary inference 能量，但必须另报 capture 总能量
3. 至少五个安全可达控制等级，含 nominal 与低端。每次都测实际功率，不同 cap 却同一实际功率不能算多个功率等级
4. 三个独立 session：随机顺序、反向顺序、重新初始化 session；每等级每 session 至少两次独立初始化。共 3×5×2=30 plateau episodes；同一 session 内仍聚类，不能当 30 个独立确认样本
5. 每次包含 idle→请求→真实/可见 EOS→实际功率返回→热/时钟/队列匹配→cooldown；记录上/下跳和自然 EOS 全周期。停止后不自动加 dummy load，不启动下一任务伪装恢复
6. 自然 EOS、固定输出长度、最大长度截断、取消、超时、错误分开。记录 max_tokens、stop string/token 规则、ignore_eos、EOS token 证据。仅 `finish_reason=stop` 不够
7. 至少一个相邻 context/phase 作为预设反例检查。若 s 受 context、温度、phase、KV 影响，使用条件模型或拒绝标量 s(p)，不得强行拟合成凹函数
8. 先过 provenance/time/rail/coverage/完整周期 gate，再做诊断拟合。本套件仅提供 interval-mean OLS 和经验 secant 检查；没有因果/点态/硬下包络证明

停止条件：缺失/漂移时钟、饱和/漏 rail、power 不可控、并发混入、无有效服务下包络、真实 return/burn 不可实现、目标 PCC 通道缺失。失败本身是有效研究结果，不用别的数据拼成一次实测。

## 3. 阶段 II：冻结后确认

- 完成 pilot 后，冻结算法、同信息 baseline、工作量分布、初始/终止状态、full-cycle primary endpoint、cap/实际功率范围、误差预算、处理规则、停止规则和代码 hash
- pilot 永久归 development。对未来完整 session/run 分配 identification/calibration/confirmation；不得随机拆行、token、重叠 window。保存 registry 原件与冻结 hash
- calibration 只选诊断模型与不确定度；confirmation 不参与调参。测试失败或不确定后修改，只能另取新确认样本
- 两策略用相同任务/初始状态、已知信息和完整成本界；随机策略顺序，按 session 分组。自然生成随机性应预先控制并记录 seed/采样；不能借未来 EOS 给 baseline 或控制器
- 示例 iid 零失败预算：单一预设二元失败事件，95% 单侧置信，失败概率上界目标 5% 要 59 iid 单位，1% 要 299。五端点 Bonferroni 分配分别 90/459；前提不成立就不使用该表
- 一次 full cycle 的回报分别报告 useful latency、EOS visibility delay、actual power-return time、matched-state reset time、gross/dynamic energy、恢复能量、grid tail。不能只比较 productive 段

## 4. 阶段 III：消融与迁移

- 消融：去掉回收约束、把瞬时 EOS 换实测可见延迟、移除网侧 guard、改变误差预算、固定 cap baseline；仅在独立标注的 ablation 样本上运行，不回写主确认结论
- 迁移：整块保留新物理 GPU ID/模型族/phase/context/session。分清“同 GPU 新工作负载”与“跨硬件”；本工具 registry 强制选择 transfer_axis=device 或 model_family，按真实 device_id_hash 或模型族保留整组；device_model_unit 还核验联合身份。需人工确认模型族归属
- 对新区间/新温度/新电气模式，原有包络不外推。若重标定，称 adaptation，并重新冻结确认数据
- GPU-only 与 DC 结果不能迁移成 PCC 实测。网侧模拟与硬件记录始终使用不同 evidence 标签

## 5. 安全停机与不支持事项

- 所有采集命令默认 dry-run；cap 额外需要 `--execute-power-control`、显式 operator_reviewed、独占确认、UUID hash、设备和操作者双重范围
- 工具不提权、不调用 sudo、不自动改权限、不改电压/频率/安全设置，不写凭证，不安装驱动，不运行 burn/stress 工具
- cap 控制限于不高于会话原始 cap，最后恢复原始值；SIGINT/SIGTERM 与普通错误走 finally。SIGKILL、断电、驱动挂死、丢卡无法保证恢复，必须人工检查。恢复失败会明确失败退出
- 该简单 cap 调度器不是温控联锁、安全系统、W6 连续 slew actuator 或生产调度器。温度轮询存在延迟；生产环境需既有独立硬件保护和经批准的操作规程
- 本次无 GPU，硬件兼容性、engine/device EOS hook、仪器驱动与设施测量仍未验证。没有把 mock 成功写成实测通过
