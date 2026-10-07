# W6 最小充分实验与一次采集复用计划

日期 2026年10月5日 UTC

## 结论与使用方法

当前最合理的路线是先完成窄域可识别性和可实现性检查，再做独立确认；不要一次安排 GPU、模型、长度、cap、温度、并发、网模型的全笛卡尔积。现有 CPU 结果已相当充分，新增主要缺口是同次真实采集、有效执行合同、强基线下的完整周期和匹配服务质量。若这些缺口无法闭合，仍可完成有明确边界的理论及模型论文。

本报告只做规划，没有执行新科学实验、GPU 查询、模型请求、cap 写入、仪表采集或 Codex 任务。既有历史结果均来自已存在的文件，本次仅阅读与记录。完整 38 项实验的输入、输出、门槛、依赖、硬件等级、实现状态与失败转向见 EXPERIMENT_MATRIX_ZH.md；CSV/JSON 为同一矩阵的机器可读版本。

执行依赖以 ROUTE_PLAN.json 为准，共五个独立路线。矩阵的 depends_on_by_route 覆盖基础依赖，conditional_dependency_gates 随声明触发；GPU_ONLY 的 I11 核心仅 I03/I05/I07，不需要 DC。只读 I09 可选且有独立非 DC 依赖。CPU 新模型的 N01 从 F03/N03 与声明模型输入开始，不经 I11；硬件参数版本则先通过 I11。C01/F04/C02 是 DC 主路线。Z01 必须逐项审计所有已选必要 ID 的终态，不能只检查 F02/F03。

MUST 表示所选声明成立必须做；CONDITIONAL 只在要保留对应更广声明时触发；OPTIONAL 不应阻塞主要路线。没有做的分支标记 NOT_APPLICABLE_BY_SCOPE 或 BLOCKED，不能标记通过。步骤规划不是硬件操作授权。

## 1 按论文声明选择闭合路线

### 1.1 理论与固定模型论文

必需 F01–F03、N03、Z01；旧模型和更正只核验，新的控制参数或新理论合同才触发 N01/N02/N04。主贡献应保持“完整恢复域约化与 sharp hazard 凸性”的联合窄结果，网侧部分保留正序兼容条件、变号核反例和充分安全子类。独立证明和明确失败边界比增加几十个同质仿真配置更有价值。

此路线不需要 GPU，不允许以无实测为由把公开 trace 拼成标定。若不主张严格机器数值证书，O01 向外舍入可选；解析证明、精确有理可行性、普通浮点评值、高精度反例必须分别标记。

### 1.2 仅有 GPU 的记录域验证

执行 F01–F03、I01–I03、I05、I07、允许范围内的阶段/上下文只读检查，最后 I11 与 Z01。可测 NVML 记录域功率/能量、客户端或 host-engine 可见事件和性能；必须把仪表/事件来源写明。没有 DC 和 device 时间不强行走 I06/C01 的严格 DC 路线，也不能宣称连续 actual-power slew、device EOS 或物理 burn 合同成立。

若要比较 recorded-domain energy，另冻结该有限声明的同边界对照和统计方案；其结论不自动成为 W6 DC 最优控制验证。模型权重、精度、engine、采样、phase/context/batch、GPU UUID 均固定，不把 cap 数字当实际功率。

### 1.3 GPU 加经标定 DC 的真实控制论文

核心闭合为 F01–F03 → I01–I11 → N01/N02/N04 → C01 → F04 → C02–C05/A01 → Z01。只有 engine/device EOS、实际控制与恢复均可实现，才进入真正 W6 策略确认。A02 只做最有辨识力的 1–2 个实体组件消融，安全保护不可删除。要声称跨 workload/model/device 才分别触发 X01/X02/X03；单卡单模型论文可以明确只覆盖这一窄域。

### 1.4 PCC 与真实网侧论文

在 DC 路线基础上补 G01–G04；设施阈值、真正 PCC、同步映射、网态/尾部、模型误差都是独立必需证据。若仪表一开始可用，应在 I06/I08/C02 采集时同时记录 PCC，避免以后重复采一套相同 GPU 请求。GPU→PCC 可识别不等于 GPU→公用电网频率因果响应可识别；后者需设施/接入方验证的网络模型与误差证据。

