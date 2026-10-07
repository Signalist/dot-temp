# Gate1 guard 独立接口审计

日期：2026-10-02 UTC。审计仅限静态代数样本与函数级测试，不执行物理轨迹、六闭环或新策略。冻结协议 SHA256 为 `be681761f993c6beaefaca0a54ece73dc2e3263d56b5b7f869ab476e87c96fa3`。

## 当前审计状态

结论：`PASS_FUNCTION_LEVEL_ONLY`。独立代数与9组函数级测试均通过；所检查接入路径未发现阻断项。六个物理闭环模型在本审计中均未执行，接口通过不代表六门完成或安全/服务资格已建立。

## 1. 独立数学与存档检查

`audit_algebra_oracle.py` 不导入 guard、Gate0 solver 或物理积分器，采用独立复数公式重算全部量。运行结果存于 `audit_algebra_results.json`。Gate1/Gate0设计、原参数、checkpoint 的冻结hash均逐项核对。

- 结构化原存档计划独立复算最大 primal 残差为 1.6653345369377348e-16，含全10拍动力学、全部电流节点、queue、新input、终端、初态Ω与首实际命令
- 宽合同失败产物独立重算最大违规为 1943.3890296439702，明确拒绝。该失败产物没有作为命令或备份使用
- 明确区分 q̄（本拍旧队列）与 m̄（本拍新命令）；二者相差一个采样期的旋转，不能互换
- Ω逆见证使用 w₁=e_q/(Ki·exp(−jωTs))、w₀=e_i−a·exp(−jωTs)w₁，显式报告两个圆盘范数与重建残差
- 已构造电流/queue各自在投影半径内、但不属于Ω的相关性反例：两个见证范数为 .2327761664 与 .07774806424，前者大于 r=.08638673804。因此两个投影圆的笛卡尔积不能替代Ω准入测试
- 独立人工代数状态覆盖 j=1、j=N−1=9、j=N=10；前两者取同索引 z_j/v_j，后者取 s̄/m̄。各自测试当前帧输出与下一拍queue帧旋转，不产生任何物理轨迹
- 将当前测量整体旋转 .73、−2.17 和 π rad 后，仍以当前 i、PCC、Vdc、旧applied反解源相量。未用绝对仿真时间恢复相位
- NaN输入、损坏终端与损坏queue计划均被独立checker拒绝

这些是双精度数值一致性测试。它们既不证明采样点之间的真实物理轨迹，也不提供严格外向舍入证书。

## 2. 必须满足的实现接口

1. 在接入时刻以当前电气测量锚定初相，随后只按固定60Hz合同和样本索引推进；不读干净源相位、事件或未来波形
2. 在任何队列提升之前取样。guard状态中的 q 是旧queued；本拍新命令只替换新queued，原保持段不可重写
3. 原Q优先PI名义输出、PLL、源指令均按原冻结公式计算。guard=m_nom时应逐字段复现原sample；guard改动时仅把相同Kaw回算中的新饱和电压替换为 Vdc·m_safe·exp(−jθPLL)
4. 优化器返回状态与primal可行性须独立记录。每个候选必须有限、通过独立全计划检查、当前Ω逆见证和domain/contract检查，并满足实际新调制范数
5. 保存计划包含origin sample/phase、完整z/v、证书版本、残差与backup-ready语义。移位备份使用 j=k−k₀，终端备份从j=N开始，不重用z₀/v₀
6. 失败产物拒绝后才能查可用备份；没有合法备份时停止并保留完整原状态/队列，不能将原PI、零电压或随机输入标成安全回退

## 3. 保留边界

- 所有RPI/终端推理仍依赖理想实数关系、Vdc和固定电源合同；没有联合DC/SoC不变性
- 数值终端容差与1e−8储备不等于严格外向舍入或完整浮点误差包络
- 初态健康干预 .214580692240 必须完整保留；接口通过不代表服务透明、健康服务保持或新策略优越
- 冷启动SLSQP wall time只描述该固定实现；不能据此推断成熟MPSC方法的性能极限，也不能声称满足100μs实时期限
- 本审计不变更 current_guard_qualified 或 paper_ready 状态，不替代六个离线模型门及其准入规则


## 4. 最终实现审计与函数测试

本节是接口实现完成后的最终补充。测试文件 `audit_interface_tests.py` 使用上述独立oracle核对，不执行 `rhs`、`solve_ivp`、`run` 或任何物理推进。除了每次套件执行中的一个冻结初态冷启动SLSQP点，其余优化异常情形均采用函数级返回值注入；人工代数状态不是新的物理条件或故障轨迹。为开发、补充测试与最终验证执行套件，不构成优化重启或参数搜索。

### 4.1 信息与坐标

- `CommonGuard.observe` 严格限定五项输入：当前 `i_ab`、`vp_ab`、`vdc`、旧 `applied_ab`、旧 `queued_ab`。额外event对象被拒绝
- guard参数字典只保留非bool数值标量；原case registry、事件结构与其他嵌套元数据不会存入guard对象。源波形标量只在传感器适配层用于生成当前测量
- 初相由上述当前电气量反解；后续使用初相加 ω(t−t₀)。非零 .73 rad 锚点及1/9/10/500拍分别检验通过，未以 ω·绝对时间代替源相位
- 当前PCC向量直接给定，因此实现没有P/Q除以零电流的奇异性；零电流静态观测测试通过。源幅值超合同或相位偏离时拒绝domain
- `z_j/v_j` 保存于各自未来样本的同一个因果旋转坐标。新输入在当前源相位下回转至αβ，而进入下一拍queue状态时多一项 Rot(−ωTs)；两者未混用

