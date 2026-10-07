# W6 实验设计与 Codex 提示词独立审查

审查日期：2026-10-05 UTC  
结论：PASS_PLANNING_ONLY。范围限于计划、提示词、结构化合同、既有实现能力及来源一致性；不代表科学结果、硬件可用性、物理资格或研究主张已经通过。

本次审查没有发出模型请求、查询 GPU、写入 cap、采集 DC/PCC，或运行新的科学仿真。既有 39 项单测、1,369 条 schema 样例、8 个模拟 run 的数字是历史状态文件记录，并非本轮重新执行结果。

## 1 审查方法与覆盖

- 对照原 gpu_handoff 的 acquire.py、cap.py、core.py、analysis.py 检查计划所称现有能力；读取既有状态、原 A–E 检查点及来源清单
- 独立核验原两份 ZIP 的实际字节数、SHA256、CRC、安全成员路径及重复路径；两包都是普通 ZIP，可以合并解压，不是二进制分卷
- 核验 38 个实验 ID、矩阵 JSON/CSV 一致性、依赖合法性、32 维覆盖、各层 schema 的 ID 集合、字段字典与 CSV 表头
- 检查 JSON 严格可读、schema 本身有效、DRAFT 冻结模板有效、未经确认的伪 FROZEN 模板被拒绝
- 逐项审查物理/统计/因果边界、全周期与尾部、基线可比性、冻结和恢复续跑、隐私与逻辑分包要求

精确文件快照、机器检查结果及范围见 INDEPENDENT_QA.json。任何源文件在此快照后改变，都需要重新核验受影响项。

## 2 已闭合的关键修订

### R01：旧 split SHA 与 pilot 后确认预算

旧 fit_service 将整份 frozen split 的 SHA256 写入 model；evaluate_service 要求字节级相同。计划现明确：不覆盖原 split/model，不删除 SHA 门禁。可在拟合前冻结实际完整执行集合，或另实现经过测试的、事前声明 N 选择规则的父子 registry/协议链接。单纯预留很多 slots 再不执行部分 slots 不兼容原 evaluate；不能用删 slot 或过滤失败使检查通过。

### R02：声明路线与执行依赖

ROUTE_PLAN.json 的五条路线及矩阵的 route override 已逐条核验闭包和无环，明确分开既有理论、新模型、GPU 记录域、DC 控制和 PCC 路线。GPU-only 的描述准入不应隐式依赖 DC；模型数值工作不应被实测准入阻断。DC/W6 控制与自然 EOS 工作量声明各自具有附加门槛。最终交付必须审计所有选定必要 ID 的终态，未执行不写 PASS。F04 还要求最终 calibration/policy 输入与 N01/N02/N04 数值检查的 hash 闭合；参数变更后先更新 development 检查，不拿旧检查背书。

### R03：A–E 科学检查点不改义

保留原 A 新意与最近先例、B 理论/证明/数值、C PCC/网侧、D 真实执行测量、E 公平冻结验证。GPU_ONLY、GPU_DC、PCC 另作资源维度；它们不会替换原 A–E 意义。

### R04：产物路径统一

OUTPUT_PATH_MAP 的 127 个逻辑产物与总提示词的编号交付根目录明确映射，避免生成两套互相找不到的文件。编号输出合同与逻辑路径映射应在未来 study 中一并保留；旧工作区来源路径和旧交接包内路径另以来源映射定位。

### R05：原工具限制保留，不把适配需求写成现成能力

原工具只支持 localhost SSE 观察、host token hook、有界 cap 排程、外部给定变换的仪表导入和诊断 OLS。它没有通用 device EOS、物理 W6 actuator、burn、服务端取消、总体推断或真实仪表标定。旧 selected_folders 采用扁平 root/run_id；原 evaluate 要求全部已注册 heldout 角色存在。新嵌套 raw/attempt、workload transfer、分阶段评估必须有显式、安全且测试过的映射或版本扩展，失败仍保留在 all_attempts。

原 registry 仅接受 device/model_family 轴；无 transfer 研究可以保留真实的受支持轴且 transfer 集合为空，无需假造新设备；同设备 workload transfer 与字面 none 轴不能假装原实现已支持。原 PCC power/baseline 非负合同不支持有符号回送，且缺完整 Q/V/I/f 导入；扩展必须明确正负方向和数据语义，禁止取绝对值或截零隐藏问题。

### R06：能量目标电气边界

J_W6_J 仅用于冻结理论电气边界的动态 GPU 功率周期；NVML、AC、PCC 等其他边界不能同名替代。逐 run 能量也带 electrical_boundary，边界多行不增加独立样本数。request→power_return、request→matched_state、完整网侧 tail 是不同窗口，不能偷换。

## 3 科学与操作边界核验

通过计划层审查的重点如下：

1. HTTP stop、chunk、host callback 均不冒充自然 device EOS；自然 EOS、规则停止、截断、取消、超时、错误和未知分别记录
2. cap 命令、实际功率和真实 PCC 分开；NVML 差分不是连续 slew 硬界；计量/滤波/时钟/基线误差不会靠增加请求数消失
3. 控制写入默认关闭，需要具体设备、范围、时长、安全与恢复授权；不自动提权、租用 GPU、下载权重、进行 burn 或带电接线；恢复有 readback 和失败停机
4. pilot 是单 stratum 的 30 episodes、3 个 session clusters，配少量预定 sentinel；不会做全因素笛卡尔积，也不会当 30 iid 确认样本
5. 确认 N、工程 MDE、质量/QoS 非劣界、主次端点、多重性、缺失/删失/单侧 pair 失败、重试和停止规则事前冻结；默认固定 N，不看显著性随意加样本
6. 策略在相同信息、工作/质量、控制与恢复约束、成本边界下比较；constant-target 先公平优化；有限 Bellman 最优仅限其离散类，clairvoyant 只作放松参考
7. 匹配平均时延不足以声称同 QoS 节能；尾部、完成率和质量共同审查；J=E+cT 变化不能直接改写成能耗收益
8. 同 raw 会计重算不算新独立样本；改变在线策略需另采或标为模型反事实；安全保护不是可删除的硬件消融组件
9. 网侧初态、背景、映射误差及 p 返回后的峰值和尾部必须覆盖；有限观察零越限不是全未来安全，也不是监管认证
10. sealed raw、partial、全部失败、负收益和 amendment 保留；恢复续跑新建 attempt，不覆盖旧证据；小审查包缺 raw 时必须说明实际复算范围

## 4 包装与复算合同

原输入两 ZIP 的实际校验通过：主包 13,935,770 bytes，NetworkData 包 8,712,402 bytes，SHA256 与总提示词一致。独立检查合计 522 个文件成员，没有重复路径或不安全路径；历史“520 payload”与交付附加说明文件的计数口径分开。

未来结果要求普通独立 ZIP，每份严格小于 18,000,000 bytes；清楚列出完整复算需要哪些包、payload/hash/来源/许可、分块顺序及外置最终 ZIP 回执。不能通过丢 raw、删除失败或隐藏缺依赖让复算“通过”。CPU 复算与 GPU 纯 dry-run 入口是未来实现要求，本计划没有冒充已经实现和验证。

## 5 尚未闭合的研究工作

本计划通过不改变以下事实：真实 engine/device timing、实际控制与恢复、DC/PCC 标定、现场授权、研究预算、确认 N、控制/统计/路径适配和新实验结果仍待未来执行。缺项必须 BLOCKED 或缩小主张；可能得到无可辨收益、模型失配、不可实现或不确定结论。该结果同样应完整交付，不要求一直重跑至阳性。