没有该证据时，只能写“实测 GPU/DC/PCC 波形，加声明网模下的响应”，不能写“实测 GPU 降低真实电网振荡”或合规认证。只有更宽网络/非线性 claim 才触发 G05；连续任务、并发、长期平均吞吐或再生循环 claim 才触发 X04。

### 1.5 原 A–E 检查点保持原意

A 是最近先例非包含与有意义核心，对应 F02/F03/N03；B 是理论合同、证明与数值证书，对应 N01–N04 及可选 O01；C 是 PCC 与电网价值合同，对应 G01–G05；D 是可执行控制与真实测量，对应 I01–I11/C01；E 是冻结公平基线、独立确认、消融、迁移、误差与成本，对应 F04/N02/C02–C05/A01–A02/X01–X04。完整映射与旧状态见 CHECKPOINT_A_E_MAP.json。A–E 不是硬件等级，CPU/GPU_ONLY/GPU_DC/PCC 单独记录。

## 2 已经完成并应冻结复用的证据

1. 旧 GPU 工具软件记录为 39/39 单元测试通过、1,369 条示例 schema 检查、8 个 SIMULATED run。硬件执行各项为零。这些证明软件流程被测试，不能证明硬件合同。
2. round3 保存 12 个主要模型（10 个缩放等价类）、12 个迁移目标、6 个非零初态、8 个 synthetic atomic、2 个 Azure trace 模型。均是模型配置，不是独立部署样本。旧 hard-deadline 失败及权威更正保留。
3. round3 的 safe constant-target 加权目标改善约 0.198061%–1.694450%；与同信息 Bellman 的最大相对 excess 约 0.026014%。这不是战胜真正全局最优参照的证据。
4. 匹配平均 power-cycle 的 constant-target 对照只有 6/12 可行；另外 6 个明确不可达。在可比的 6 个中，模型动态能量差约 0.455453%–3.866496%。它不是匹配 p95/p99 延迟、hard deadline 或所有策略类的节能结论。
5. 网侧已有 1 个设计、8 个冻结确认配置、72 个理想 actual-power executor 组合、12 次支持函数 LP，以及 4 个 exploratory network cases。无需为增加样本数重复跑它们。
6. 同 cap 的对齐后 nominal 加权目标收益仅 0.000730%–1.401856%，robust 0.000148%–0.711037%。uniform mesh 曾出现 N256 比强恒目标差 0.040332%，最大 N128→256 变化 0.561157%；后续 knee-alignment 是另存的 amendment，不能替换原冻结结果。
7. 7/8 nominal guarded 配置的最坏峰发生在实际功率回零之后。nominal guard 在所测不确定性角点没有越限；不得编造 robust 防住了这些案例中的 nominal 失败。未加 guard 诊断真实越限计数为 nominal 3/8、uncertain 5/8。
8. robust 的代价真实存在：设计例成本溢价约 8.55%，确认例约 0.99%–33.52%。Kundur 高增益 tight-cap 情况，网格策略还比同 cap 恒目标差，bus7 约 0.001733%、bus8 约 0.000849%。
9. 广義 novelty 当前 FAIL，窄理论方向 CONDITIONAL。当前 admitted matched hardware captures 为零，公开数据不同时闭合命令、真实功率、进度、自然 EOS、恢复、PCC 和时钟合同。

以上来源见 SOURCE_LEDGER.json；均为旧文件中的已记录结果，本次未复算科学值。两个交付 ZIP 是普通可分别解压的主包与 NetworkData 补包；原 split QA 记录 520 个 payload 文件完整，第二包仅含四个原始 network-kernel NPZ 等相关说明。不得把第二包内容当新的真实网测量。

## 3 避免漏测的原始采集合同

### 3.1 一次完整 capture 记录全部未来可能复算的量

