> Historical scientific document. Use the handoff root README.md and REPRODUCE.md for current execution commands and dependency limits. Historical hashes/complete-workspace statements are not current handoff verification.

# G6 二轮：复现与证据入口

## 入口

- 主结论：reports/G6_FULL_REPORT_ZH.md（全部冻结非线性回放结束后生成）
- 假设/容量量词：reports/ASSUMPTION_AND_HYPOTHESIS_LEDGER_ZH.md
- 主定理：theory_review/G6_STRUCTURAL_AND_COMPLEXITY_PROOFS.md
- 独立审查：audit/INDEPENDENT_PROOF_AUDIT.md
- 文献：literature/G6_DYNAMIC_NOVELTY_AUDIT_ZH.md、G6_NARROW_THEOREM_AUDIT_ZH.md、PRIMARY_SOURCES.json
- 基线、消融、统计单位：reports/BASELINES_ABLATIONS_AND_TRANSFER_ZH.md
- 失败：reports/FAILURE_AND_REPAIR_LEDGER_ZH.md
- 理论候选定位：reports/NEXT_GATE_AND_POSITIONING_ZH.md
- 原工作点线性迁移：transfer/REPORT.md
- 正50MW×2的Kundur新工作点：positive_workpoint/POSITIVE_WORKPOINT_REPORT.md
- 原NL回放：nonlinear/内的报告、逐例JSON与NPZ
- 永久/有限期风险：stochastic/THEOREMS_AND_AUDIT.md

## 工作目录与环境

本轮位置：outputs/round2_g6_joint_admission_20261003。命令从本目录上面的工作区根运行；现有qualified ANDES环境是outputs/round2_20261003/andes_env/bin/python。普通结构代码使用现有Python、NumPy、SciPy、mpmath、matplotlib。

所有本轮实现均为本轮原创或明示复制的既有已审计适配代码。未执行新取得的第三方代码。这里不给自动pip安装命令；若换环境，需要先按本身的权限和官方软件来源配置依赖。

## 轻量数学与数值复核

```bash
G6=outputs/round2_g6_joint_admission_20261003
python "$G6/src/run_structural.py"
python "$G6/src/run_dynamic_optional.py"
python "$G6/src/run_shared_parameter.py"
python "$G6/src/run_face_budget.py"
python "$G6/theory_review/check_theory.py"
python "$G6/audit/independent_checks.py"
python "$G6/stochastic/verify_stochastic.py"
```

这些命令会重写本轮相应结果，不应在已冻结科学源上直接运行后还声称哈希未变。建议复制整目录到新的复现输出目录再跑；脚本使用本身位置定位结果。需要外部冻结模型路径的脚本见下一节。

## 原工作点公共模型

```bash
G6=outputs/round2_g6_joint_admission_20261003
python "$G6/transfer/run_transfer.py" kundur wecc
python "$G6/transfer/validate_transfer.py" kundur wecc
```

inputs/已包含这些数值fixture的逐字节副本与SHA；src/replay_local_transfer.py可使用副本输出到新的replay_validation/local_transfer目录，不覆盖原结果。原脚本默认只读先前qualified源：

- outputs/round2_20261003/grid_transfer/kundur_reduced51.npz
- outputs/round2_20261003/grid_transfer/wecc_verified_descriptor_K.npz
- outputs/round2_20261003/grid_transfer/wecc_descriptor_aux.npz
- 相关原始端口资格文件（实际路径及SHA在transfer/BASELINE_SCOPE_AUDIT.json和各qualification中）

Kundur去掉统一转角规范后保留51状态；WECC不使用已被否决的普通QZ状态模型。原探针P0均为0，原模型迁移只能先解释为有符号增量端口。

## 原非线性与新正基值工作点

```bash
PY=outputs/round2_20261003/andes_env/bin/python
G6=outputs/round2_g6_joint_admission_20261003
$PY "$G6/nonlinear/run_g6_nonlinear.py" kundur wecc
$PY "$G6/positive_workpoint/qualify_positive.py"
$PY "$G6/positive_workpoint/run_positive_support.py"
$PY "$G6/positive_workpoint/run_positive_nonlinear.py" primary
$PY "$G6/positive_workpoint/run_positive_nonlinear.py" refine
```

这部分耗时较长。原NL为2网络×5案例×2步长；正基值为7主案例和3预定细化案例。预定输入和幅值在运行前另存；已有complete结果可被脚本识别复用，不把缓存读取说成重新运行。

原完整257块输入在旧/新工作点均保留。旧工作点NL使用有LTI尾差账本的65块尾词；新正基值NL执行全部257块并保留20秒ringdown。实际事件时间和接受输入在NPZ/CSV中，不能只用名义时间网格替换。

正基值固定为Kundur母线7/8各50MW、Q=0；旧A不重用。新增工作点的潮流、初始化、导数、稳定性、两个递减小脉冲与sink探针修正都有独立记录。

## 数据规模与轻量复现

transfer/的两个原始*_coefficients.npy约278MB，是完整相位×历史×端口张量；positive_workpoint/还有新工作点张量。每个张量可从相应kernel、模板和run脚本重建。支持数组、所有射线表、见证字、解析尾/相位界和小型资格记录远小于原张量。

若提供轻量包，必须附明确省略清单、原文件哈希、重建脚本和条件，不能声称轻量包包含全部原轨迹。原NPZ回放和完整张量均在本轮目录保存，没有用统计摘要替换唯一原始结果。

## 证书与复现的边界

数学定理是精确证明；网络尾和/相位公式是精确形式的普通浮点评价，缺全局向外舍入和descriptor近似误差包络；有限NL是有限轨迹检查。三者不能混称同一级证书。没有实测PCC、真实compute-power校准或无限非线性全族保证。

本轮冻结是本地计算流程冻结，不是第三方预注册。FACE_BUDGET局部时间戳曾在纯措辞修复重放时再生成，经过审计透明记录；参数和结果没有据此选优。参见protocol/FREEZE_TIMING_AUDIT.md。

“独立审查/独立实现”指本轮分别实现与交叉复核，不是期刊外部同行评审或第三方认证。数学证明未使用形式化证明助手。