### 4.2 队列、原控制与抗饱和

对冻结checkpoint及另3个孤立静态电气/控制器样本，令guard返回原 m_nom，完整controller字段和返回值逐项与冻结原Q优先 `dq_bench.controller` 对比，最大差为0。没有物理状态变化。

- 当前量测、PCC/逆变器功率、源指令和PLL均取队列提升前旧状态
- 新applied恰为旧queued；guard仅替换新queued。旧applied用于当前测量，不被当作新保持段
- 三类返回标签（optimized、shifted_plan、terminal）均检验同一Kaw回算：δzi=Ts·Kaw·Vdc·(m_safe−m_nom)·exp(−jθPLL)
- 源指令、PLL与其余原sample字段保持原更新；Ki误差项未替换，未重置PI/PLL
- 强制GuardFailure时原ctl与y均完全不变，异常未被吞掉。没有默认旧PI、零电压或随机fallback

### 4.3 独立primal与失败注入

直接物理公式的 `validate_plan` 与优化提升矩阵分离。它重算Ω逆见证、完整动态、所有固定节点、queue、input、终端及首实际命令。

- 保存结构化计划及一个固定初始化SLSQP点均通过独立oracle
- 损坏input、queue、current、terminal，以及NaN候选均拒绝
- 将既有宽合同巨大残差产物注入优化返回值，即使伪造 `success=True`，也因primal失败拒绝；合法seed通过当前状态验证后才被选用
- `success=False`但primal可行的注入候选明确记 `accepted_suboptimal=True`，并不把solver状态当作可行性证明
- 无有效seed/backup的孤立不准入状态抛出 `lost_certificate_no_valid_backup`；Vdc失域在调用optimizer之前拒绝
- 代码没有静默终端尾部修正；`terminal_tail_correction_applied=False`。近等式仍属于数值判定，保留第3节严格性边界

### 4.4 计划移位、来源和拒绝路径

强制求解失败后，j=1、9、10、13的返回命令均与独立复数公式一致。1/9使用同索引计划项，10/13使用终端项；负索引和Ω外误差被拒绝。非零初相下αβ输出旋转正确，输入observation字典不发生修改。

初版实现曾缺少计划phase/certificate/residual/ready记录，经审计指出后已在新接口代码中补齐。最终测试确认保存 `origin_k`、phase锚点、origin frame、证书版本、完整primal validation和backup-ready；未ready、证书不符、相位/时间锚点被篡改的计划全部拒绝。另在第7拍静态fixture接受计划后，第8拍backup正确使用 j=1，而不沿用初始origin。

### 4.5 数值与用时记录

本次最终套件的独立SLSQP计划最大primal残差为 2.2204460492503131e-16；健康首命令改变量范数为 0.214580692240357，未为缩小它而改变参数。

该次setup/solve/validation/point-total wall time分别为 0.001420463、0.012549196、0.001064162、0.015033821 秒。超出100μs是当前固定冷启动离线实现的观测，不能推广为成熟MPSC算法或优化实现的极限。guard调用总时间在输出准备完成后更新；wrapper完整sample用时仍需由模型driver单独记录。

## 5. 复现、文件与最终边界

在G3根目录执行：

    .venv/bin/python current_guard_gate1/audit_algebra_oracle.py
    .venv/bin/python current_guard_gate1/audit_interface_tests.py

`py_compile`亦通过。结果分别写 `audit_algebra_results.json` 与 `audit_interface_results.json`。本审计未修改冻结协议、原参数、checkpoint、原控制器或旧结果。

本次最终源文件hash：

- `common_guard.py`：`89e47d8429f893d09c2fd7cac5a38de360e76d7dc225ad5e0eb940b1a96fbe03`
- `guarded_controller.py`：`9379032e4edc99a204ce0db3947e61f71dee30b8a876dce0d5740312bfda4af5`
- `audit_interface_tests.py`：`3ea62339be08d21a60db5373f7d0e3be6e0b5be94e57a0fde89494994d57d6fd`
- `audit_algebra_oracle.py`：`de339bc42b1d833e9b11ba4f044bee4890d5e11c77f095b4e2e7330c20b0e2fb`

最终结论限于批准的函数接口：所需非轨迹接口检查已通过，支持按已获批的冻结顺序开展六个离线模型门。这里不声称门C0/C50/C1已通过，不改变原慢源能量矛盾，不提供联合DC/SoC不变性、机器严格舍入、100μs实时性、服务透明性或全装置认证。动态波形/相位扫参及新P/Q策略均未执行。

## 6. 后续模型记录状态更新（2026-10-02 03:28 UTC）

以上接口检查的时间线和结论保持不变。随后生成的六个主模型条件及四个同条件5μs数值细化，已另行只读复核，详情见 `RUNNER_REVIEW.md` 和 `audit_runner_results.json`。

最终模型状态：两个C0完成并取得数值物理准入，但健康P/Q服务有明显损失；四个故障主记录均在清除前触DC高界停止，5μs细化重现该结论。已保存的完整采样转移及保留节点满足数值Ω/电流误差管判据，只覆盖各自停止前观测时段，不证明完整150ms故障安全或恢复。没有实际backup切换，不能将函数级强制测试误报为真实闭环backup验证。

该更新不改变接口函数检查通过的事实，也不将其升级为 `current_guard_qualified`、`paper_ready`、联合DC/SoC证书或100μs实时认证。本包未执行新的P优先/径向分配提案。