从 stable idle 开始，记录 model load/warmup 的边界，覆盖 request、prefill、decode、真实 useful EOS、controller 首次可见 EOS、控制命令、实际功率返回、matched thermal/clock/queue state、以及所需 PCC/grid tail。原始数据只追加，不覆盖；派生版本用 protocol/hash 区分。

每条记录至少带 acquisition_id/session_id/run_id/request_id、硬件/模型/engine 身份、source_clock_id、source timestamp、映射后 monotonic ns、arrival_ns、状态/缺失原因和证据标签。多设备原始日志各自保持时间序，不能全局排序掩盖 reset。真实字段缺失填 null/unknown，不填零。

保留以下独立通道：

- cap/控制命令 issue、return、ack、requested/configured/enforced 值、physical_effect 及失败；cap 不是实际功率
- 全 rails DC reference（若有）、NVML 原始 power/energy counter、温度、clocks、throttle reason、utilization、memory/KV、采样积分窗/滤波/校准/饱和/缺样
- device useful-completion、host-engine output、client chunk、token IDs 计数、phase、context、batch、queue 与 concurrency；chunk 不等于 token
- 自然 EOS/stop_rule/length/cancel/error/timeout/unknown、max_tokens、stop 配置、EOS token 依据、取消确认与残余执行
- warmup、冷却、power_return 和 matched-state criterion/hold 时间；state 不仅是一行“restored=true”，要有验证原始证据
- PCC 的 P/Q/V/I/f、UPS/电池/转换器 mode/state、background load；若仪器支持 waveform，保留原始量及转换定义
- 运行环境、独占证明、版本与配置 hash、每个 command exit/status、CPU/wall/GPU 时间、磁盘与人工步骤

NVML counter 是交叉核对量，不默认无误差。动态功率以实测 power 减声明 baseline 得到，负偏差保留并传播不确定度，不能悄悄截零让模型成立。传感器校准、计量边界和系统偏差不会通过增加请求数自动消失。声称连续 slew 需要独立带宽/regularity 或设备保证，不能从采样最大差分倒推出 R 再拿 R 证明采样间安全。

### 3.2 三个时间窗口必须同时保存

理论目标窗口：t_request_start 到 t_actual_power_return。保留原 W6 目标 J_W6 = E_dynamic,powercycle + c T_powercycle，c 的单位与权重意义明确。

部署完整复位窗口：t_request_start 到 t_matched_state；报告该 named boundary 的 gross 和 dynamic 能量，以及 useful latency、EOS visibility、功率恢复、热/clock/queue 复位时间。此窗口可能比原理论窗口长，不能偷换成已证的 J_W6。

网侧窗口：从共同初始网态到带有证据的 tail 终止。GPU p=0 后网侧可能仍处峰值，零 GPU 动态功率尾部不等于零 PCC/整机成本。若只观测有限时长，应报告 observed-window result 和独立余尾上界；无余尾上界则不能声称全未来安全。model load、warmup 与 whole-capture 总账另列。

## 4 最小 pilot 与逐关预算

### 4.1 先低成本排除不可行方向

先只读 inventory 和一次小请求；device hook、联合编排、取消检查、实际策略桥都需 CPU mock/dry-run 后才在批准范围进行实体验证。只读采集工具、cap API 与完整控制器是不同部件，不能把包中的 CLI 当成 turnkey W6 实验 runner。

DC 核心 pilot 从一个固定 stratum 开始：3 个独立初始化 session × 5 个可达控制等级 × 每级 2 次 = 30 episodes。至少一个随机顺序、一个逆序与一个重启 session，并包含上下沿和完整 EOS/恢复。只有实测功率差异可分辨的档位才算不同 levels；30 个 episode 只提供 3 个 session clusters。

然后增加最多 12 个预设 sentinel：两端代表控制水平 × 三个相邻条件 × 两次诊断重复，分布到 pilot sessions。相邻条件覆盖 prefill/decode、context、热/clock/KV 中最有辨识力的变化。可以从同请求的 phase 分段复用数据，但不能把相邻时间窗伪装成独立重复。若发现显著状态依赖，先选一个可用窄域，不立即对所有因素展开。

