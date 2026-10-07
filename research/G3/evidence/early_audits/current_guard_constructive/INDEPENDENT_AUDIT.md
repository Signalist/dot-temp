# 四个构造性基线：独立接口与 runner 审计

审计结论：**PASS_STATIC_INTERFACE_AND_RUNNER_ONLY，未发现本次授权范围内的执行阻断**。

核验时间：2026-10-02 03:46 UTC。审计对象为以下冻结字节版本；任何后续源代码修改均使相应结论需要重核。此结论只允许进入已批准的分阶段离线诊断，不代表 P0/R0 已获物理准入，也不代表 P50/R50 会成功。审计本身没有调用物理 `run`、RHS、ODE 积分或真实优化器；新增物理轨迹数及真实优化调用数均为 0。

## 1. 冻结对象与可复核文件

| 对象 | SHA-256 |
|---|---|
| `protocol/next_constructive/FOUR_BASELINE_PROPOSAL_V1.json` | `104b5f9102c286a2005e856da777b2a203a475c368fccd56d447e54ea43275f3` |
| `current_guard_constructive/run_constructive.py` | `e9bceab631ec7f26c9639aa3a2887ddf21f8cefdd63390c76fbeb1d3d30563c5` |
| `current_guard_constructive/guarded_allocator_controller.py` | `50f4b5f97cb8caad08463451e3dfe959528119cf10b140c78af57409608f52f6` |
| 唯一共同 guard：`current_guard_gate1/common_guard.py` | `89e47d8429f893d09c2fd7cac5a38de360e76d7dc225ad5e0eb940b1a96fbe03` |
| 标准名义分配器：`baseline_allocation/allocators.py` | `485e9ac80c8de58ee676d286972b92e7c398d1e2155a7f45dc025e2faffcb95a` |
| 完整 0.6 s checkpoint | `ca8a1d63f9bb406ab83b0560986ae43b29bd831018f1cbfedb60af4afaa48152` |
| 对照旧 driver：`current_guard_gate1/run_models.py` | `9e4ca7f83570e6e62bf7f3fef9096cde5c44782a0ca7b27026dcd47978662eae` |

独立可重放审计：

- `audit_interface_tests.py` → `audit_interface_results.json`：5 组接口/共同 guard 测试
- `audit_interface_runner.py` → `audit_interface_runner_results.json`：4 组 runner/准入/评分测试
- `AUDIT_MANIFEST.json`：本次审计交付物的字节指纹

