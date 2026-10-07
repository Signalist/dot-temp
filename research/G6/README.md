# G6 精确参数的直接表示分类及合同失配边界

**处置：不升级工程主稿；仅保留窄数学短文及条件信息价值模块；paper-ready=false。** 科学结论以 2026-10-04 第三轮档案和六行目录为准；此交接代码复核日期为 2026-10-07。本目录应放在目标分支的 `research/G6/`。

## 精确研究问题

在几何衰减的共同旋转支撑模型中，精确旋转角的算术类型如何影响二维直接多面体表示？当一个未知但整个轨迹固定的旋转角处于区间、或共同方向存在固定误差时，哪些直接表示结论仍成立？在携带电气状态的两端口块输入中，把完美共同符号换成“每 L 块最多 B 次失配”的可监控合同，其条件安全波动幅值怎样变化？

这些是直接表示类别与信息/任务顺序合同问题。每个滞后/端口刷新参数会改变不确定性集合；SOC、提升 LP 和同信息标准 LP/min-cost flow 必须保留为强基线。所有 MW 都是指定分配射线上的总零均值波动幅值，不能解释为平均算力 hosting。

原结构模型为 x_(k+1)=r R_theta x_k+s_k b_k，0<r<1、s_k∈{-1,+1}、x0=0，状态跨块携带。固定cohort、一次选择后永远固定的optional cohort、每块可重新选的dynamic optional三种权限必须分开。

## 最新可保留结果

- 已有窄精确参数结论：在固定紧致内部容量斜率区间，二维直接多面体片段数为 Theta(log(1/epsilon)) 当且仅当旋转有有限指数逼近类型；无限指数类型允许次对数子序列。适用于明确的fixed-cohort及dynamic optional合同，优先权仍未确证。一次选择的optional fixed cohort另有可能矩形化的遮蔽现象，不能套到dynamic optional
- 固定未知参数区间的合成支撑证书为 `[2.862363672459, 2.862589894264]`（展示精度）；完整向外舍入小数和有理整数网格在 `evidence/round3_g6_20261004/experiments/`
- 跨绝对余弦拐点的二阶单边网格界是标准半凸插值特化。135 个浮点敏感性诊断不等于135个独立物理实验，也不证明新求解器
- 固定共同方向不确定性在可对齐扇区产生圆弧。固定活跃弧上的二维直接折线片段数为 `Theta(epsilon^-1/2)`；SOC 可常数规模描述圆弧，提升 LP 避开这一直接表示障碍
- 30 组双模型/三分配/五窗口预算的普通浮点 LTI 界已给出；每8块1次失配仍有条件幅值价值，但 WECC 对理想同步的失配非常敏感
- 同信息滑动窗口 LP、min-cost flow 与 DP 解相同目标。平均失配率即使渐近为零仍允许任意有限坏前缀，因此不能改善无限时域最坏安全域
- 两种合法宏计划可执行相同有标签任务、相同完成时间和能量；128 项 DAG 结构检查是合成目录验证，未标定真实 GPU/PCC trace，改变幅值也改变任务目录

等分配、频偏限值0.05Hz下，B=1/L=8的波动幅值内—外界：Kundur `[27.396828,27.455076] MW`，WECC `[58.550990,58.731040] MW`。B=0分别约 `[29.079654,29.145285]` 和 `[74.088449,74.376979]`；B=8分别约 `[24.301811,24.347631]` 和 `[56.416271,56.583417]`。科学精确输出以 `contracts/contract_amplitude_brackets.csv` 为准。

## 不可删除的失败和限制

- WECC 既有 dynamic-optional inner 非线性有限轨迹在 dt=1/128 秒达到 `0.0530995503416376 Hz > 0.05 Hz`；dt=1/64为 `0.0531086970696526 Hz`。原 JSON、输入和调度保留在 `evidence/round2_g6_joint_admission_20261003/nonlinear/`。本次没有新非线性积分，旧失败未撤回
- 正基值 Kundur 母线7/8各50MW的新工作点虽重新初始化，名义电压约0.945044/0.948743pu，低于示例0.95pu底线。频率合同并未建立电压/保护/热容量资格
- WECC补充端口基值仍为零，负半波是有符号增量注入，不能称非负真实计算负荷；没有正基值WECC
- 网络核、模态特征计算和参数/非线性误差没有被合成精确有理证书包围。有限旧非线性词不能给新窗口语言全族保证
- Duda支撑/折叠、弱硬实时窗口语言、半凸网格界和标准LP均有先例。2012 IFS近邻全文缺口仍在；精确表示算术分类的优先权未确证

## 阅读入口

- 最新报告及定理：`evidence/round3_g6_20261004/report/G6_ROUND3_DOSSIER_ZH.md`、`theory/THEOREMS.md`
- 当前原始CSV/JSON、窗口DP C++、Python生产者与独审：`evidence/round3_g6_20261004/contracts/`
- 原精确表示结构证明：`evidence/round2_g6_joint_admission_20261003/theory_review/G6_STRUCTURAL_AND_COMPLEXITY_PROOFS.md`
- 既有工程失败和假设台账：同第二轮目录下 `reports/`、`nonlinear/`、`positive_workpoint/`
- 更早合成网络支持包与测试：`evidence/round1/`；它不代表真实公共电网验证
- 接手执行：`AGENT_START.md`；剩余研究：`NEXT_STEPS.md`；安装与复现：`REPRODUCE.md`

```sh
cd research/G6
python verify.py
OPENBLAS_NUM_THREADS=1 python replay.py --mode quick --work-dir ../../g6_quick_new
OPENBLAS_NUM_THREADS=1 python replay.py --mode synthetic --work-dir ../../g6_synthetic_new
OPENBLAS_NUM_THREADS=1 python replay.py --mode network --work-dir ../../g6_network_new
```

入口复制证据到新目录，拒绝覆盖。network 模式约需300MB scratch，使用 C++17/OpenMP 编译源码并重建系数张量；它不是完整 ANDES/原DAE再资格审查。本次执行范围见 `validation/HANDOFF_QA.json`。`MANIFEST.json` 只认证当前公开载荷字节；原科学报告内历史hash并非当前交接清单。上游第三方原始工作簿/PDF、完整环境和大轨迹未捆绑，见 `provenance/README.md`。