自然 EOS 与固定长度控制样例分开；错误/取消路径先 mock，再批准范围内最小验证。该预算仅为可识别性先导，不承诺足够估计 p99 或得出总体 safety 结论。三个 session 的方差估计很粗，应报告其不确定性，必要时只补独立 pilot sessions 来确定合理确认预算。

### 4.2 冻结后确认的数量由问题决定

先确定工程上值得区分的差异、允许的 QoS/质量退化和费用/时间上限。这些来自实际使用要求，不从预期收益或确认曲线反推。没有应用方阈值时，预注册估计和精度目标，不制造 3%、5% 等“必须过”的门槛。

对 paired session-level mean/log-energy effect，可用 pilot 的 session 差异方差进行规划；常见正态近似 n ≈ ((z_(1−α)+z_(1−β))σ_cluster/δ)^2 只能作为有前提的 planning approximation。正式 N 要考虑方差估计不确定性、集群结构、多个主端点、非劣限制、缺失和目标总体。p99/罕见失败往往比均值需要更多请求及独立 session；不能用此均值公式给 tail 结论背书。

每个确认 session 内应有足够任务估计其预设统计量，推断按独立 session/随机化 cluster 层面进行；跨日重启也不是无条件 iid 证明。报告 N_sessions、N_devices、N_prompts、N_requests 和 repeat 数，不能只给总请求数。目标只针对一张卡就限定到该卡和采集环境；随机效应推广需要实际设备层单位。

整 session 的采集角色要在该批 outcomes 前冻结；最终策略/分析在 confirmation 前再冻结。旧 fit-service 产物绑定整个 split 的 hash，calibration 后不能覆写 registry 来加确认样本再直接调用 evaluate-service。可在 C01 前预先冻结全部未来角色/预算，或先实现经测试的多阶段父子 manifest 链，分别锁住 calibration 和 prospective confirmation；不能删 hash 检查来绕过。

C01 最终标定可能改变 provisional controller/model/baseline 参数。F04 冻结前必须核对最终 artifact hash 与 N01/N02/N04 输入 hash；不一致时更新受影响的 development 数值检查，再冻结。保留旧版本且不将过时精度/robustness 检查用于新参数。

可选固定 N，或在预注册时明确 alpha-spending/group sequential/confidence-sequence 方法、观察时点和合法假设；普通 95% CI 每一批重看直到显著不合法。软件未实现可靠序贯推断时用固定 N。预算耗尽而不确定，结果为 inconclusive；安全/数据损坏可以停，但保留已分配尝试，不能自动补到全成功。

已有 59/299 是单一二元失败事件、95% 单侧、零失败时针对 5%/1% failure-probability bound 的 iid 示例；五端点 Bonferroni 示例为 90/459。它们不是总体能耗效应、分位数、hard guarantee 或任意队列场景的万能 N；有失败要用相应完整区间方法。

### 4.3 有边界地扩展

先回答实际主 SLA；需要前沿结论时，在相同声明域内最多选三档工程相关 QoS 点，设计期选择并冻结；不是 5 cap×所有长度×所有温度×所有策略全跑。核心策略通常先三种：原生 nominal、经相同 calibration 优化的 static cap/恒目标恢复、W6；只有最近强 adaptive 方法与当前合同相容时加入第四个。

先确认一个主 workload；只有论文声称迁移，才在完整留出的 workload/model/device 上测试。每次只扩一个关键轴，冻结 zero-shot 和 adaptation 的区别。独立设备不得用同卡不同 seed 代替。X04 队列/并发属于新合同，不应为了“看起来全面”强行放入孤立任务主实验。

## 5 公平比较与统计决策

各策略必须拥有相同截至当时可见的信息，不能提前看到自然 EOS、未来实际功率或目标生成长度。共享 prompt pool/seed 减少方差，但 GPU nondeterminism 可能改变输出长度或质量；不得根据已经观察到的长度重新匹配、丢弃不利输出，或把固定输出长度表现推广到自然生成。