复核命令（从 G3 目录运行）：

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python current_guard_constructive/audit_interface_tests.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python current_guard_constructive/audit_interface_runner.py
```

所有静态 reference fixture 在新目录下的临时目录生成并清理；没有写入实际 `results`，没有把合成数据作为物理证据。审计脚本禁止生成旧目录 bytecode，并对冻结源文件进行前后 hash 一致性核验。本次审计未修改任何被审计实现。

## 2. 标准 P-priority / radial 的独立数值核验

逐字段精确透传与独立 oracle 是两层不同的检查：

1. 将 identity guard 输出固定为名义 `m_nom`，比较新 wrapper 与冻结标准 allocator 的所有 controller 字段及全部 8 个返回列，要求误差精确为 0
2. 使用单独实现的显式电路、PLL、标准分配、PI、电压饱和及源功率方程计算预期结果。oracle 不调用 `allocators.controller`、`dq_bench.signals` 或其他被审计生产辅助函数

72 个静态 fixture 覆盖两种 allocator、P/Q 四象限、PCC 电压 1.0/0.4/0.05 pu、Vdc 1120/1400/1540 V、源幅度 1.0/0.4 pu、不同 PLL 角度、正负积分器/PLL 偏置，以及 ±800 kW 和超出服务限额的 ±1.2 MW 请求。它们是孤立的代数输入，不是新的物理场景或被声明可达的状态。

结果：

- 72/72 的全部 controller 字段及 8 列返回值与原 allocator 精确相同，输入 plant state 未改变
- 独立 oracle 最大 controller 绝对差：`4.547473508864641e-13`
- 独立 oracle 最大返回列绝对差：`3.410605131648481e-13`
- 52 个 fixture 激活电压饱和；24 个低于 PLL 归一化电压门槛
- 另有 6 个零 PCC 电压/零或坐标轴请求 fixture，均为有限值，低压 PLL 积分状态和频率保持旧值
- 观测形成读取旧 applied/queued；新 applied 恰为旧 queued；相对样本索引为 `(t−0.6)/Ts`，未提前改写已承诺保持量

## 3. 共同 AW、失败原子性与信息接口

24 个额外 fixture 覆盖两种 allocator、四象限以及 optimized / shifted_plan / terminal 三种来源，使用相同的测试电压偏移。

检查的修正恰为：

`Ts × 原 Kaw × Vdc_sample × (m_safe − m_nom) × exp(−j theta_PLL_sample)`

- 最大 AW 差为 `2.1220227966643612e-13`
- 只改变 nominal 计算后的 `zi` 与新 `queued`；theta、zpll、omega、pb_command、applied 与原 nominal 更新相同
- plant state 未改变；已承诺旧 queued 仅按原队列时序晋升，不被新命令覆盖
- 强制 guard failure 时，两种 allocator 的完整 controller 字段和 plant state 都与调用前精确一致
- 拒绝 `q_priority`、`adaptive`、空值及未声明 policy，不执行 guard command
- 共同 guard 实际接收字段恰为 `i_ab, vp_ab, vdc, applied_ab, queued_ab`，没有事件对象、fault/clearance 时间、未来观测或参考轨迹字段
- AST 核验 command 参数恰为 `t, k, observation, mnom`；nominal allocator 由已声明 policy 选择，电气 guard 算法本体未因 policy 改变

## 4. 共同 MPSC 与 saved-plan/backup 不变

导入路径经核验是旧 `current_guard_gate1/common_guard.py`，新目录不存在替代 `common_guard.py`。读取固定设计并用独立代数 oracle 核对 N=10、Ts=100 us、反馈 K、扰动半径、收紧输入/电流界及弦误差项。

复用旧独立测试中以下纯代数/模拟失败回归，未运行其中真实优化或旧物理 controller 测试：

- Omega 显式逆及相关集合判别，不以独立圆近似替代
- 当前电气观测的非零相位对齐、60 Hz 因果推进、白名单和域拒绝
- 原始可行计划全约束复算，以及输入/队列/电流/终端/nonfinite 非法候选拒绝
- 假 success 的不可行候选、不成功但可行的标记、nonfinite 输出拒绝
- backup 的 j=1、N−1、N、N+3 索引和 alpha-beta 回转，负索引/域外拒绝
- 无可用 backup 则停止，不产生任意替代命令
- saved-plan 原点、相位、证书、验证及 ready metadata；篡改 metadata 的拒绝；后续接受计划更新其自身样本原点

冻结 guard 与所有受检旧源文件的前后 hash 一致。

## 5. runner 的结构等价与完整初始状态

对最终 runner 与旧 Gate1 runner 做 AST 比较。**整个 run 函数**在仅规范化以下明确变化后等价：wrapper 导入名、guard 实际路径检查、设置 `guard.nominal_allocator=case['allocator']`、用同一个 allocator 进行 nominal 对照采样，以及输出来源 metadata/明确未配对的外部 Q 对照字段。

完全相同的部分包括：

- 13 维物理 RHS、6 个服务/能量 quadrature、测量电路及电池源方程
- 0.6 s 完整 checkpoint 重建和 normalized-state 验证
- 100 us 控制时钟、sample/fault 精确切分、off-grid 终止时间
- DOP853、rtol=1e−10、atol=1e−8、硬接触/root 筛查、停机规则
- physical hard margins 与 current/DC/SoC/Pb/P/S/modulation 阈值
- 全部原始日志、失败保留、antiwindup/源/PLL 不变量检查
- 绝对请求误差积分、能量库存和 wall-time 统计
- 50 ms 自身周期/同一时刻参考、三个连续通过、150 ms 硬限且无饱和恢复要求；guard intervention 仍计入 active limiting

另独立确认 10 个顶层 helper 与全部物理列 schema 的 AST 等价。对所有四个 case，整个数值参数字典与原协议一致，仅使用已冻结 fast port 的 tau=0.002 s、up/down=50 MW/s；完整 controller 和 7 个原 plant/passive state 来自同一 checkpoint，新增 6 个 quadrature 为零。normalized 初态最大差精确为 0。

各 case 如完整完成均有 21,501 次采样：0.6 到 2.7500 s；末尾按原规则精确推进到 2.75005 s。两故障只为 0.60005–0.75005 s、0.4 pu。不存在慢端口、1 us 相位、幅频/相位网格或新增物理场景入口。

## 6. 健康准入与同 allocator reference

37 个动态 helper 负例覆盖缺失健康结果、自身 allocator 健康失败、错误 case/allocator/port/event、protocol/guard/allocator/wrapper/runner/checkpoint hash、完整初态声明、端口 tau/ramp、缺失或 hash 失配 trace、不同 normalized 初态、防覆盖、未指示 5 us refinement 和非法步长。

已验证：

- P0 是首个允许条件；必须记录 P0 才允许 R0
- 两份健康结果都必须存在才允许任一 fault
- P50 必须以自己的 P0 物理/guard 通过为准；R50 必须以自己的 R0 通过为准
- P 健康失败会阻断 P50，但不阻断已通过健康门的 R50；若 P 通过，则 R50 前须记录 P50
- 只有同一物理条件 primary 记录明确触发 near-boundary/hard-contact refinement，才允许 5 us
- 任意既存 primary/refinement/started 证据都不能静默覆盖
- P0/R0 因无冻结同 allocator unguarded trajectory，paired healthy reference 明确为 `NOT_AVAILABLE`，不读取旧 Q-priority 当作配对基准
- P50/R50 分别只取 P0/R0，验证所有来源及 trace hash，初始全 normalized state 必须精确一致；共同观察窗口内 P/Q、绝对误差及 normalized state 的合成 arithmetic 检查通过
- 旧 Q+guard 只出现在明确 `matched_own_allocator_reference=False`、`used_for_recovery_scoring=False` 的外部已知对照记录中
- 未完成轨迹或缺失 reference 不会获得恢复时间评分

## 7. 边界与下一阶段

本审计未发现阻断，可以进入已批准的 P0-fast、R0-fast 健康诊断，再严格按各自健康门决定是否允许 P50-fast、R50-fast。实际结果及其日志/能量/硬限证据需要另行核对，静态 PASS 不预授物理通过。

仍必须保留：这是标准分配器加同一旧共同 MPSC 的离线构造性诊断；不构成新算法优越性、联合 DC/SoC 不变性、区间认证、100 us 实时性或 paper-ready 声明。健康物理通过也不自动表示 800/700 服务透明。两种基线都失败亦不能推出 fast port 的普遍不可行性。
