# 构造性基线：独立只读产物审计

当前状态：**PASS_ALL_FOUR_COMPLETED_ARTIFACTS**。已核对 4 份完成产物；尚未完成审计的 primary 条件：无。

本审计不运行物理模型或真实优化器。对既存 summary、NPZ 和 gzip 记录进行独立代数重算，物理轨迹数和真实优化调用数均为 0。`INDEPENDENT_AUDIT.md` 记录此前的冻结接口/runner 静态审计；本文件补充实际已完成产物。

## 1. 全窗口事实与证据一致性

| 条件 | 样本数 | 完整物理硬限通过 | I峰 pu | Vdc范围 pu | 全窗口平均P kW | 全窗口平均Q kvar | 冻结联合恢复时刻 |
|---|---:|---|---:|---|---:|---:|---|
| P0-fast | 21501 | True | 0.835358093 | 1.006535431–1.014022862 | 705.442969 | 644.791272 | 无故障不适用 |
| R0-fast | 21501 | True | 0.835358093 | 1.006535431–1.014047516 | 705.441863 | 644.793187 | 无故障不适用 |
| P50-fast | 21501 | True | 0.914650727 | 0.991410375–1.056608624 | 684.452532 | 600.360387 | 未达到 |
| R50-fast | 21501 | True | 0.905240966 | 0.986834300–1.056960174 | 681.310047 | 623.018108 | 未达到 |

每一行的完整时段均从 0.6 s 到 2.75005 s。健康通过是执行对应 fault 的物理/guard 准入，不表示预先未定义的服务透明容差已经通过。健康 reference 正确保留 NOT_AVAILABLE；故障按同一 allocator 的 P0 或 R0 配对，未把旧 Q-priority reference 冒充成配对参考。

## 2. 每个采样和计划的独立重算

| 条件 | 独立重算样本/optimized计划 | nominal最大差 | 共同AW最大差 | plan/index/frame command最大差 | 独立plan最大primal残差 |
|---|---:|---:|---:|---:|---:|
| P0-fast | 21501/21501 | 3.140e-16 | 4.388e-14 | 4.475e-16 | 5.467e-12 |
| R0-fast | 21501/21501 | 2.989e-16 | 4.380e-14 | 4.475e-16 | 4.725e-12 |
| P50-fast | 21501/21501 | 2.618e-16 | 3.875e-14 | 5.027e-16 | 5.600e-12 |
| R50-fast | 21501/21501 | 2.898e-16 | 4.240e-14 | 4.518e-16 | 5.862e-13 |

所有已接受 sample 均以独立显式电路/标准分配/PLL/PI/源反馈方程重算名义量，再应用相同 Kaw 的实际新队列修正；逐字段检查全 controller、plant 不变、旧队列晋升和日志。每个 accepted optimized plan 另用独立动力学/terminal/输入/队列/电流/Omega 方程全约束复算。没有以抽样重算替代全 sample 检查。

## 3. 已保存的管、能量、硬限与wall-time

| 条件 | 完整拍Ω/排除部分拍 | Ω最大disk超出 | 保留dense区间/节点 | dense误差减固定管半径最大值 | 硬接触/guard失败 |
|---|---:|---:|---:|---:|---:|
| P0-fast | 21500/1 | 5.467e-12 | 50/846 | -2.911e-02 | 0/0 |
| R0-fast | 21500/1 | 4.725e-12 | 50/846 | -2.912e-02 | 0/0 |
| P50-fast | 21500/1 | 5.600e-12 | 2001/33999 | -6.824e-03 | 0/0 |
| R50-fast | 21500/1 | -1.598e-05 | 2001/34003 | -3.770e-02 | 0/0 |

Ω判定沿用原 1e−8 数值容差；微小正浮点残差未被改写成精确零。每例末尾 50 us 部分拍单独排除完整一拍Ω声明。dense 只核对实际保留的节点/区间，不能升级成未保留连续时刻的认证或区间证明。