static-cap/恒目标基线必须在独立 calibration 内全局或足够精确地优化；不得挑一个随意 cap 当弱对手。所有策略用相同硬件约束、终态要求、计量边界、允许采样/延迟与调参预算。Bellman 的 finite state/edge optimum 只是该离散可行类全局参照，不是自动的连续下界；要称下界必须有对应证书。clairvoyant oracle 如有，只作明确的信息松弛参照，不能列为可部署对手。

主要结果至少共同报告：

- 预定 named-boundary 完整周期能量效应与 CI；gross/dynamic 分开
- J_W6、useful/power-cycle/matched-reset time 分开，不把加权目标差等同节能
- latency 的 mean、p50、p95、p99，按场景记录 TTFT、ITL/TPOT、deadline-miss、吞吐/排队
- 完成率、错误/超时/取消/截断、输出质量；QoS 必须含尾部和质量
- 算法开销、恢复/冷却/尾部、一次性 calibration/solver 开销、可能的 amortization
- meter/systematic uncertainty、session sampling uncertainty、solver error、模型误差分别列出

“节能”主张应在预定共同可行 QoS/质量点上成立。相同 mean latency 不能替代相同 tail；目标点不可达应明确不可达，不填虚构能量。数值收益小于系统计量偏差或分辨率时，增加更多相关样本不会救回主张；结论可以是无可辨优势或工程价值有限。

所有 randomization assignments 都有 all_attempts terminal status。缺功率样本不能捏造 energy，但必须留下失败分母、原因和按策略缺失率，进行预定敏感性分析。准入失败可阻止使用坏数据计算某数值，不得让该请求从可靠性/QoS 总体中消失。若故障改变工作量/质量，优先报告 tradeoff，不“清洗”成成功样本。

## 6 消融和压力测试如何少跑仍完整

同一 raw 可以复算 task-only/full-cycle、host-visible/device EOS、不同计量误差预算、合法积分方法等会计与观察口径，不需再占 GPU。downsample 高分辨 raw 可诊断采样影响，但不是不同物理传感器的实测。

修改在线 controller、改变 EOS 可见延迟、删除恢复-aware 逻辑等反事实会改变真实轨迹，不能从一次观测声称另一实体策略已经测过；需要模型重放（标 simulated）或另开少量预留 ablation sessions。去 guard、超限或故意破坏联锁仅在仿真中，不应在硬件执行。若可执行消融不安全或违背合同，写明不适用。

模型层压力优先覆盖服务/执行误差边界、EOS delay、sample interval、clock uncertainty、非零初态、law shift 和 grid kernel sign/tail，采用单因素及预定关键交互，避免全乘积。sharp hazard 临界附近、atomic vs continuous、hard deadline、signed-grid nonconvexity 已有理论与数值证据，先复核；新模型范围才增做。

## 7 当前可调用工具与缺实现项

现有可直接复用的入口包括 telemetry/request/cap-session dry-run、import-meter、freeze-split、validate、analyze、fit-service/evaluate-service、budget，以及 CPU 理论/全局基线/guard/executor 程序。特别限制：

- request 只是受限 localhost SSE client，finish_reason=stop 被保守标 stop_rule/censored，true_eos_ns=null
- record_engine_progress 是 host output token-count hook，不能替代 device completion
- cap-session 只做有界 API 调度与原 cap 恢复，不能执行 workload、W6 连续功率控制或 burn
- import-meter 只按调用者给定 transform 导入，不创造仪表标定或时钟认证
- fit-service 是区间均值 OLS 与经验 secant 检查，没有点态因果服务律、硬包络、hazard 估计或控制器学习
- evaluate-service 只输出冻结模型残差，没有总体 inference、QoS tail/noninferiority 或 guard 发证
- validate --purpose w6-dc/pcc 是声明性数据 gate，不是物理准确性或安全认证

旧 core.py 对所有 power_W/baseline_W（包括 pcc_active）要求非负。含净回送的 PCC 需明确正负方向并新增版本化 schema/adapter 与测试，不能取绝对值、截零或删除 gate 冒充兼容。无 transfer 行时，registry 可保留 truthful device/model_family 轴且不作迁移声明，无需为 no-transfer 新增 none；同卡同模型 workload transfer 才需要明确扩展。

IMPLEMENTATION_LEDGER.json 将每个已有源文件与缺实现任务分开。未来 Codex 首先实现和单测缺部件；不得发明现有 CLI 能做尚未实现的功能。生产使用前需要操作人范围、实际硬件支持、恢复 readback 和独立安全保护。

## 8 输出目录与一次采集多次分析

每个新 study 独立根目录，不覆盖现有交接包。以下旧语义目录是逻辑别名；实际物理目录严格采用 prompts master 的 00_inventory、01_protocol、02_code、03_calibration、04_raw、05_derived、06_figures、07_audit、08_delivery。OUTPUT_PATH_MAP.json/csv 已将矩阵全部 127 项 logical_name 映射到 canonical_relative_path，矩阵另含 canonical_required_outputs。采集 raw 统一落 04_raw/<tier>/<stage>/<session_id>/<run_id>/<attempt_id>/，相同 acquisition 只存一次，其余实验引用 hash。规划中的模板不是已经存在的结果；真正运行后必须展开并逐项验文件/hash。

下列逻辑别名只帮助理解内容分类，不能再生成与编号目录冲突的第二套结果：

- protocol/：claim_scope、operator_inputs、preregistration、frozen registry、analysis plan、hash/外部时间戳
- software/：代码 commit、环境/dependency lock、tests、dry-run、adapter 版本、CPU/GPU 执行计数
- hardware/ 与 calibration/：安全范围、仪表/clock/service/actuator、model 和 policy 冻结件
- raw/acquisition_id/：原始各源文件、immutable manifest、NVML、engine/device events、commands、DC/PCC、queue/thermal 与同步 markers
- derived/version_id/：标准化 power/events/commands、per_request/per_cycle/per_session、派生 spec/hash
- confirm/、ablation/、transfer/、grid/：严格分 role 的结果与 protocol，不复制改名 raw 冒充新采集
- analysis/：全部 attempt/attrition、effect/CI/feasibility、QoS 前沿、missing sensitivity、数值与计量误差分解
- accounting/：实际 wall/CPU/GPU 时间、采集/离线/在线成本、storage；费用 unknown 就保持 unknown
- evidence/：CLAIM_EVIDENCE、FAILED_AND_INCONCLUSIVE、limitations、原始更正和 prior hash
- README_ZH.md、FINAL_STATUS.json、REPRODUCE.md、MANIFEST_SHA256.json、file index、最终表图/正文

CSV 用明确单位、UTF-8，JSON 禁止 NaN 并保留 null，高频 raw 可用 JSONL/Parquet/压缩 CSV（带 schema/时间域）；NPZ 只存数值数组并附单位/索引。每个结果包含 experiment_id、evidence_tier、status、protocol_hash、source_hashes、code_hash、population/split、N_clusters/N_requests、estimator/CI、limitations。figure source-data CSV 必须与图绑定。

复算命令默认只读 raw，不访问 GPU、不请求服务、不写 cap。采集命令默认 dry-run；真实动作独立显式开关与获批配置。新 package 内的计划文件或空目录不算完成，status 应准确列 completed/blocked/not_applicable/planned。

## 9 必须暂停或改写主张的情况

缺 device EOS 时暂停真实 EOS/迟报合同；缺全 rail DC/时钟界时暂停 actual-power/连续 slew；scalar s(p) 被 phase/context/thermal 反例推翻时改为条件模型或限定域；burn/恢复不可物理实现时改执行合同；自然长度受未知截断时暂停自然 law 结论；强基线相同 QoS 下无收益时保留负结果；差异低于系统误差时不要盲目加 N；PCC 映射不识别时保留设备级结果；grid state/tail 无界时不宣称全未来网侧安全。

达到冻结预算但效应不确定可以结束为 inconclusive，不要求“跑到赢”。任何修改不得把已看过的 confirmation 再包装成 untouched；保留 v1 结果，新 v2 使用新未来完整 sessions。完成所有选中脚本也不能自动宣称 paper-ready，最终由 claim–evidence 审计决定能写什么。