每例还核对全部 summary/NPZ/raw hash、最终全状态、列定义、端点电功率、P/Q/绝对误差积分、SoC、电池/DC/RL能量及守恒残差、contact列表、solver/backup计数和wall-time分位数。

| 条件 | controller实际wall-time median ms | p95 ms | 最大 ms | >100us次数/调用数 |
|---|---:|---:|---:|---:|
| P0-fast | 9.26936 | 14.45624 | 225.44234 | 21501/21501 |
| R0-fast | 9.25393 | 13.15195 | 231.83225 | 21501/21501 |
| P50-fast | 9.10875 | 12.80037 | 217.16709 | 21501/21501 |
| R50-fast | 9.21590 | 14.35174 | 225.65342 | 21501/21501 |

记录的wall-time只用于披露离线成本；100 us虚拟采样时钟没有被当成真实计算deadline已满足。

## 4. 实际150 ms故障服务与边界连续性

| 条件 | 故障平均P kW | 故障平均Q kvar | Q实际积分 var·s | Q绝对请求误差 var·s | 故障段能量守恒残差 J |
|---|---:|---:|---:|---:|---:|
| P50-fast | 417.761807 | -9.128479 | -1369.271860 | 106369.271860 | -2.252e-08 |
| R50-fast | 367.639535 | 317.960876 | 47694.131464 | 57305.868536 | -3.090e-08 |

实际Q来自 onset/clearance 精确split处的PCC无功quadrature差，并非Q请求误差字段。边界审计确认 .60005/.75005 s 的13维plant/passive/quadrature状态左右精确相同，applied/queued和控制积分器不重置，没有额外控制sample；PCC的P/Q代数跳变按同一瞬时电流和同一held电压独立重算。

保留每个sample左/右电压跳变的dense梯形积分仅作描述性交叉检查，正式服务数值使用已保存的积分状态。

## 5. 冻结恢复判据逐项核对

- P50-fast：复算 37 次恢复检查，qualifying=0，联合恢复时刻=None；失败子项次数={'self_cycle': 5, 'matched_target': 4, 'hard_safe_window': 0, 'unclipped_including_guard': 37, 'PLL_frequency': 2}
  - 最后检查：self=5.734e-13，matched target=2.274e-13，150ms hard safe=True，unclipped including guard=False，PLL频差=1.541e-11Hz
- R50-fast：复算 37 次恢复检查，qualifying=0，联合恢复时刻=None；失败子项次数={'self_cycle': 4, 'matched_target': 3, 'hard_safe_window': 0, 'unclipped_including_guard': 37, 'PLL_frequency': 2}
  - 最后检查：self=5.722e-13，matched target=2.274e-13，150ms hard safe=True，unclipped including guard=False，PLL频差=1.754e-11Hz

同自身健康参考的轨道误差变小不能替代原联合恢复要求。只要guard仍介入，150 ms无active-limiting项不通过，恢复时刻必须保持None；未放宽定义。独立审计器另经11个合成数组自测，覆盖每个limiting标志、硬限、self/target误差、PLL和“早期违例不能抹除”。

## 6. 有限结论与交付物

通过说明这些冻结条件的数值物理轨迹与其保存证据一致，并提供本条件下的已知标准基线构造性结果。它不表示800/700服务被完整保持，不构成新算法优越性、普遍fast-port可行性/不可行性、联合DC/SoC不变性、机器区间证明、100us实时性或paper-ready声明。

- `audit_artifact_checks.py` / `audit_artifact_results.json`：完整记录、逐sample、plan、管、能量、wall-time和恢复检查
- `audit_event_boundaries.py` / `audit_event_results.json`：故障边界、真实服务及段能量
- `audit_recovery_fixture_tests.py` / `audit_recovery_fixture_results.json`：恢复审计器的11个有限合成反例/正例
- `ARTIFACT_AUDIT_MANIFEST.json`：审计交付物hash
