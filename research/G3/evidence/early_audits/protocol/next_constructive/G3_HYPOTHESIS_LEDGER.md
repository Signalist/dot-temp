# G3 科学假设账本

2026年10月2日 UTC

## 当前判断

现有证据尚不足以支持 paper_ready。已经建立的是冻结合成受控DC端口内的模型复核、慢端口条件能量排除，以及已有 tube-MPSC 适配的条件数值诊断。一般安全滤波、静态P/Q能力圆、常规相位滞后和AI标签均不构成新增贡献。

仍可保留两个有条件的科学方向：H07所述非平凡的状态条件外界与构造性恢复内集之间的定量关系，以及H08所述同信息、同硬安全和恢复合同下的服务取舍增量。两者目前都没有独立高创新证据。H05所述快端口构造性可行性尚未决定；当前资料不支持预设成功，也不支持预设所有控制无解。

本账本仅审计已有证据，不执行新轨迹或控制性能搜索，也不制定下一四条基线的执行协议。模型名称统一为“合成受控DC端口”；20ms/5MW·s⁻¹与2ms/50MW·s⁻¹均不是实机校准。current_guard_qualified=false，paper_ready=false。

## 最新证据快照

六个主JSON全程使用恒定800kW/700kvar请求；没有验证持续算力波形或危险慢服务相位。此前300kW周期只是健康周期存在性与损耗/库存记账诊断，不能替代这两项证据。六行的共同初态为0.6s完整检查点。健康窗结束于2.75005s，长度2.15005s；四个故障为0.4pu、计划150ms，均在清除之前因DC上限终止。表中I峰值属于已记录区间，不能延伸到未观察部分。

| 条件 | I峰值 pu | Vdc峰值 pu | 故障已观察 ms | 结果 |
|---|---:|---:|---:|---|
| C0-slow | 0.835358093 | 1.038483078 | 不适用 | 完整健康窗物理通过 |
| C0-fast | 0.835358093 | 1.014067875 | 不适用 | 完整健康窗物理通过 |
| C50-slow | 0.888168876 | 1.100000000 | 6.224326 | DC触顶，清除和恢复未观察 |
| C50-fast | 0.888169284 | 1.100000000 | 8.596763 | DC触顶，清除和恢复未观察 |
| C1-slow | 0.908225710 | 1.100000000 | 6.192110 | DC触顶，清除和恢复未观察 |
| C1-fast | 0.908225710 | 1.100000000 | 8.362635 | DC触顶，清除和恢复未观察 |

两条健康窗的均值P为705.517/705.441kW，均值Q为644.839/644.795kvar，请求为800kW/700kvar。初始调制改动均为0.214580692；健康累计P绝对误差约203.143/203.307kJ，Q绝对误差约118.599/118.695kvar·s。没有事前服务透明性容差，JSON保留 service_transparency_pass=null；应写“物理准入成立且显著服务偏离已观察”，不能补判透明通过或正式失败。该健康窗持续净放电，不能称无限可持续或库存周期闭合。

C50-slow/C1-slow的控制无关能量必要界从各自真实事件状态重算，首等式分别约17.088203933/17.088205194ms；可保留20ms前缀矛盾的保守表述。实际Q优先+guard更早触DC界与此一致。快端口必要界未排除，只是外侧必要条件不活跃；它把所有电流资源乐观授予远端有功传输，与固定Q优先的实际策略不同。

四个DC终止的已有10→5μs复核，最大停止时刻差2.255e−10s、峰I差3.941e−13pu。它降低“此失败只是积分步长伪影”的疑虑，不验证参数不确定性或硬件。实际轨迹中备份调用均为0；函数级故障注入不等于轨迹级备份切换已观察。

两条健康窗的整次采样控制wall中位数约9.271/8.980ms，所有调用均超过100μs。它们是固定冷启动SLSQP的离线实现数据；不能据此判定成熟MPSC或合理优化的QP/SOCP无法实时。健康服务损失也只是当前固定构造的代价，不是所有安全控制不可避免的下界。

证据入口：`current_guard_gate1/results/{case}_h1e-05.json` 的 `/metrics`、`/service`、`/phases`、`/health_gate`、`/actual_onset_energy_necessary_condition`；`GATE1_MPSC_MODEL_REPORT_ZH.md`；`current_guard_gate1/REFINEMENT_COMPARISON.json`。

## 假设分类总览

| 编号 | 对象 | 当前判断 |
|---|---|---|
| H01 | 冻结模型的一致性与复现可信度 | 限定支持 |
| H02 | 共同实际电流层能补上参考限幅缺口 | 已观察前缀支持但未总资格 |
| H03 | 健康接入能够保持原服务 | 显著偏离已观察 正式透明性未评分 |
| H04 | 慢端口的控制无关能量排除 | 在冻结对象上成立 |
| H05 | 快端口是否存在完整安全恢复见证 | 开放 尚无见证 |
| H06 | 危险相位偏离功率峰值构成新机制 | 弱创新主张不成立 |
| H07 | 双侧排除区与构造性恢复集的定量缺口 | 条件性待证命题 |
| H08 | 同信息上层服务仲裁保留增量价值 | 尚无公平比较证据 |
| H09 | 微时序与扰动合同产生新的普适限流结论 | 合同相关的局部结论已支持 |
| H10 | DC端口响应代表真实BESS硬件 | 尚未标定 |
| H11 | AI阶段标签能够形成独立电气创新 | 标签不构成机制 波形研究未准入 |

## 逐项证据与停止条件

### H01 冻结模型的一致性与复现可信度

**类别：**已知建模与数值工程补齐。**当前状态：**限定支持。

**待检验命题：**独立坐标实现、守恒与事件细化足以支撑当前合成平均模型的数值诊断。

**当前证据**

- G3_PORT_AND_CURRENT_AUDIT_REPORT_ZH.md §§3–5：旧快端口P优先的参考始终≤0.95pu而实际触1.1pu；独立abc与dq的首次过流/停止及状态一致。
- GATE1_MPSC_MODEL_REPORT_ZH.md §3及REFINEMENT_COMPARISON.json：四个新DC终止在10/5μs下最大时刻差2.255e−10s、峰I差3.941e−13pu；所查终态能量导数向外。

**先前碰撞：**[dc:Z7a](https://aalto-electric-drives.github.io/motulator/grid_examples/grid_following/plot_10kva_dc_bus_gfl.html)；[dc:Z7b](https://aalto-electric-drives.github.io/motulator/control/grid/dc_voltage_ctrl.html)；[dc:Z7c](https://aalto-electric-drives.github.io/motulator/_modules/motulator/common/model/_converter.html)。具体版本、锚点与访问限制见末尾来源登记。

**可能的独立新增：**可提供有价值的可复核基准、方程/接口纠错与失败归因，但数值一致性本身不构成新控制理论、实机标定或新服务机制。

**最小改变判断的证据**

- 如拟提出新的物理结论，须由明确的额外物理假设或非平凡定理支撑，不能再增加同类步长/坐标一致性图作为创新替代。

**反证或停止条件**

- 发现守恒/符号/队列差错时暂停受影响结论并纠正；不得靠当前步长一致性外推开关模型、传感器不确定性或所有连续极值。

**当前可写：**当前平均模型内若干固定轨迹得到独立数值复核。

**当前不能写：**仿真与硬件等价、所有连续约束严格认证、复现完成即可paper_ready。

### H02 共同实际电流层能补上参考限幅缺口

**类别：**已知控制方法适配。**当前状态：**已观察前缀支持但未总资格。

**待检验命题：**现有tube-MPSC经队列增广及采样间包络适配后，可以作为上层分配共同的实际电流约束层。

**当前证据**

- GATE0_MPSC_REPORT_ZH.md §§2–6：理想实数条件电流/调制RPI、结构化初态数值计划与首段包络成立；外向舍入、联合DC/SoC不变性和部署未闭合。
- 六个主JSON /metrics、/current_continuous_crossings_s、/phases：两条健康窗通过；四个故障停止前I峰0.888169或0.908226pu，无I=1记录，随后DC触顶。
- 各JSON /timing/counts：实际备份调用均为0；动态轨迹并未检验真实求解失败时的备份切换。

**先前碰撞：**[guard:S1](https://arxiv.org/html/1803.08552v6)；[guard:S2](https://arxiv.org/html/1812.05506v4)；[guard:S3](https://arxiv.org/html/2405.14427v1)；[guard:S4](https://aaltodoc.aalto.fi/items/79bb654e-a84c-47b7-bb2f-39bc6a0e6763)。具体版本、锚点与访问限制见末尾来源登记。

**可能的独立新增：**队列、电压乘积和拍间合同的具体适配有工程价值；一般安全滤波、最小改动、鲁棒管、终端备份均是已有方法。尚无独立高创新依据。

**最小改变判断的证据**

- 若要称合格共同内层，需在明确合同与数值误差预算下完成相应资格；若用于服务比较，还需联合物理安全及服务准入，不能把电流条件保证直接升级。

**反证或停止条件**

- 任何合同内轨迹越过I硬界却仍报告认证，应撤回对应证书并查错。
- DC退出后停止证书适用；求解成功或六个有限轨迹未过流都不等于任意扰动的机器严格保证。

**当前可写：**已有方法的适配在已观察、DC域有效的前缀中消除了旧过流现象。

**当前不能写：**新限流原理、完整150ms故障安全、全装置认证或部署资格。

### H03 健康接入能够保持原服务

**类别：**已知工程准入问题。**当前状态：**显著偏离已观察 正式透明性未评分。

**待检验命题：**共同安全层在健康状态下接入时，可用可接受的预留代价保持已约定的P/Q服务。

**当前证据**

- C0-slow/fast /service：2.15005s均值P分别705.517070/705.440975kW，Q分别644.839354/644.794605kvar，请求800kW/700kvar。
- C0-slow/fast /health_gate：初始调制改动均0.2145806922403564，介入21500/21495次，总调用均21501；service_transparency_pass=null。
- 健康P绝对误差203.143024/203.306632kJ、Q绝对误差118.599223/118.695434kvar·s；健康物理通过不能替代服务质量。

**先前碰撞：**[guard:S1](https://arxiv.org/html/1803.08552v6)；[phase:C3](https://arxiv.org/html/1910.04052v2)；[phase:S10](https://arxiv.org/html/2110.10052v1)。具体版本、锚点与访问限制见末尾来源登记。

**可能的独立新增：**量化安全预留与服务损失是必要评估；对固定短预测域/终端/外包的代价诊断不是新的不可避免安全成本下界。

**最小改变判断的证据**

- 对预先声明的服务/预留合同，获得服务合格的健康准入证据；须分别保留绝对请求误差与同窗无guard增量。若想宣称代价不可避免，另需对全部允许控制的下界。

**反证或停止条件**

- 不得事后设置容差把本结果追认为透明通过，也不能把null补写成正式失败。
- 不能把保守外包、固定终端或冷启动实现导致的偏离说成设备的物理极限。

**当前可写：**两个有限健康窗物理安全，显著服务偏离被量化，尚无透明性判定。

**当前不能写：**透明接入、健康服务已通过、95kW左右损失是不可消除的鲁棒预留代价。

### H04 慢端口的控制无关能量排除

**类别：**条件物理结论 已有能量工具应用。**当前状态：**在冻结对象上成立。

**待检验命题：**在20ms/5MW·s⁻¹合成受控DC端口和锁定故障初态下，0.4pu跌落存在所有电流/DC安全控制都必须面对的前缀能量矛盾。

**当前证据**

- C50-slow /actual_onset_energy_necessary_condition：可用总余量4341.250139J，最大前缀增加下界8870.613573J，排除裕度4529.363434J，首等式17.088203933ms。
- C1-slow由自身故障起点重算：排除裕度4529.363166J、首等式17.088205194ms。
- 当前Q优先+guard分别6.224326/6.192110ms触DC界，早于该乐观外界，逻辑一致。

**先前碰撞：**[phase:C1](https://www.mdpi.com/1996-1073/19/18/4464)；[phase:C2](https://www.sciencedirect.com/science/article/abs/pii/S0378779626008503)；[dc:Z3](https://files.sma.de/downloads/MVPS-S2-SCS-US-B8-SH-en-11.pdf)。具体版本、锚点与访问限制见末尾来源登记。

**可能的独立新增：**该冻结对象的规范推导与明确适用域具有分析价值；能量积分、头寸与源爬坡不是新原理。当前证据不足支持一般BESS的新普适定理。

**最小改变判断的证据**

- 若要提升科学贡献，需要证明一个非平凡、带误差预算且有辨别力的状态条件边界，并与最近能量/服务边界工作逐条区分；不能只重复这个单初态数值根。

**反证或停止条件**

- 若在严格正排除裕度且全部假设满足时发现全程I/DC安全见证，必须查证书、包络或数值错误。
- 拓扑、R、允许保护路径或真实初态改变后，原数值根不可照搬；更早控制失败不反证必要界。

**当前可写：**约17.088ms为冻结控制集合的能量必要界等式；20ms保守矛盾表述保留。

**当前不能写：**所有BESS的17.088ms极限、精确控制失效时刻、此前保证安全、guard可以消除该负控制。

### H05 快端口是否存在完整安全恢复见证

**类别：**待决的构造性可行性问题。**当前状态：**开放 尚无见证。

**待检验命题：**在2ms/50MW·s⁻¹纯假设端口及相同信息/设备合同下，可能存在完整故障及恢复阶段均硬安全的因果控制。

**当前证据**

- C50-fast/C1-fast实际起点的能量必要界最大裕度约−3454.188781/−3454.189049J，只是不排除。
- 同两行当前Q优先+guard故障后8.596763/8.362635ms DC触顶；清除与恢复均未观察。
- 旧快径向记录完成但I峰1.030394pu；旧快P优先实际过流。均不构成安全见证，也不构成对所有分配的反证。

**先前碰撞：**[phase:C3](https://arxiv.org/html/1910.04052v2)；[phase:S10](https://arxiv.org/html/2110.10052v1)；[guard:S1](https://arxiv.org/html/1803.08552v6)；[phase:G1](https://arxiv.org/html/2605.05932v1)。具体版本、锚点与访问限制见末尾来源登记。

**可能的独立新增：**一个普通因果控制的完整安全见证可以闭合当前存在性问题，并为比较准入；见证本身不自动证明高创新或新仲裁优势。

**最小改变判断的证据**

- 最小改变是同一假设端口、完整因果信息合同与硬约束下，一个不借用故障/清除预知、观察到清除和规定恢复终点的可复核见证；或一个确实覆盖全部允许控制的更强必要排除证书。

**反证或停止条件**

- 任何硬越限使该见证失败，即使后来回轨也不能恢复资格。
- 若有限几个分配都失败，仅停止这些实现的可行性主张；不能升级为全策略不可能。
- 不得为找到见证默改电容、额定值、源速度、故障或初态。

**当前可写：**快端口的本必要界失活，当前控制仍失败，其他分配是否可行未知。

**当前不能写：**快端口已可行、当前失败证明无解、更快端口属于已验证硬件。

### H06 危险相位偏离功率峰值构成新机制

**类别：**已知普通机制。**当前状态：**弱创新主张不成立。

**待检验命题：**仅观察最危险慢服务相位偏离P峰值、上下头寸不同或同P升降沿状态不同，即可构成新的物理机制。

**当前证据**

- literature_collision.md的无损一阶源零假设已产生偏峰；theory_proposal.md §§3–4保留DC反馈后仍属分支局部普通谐波机制。
- 当前代理的临界电压相对P极值仅提升0.000277965/0.000167270pu，等效14.68/11.29J；不是完整模型新轨道。
- 既有300kW/1Hz健康周期在登记跌落幅值下双侧必要界不活跃；800kW/.5Hz只是未执行提案。

**先前碰撞：**[phase:C7](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/iet-cta.2017.1174)；[phase:P1](https://arxiv.org/html/1804.09262v1)；[phase:P2](https://arxiv.org/html/2407.07615v1)；[phase:P3](https://arxiv.org/html/2512.04239v2)；[phase:C3](https://arxiv.org/html/1910.04052v2)。具体版本、锚点与访问限制见末尾来源登记。

**可能的独立新增：**偏峰本身没有独立新增依据；可能保留的对象是H07的非平凡状态条件定理，而非相位标签或几度移动。

**最小改变判断的证据**

- 只有超出LTI积分/普通周期可行集、且效果严格大于模型/测量/数值误差的额外结构证据，才会改变这一判断。相位曲线变得更明显本身不够。

**反证或停止条件**

- 若完整结果可被普通滞后和状态记忆解释，停止偏峰创新主张。
- 若移相分类差低于误差预算，按无可辨信息处理，不能提频或改电容专门放大。
- 完整Markov状态与时钟/未来输入相同，不能再宣称独立于状态的神秘历史效应。

**当前可写：**常规动态记忆可使危险指标偏峰；现有小幅代理结果不支持高创新。

**当前不能写：**首创相位安全、AI特有记忆、把相位并入状态就是新方法。

### H07 双侧排除区与构造性恢复集的定量缺口

**类别：**可能独立的分析贡献。**当前状态：**条件性待证命题。

**待检验命题：**在完整健康轨道索引下，能给出带可核验误差的双侧状态条件必要排除区与联合约束构造性恢复内集，并定量说明二者缺口、主导切换及边界信息。

**当前证据**

- theory_proposal.md §§2–3已给上下能量外界和源lag/ramp/效率分支语义；必要界非充分。
- 同q代理60°/120°能量差约1.015kJ、上侧裕度差约1.023kJ，但两点都未被排除，且未控制其他状态；不证明不同可行性。
- 当前没有联合I、调制、DC、Pb、SoC与恢复的充分证书；Gate0的Ω仅含电流/队列，Gate1未到清除。

**先前碰撞：**[phase:C1](https://www.mdpi.com/1996-1073/19/18/4464)；[phase:C2](https://www.sciencedirect.com/science/article/abs/pii/S0378779626008503)；[phase:C7](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/iet-cta.2017.1174)；[phase:P1](https://arxiv.org/html/1804.09262v1)；[phase:P2](https://arxiv.org/html/2407.07615v1)；[phase:P3](https://arxiv.org/html/2512.04239v2)；[phase:G1](https://arxiv.org/html/2605.05932v1)；[phase:G2](https://journals.sagepub.com/doi/10.3233/ATDE260653)。具体版本、锚点与访问限制见末尾来源登记。

**可能的独立新增：**若在固定外生合同及本物理组合下，获得不可由已有能量积分/标准周期集合命名直接替代的紧性、切换或可计算误差定理，并说明操作上的新判别价值，可能形成独立贡献。现有“未检出完全相同组合”不是空白证明。

**最小改变判断的证据**

- 先给一个具体可核验命题及最近文献的假设/结论逐项差异；在一个健康合格完整状态族上，给有严格余量的新分类及至少一个对应构造性内集/见证，使外内差可度量。无须以大幅频/全参数搜索替代此证据。
- 若只主张解析定理，不必预先要求启发式控制击败MPC；但定理须独立新增、非平凡并正确。

**反证或停止条件**

- 若只能得到普通比较原理加三角积分、已知周期前驱集合或松外界，停止高创新表述。
- 若全登记状态均不活跃或仅按瞬时P单调排序且没有新增稳健判别，停止主机制主张。
- 若首要失败一直由别的约束主导，保留正确数学外界但撤回其主导解释。
- 严格正排除区内出现满足全部假设的安全见证，直接触发推导/证据纠错。

**当前可写：**这是尚有独立新增可能、但目前未完成的窄分析问题。

**当前不能写：**双侧公式已经首次提出、相位扇区已充分认证、已有完整恢复定理或paper_ready。

### H08 同信息上层服务仲裁保留增量价值

**类别：**可能的算法或服务结果。**当前状态：**尚无公平比较证据。

**待检验命题：**在共同且合格的动态电流层、同源端口和相同因果信息下，上层分配能够在既定硬安全及恢复要求内提供超出成熟动态分配的可复现服务取舍。

**当前证据**

- 旧P/Q优先与径向仅是冻结PI下诊断性弱基线；其实际过流削弱任何基于这些失败的优越性结论。
- 新六行上层只有Q优先；无健康服务透明资格、无完整安全故障见证，也无共同guard下分配比较。
- P/Q有符号/绝对误差、同窗无故障增量与库存各有独立记录；早停前缀不得按积分大小排名。

**先前碰撞：**[phase:C3](https://arxiv.org/html/1910.04052v2)；[phase:S10](https://arxiv.org/html/2110.10052v1)；[phase:C2](https://www.sciencedirect.com/science/article/abs/pii/S0378779626008503)；[phase:C7](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/iet-cta.2017.1174)；[phase:P3](https://arxiv.org/html/2512.04239v2)；[guard:S1](https://arxiv.org/html/1803.08552v6)；[guard:S3](https://arxiv.org/html/2405.14427v1)。具体版本、锚点与访问限制见末尾来源登记。

**可能的独立新增：**可能来自具体非平凡的合同/信息约束下、经强基线验证的服务前沿或可解释结构；不能来自多看未来、松Q、忽略库存/恢复或替基线补限流。动态P/Q、静态能力圆、一般安全滤波均已知。

**最小改变判断的证据**

- 先取得H05的构造性准入，再以预先声明的服务合同/安全优先级、同窗成本和成熟同信息动态方法证明一个可复现、非支配的增量；若涉及计算优势，采用合理优化的成熟实现及相同计算预算。此为证据门槛，不是执行协议。

**反证或停止条件**

- 强方法在同信息/资源/合同下复现前沿，则停止新分配优越性主张；这不自动反证H07的独立定理。
- 收益仅来自服务放松、未来故障泄露、更多预览、额外能源、较弱恢复或早停删失时，否定该收益。
- 共用内层弥合差异时，降级为已知控制工程修补，不改名保留创新。

**当前可写：**上层增量仍待验证，当前未建立新服务仲裁优势。

**当前不能写：**Q优先+guard失败证明新分配必要、一个快端口成功就是最优、优于弱静态基线即可论文级算法结论。

### H09 微时序与扰动合同产生新的普适限流结论

**类别：**已知延迟与鲁棒性问题的具体实例。**当前状态：**合同相关的局部结论已支持。

**待检验命题：**采样后1μs与50μs的故障偏移、一拍队列和源方向合同，必须计入初态可准入与安全声明。

**当前证据**

- GATE0_MPSC_REPORT_ZH.md §§1、3–4：宽全相位圆容许180°突跳，旧队列在首100μs有1.065060034pu投影下界；结构化幅值/60Hz/无相跳合同首段上界0.914045145pu。
- C1/C50只是控制拍内偏移，四行峰I与DC时间不同；不是慢服务相位扫描，也不是交流故障初相普遍性验证。

**先前碰撞：**[guard:S1](https://arxiv.org/html/1803.08552v6)；[guard:S3](https://arxiv.org/html/2405.14427v1)；[phase:P1](https://arxiv.org/html/1804.09262v1)。具体版本、锚点与访问限制见末尾来源登记。

**可能的独立新增：**不可更改首保持段可产生有用的本模型不可准入见证，但采样延迟、增广状态和扰动集合依赖性本身已知；暂未形成独立一般定理。

**最小改变判断的证据**

- 若要升级为独立分析贡献，需要对明确定义合同给出非平凡的队列/可用电压/状态必要边界及可达紧性，先与既有延迟鲁棒控制区分。仅新增更多拍内偏移不改变创新判断。

**反证或停止条件**

- 不能用宽合同反例否定窄幅值合同；不能由两个微时序推断任意相角跳跃/频率偏移。
- 任何通过篡改旧队列、故障预知或缩小未声明扰动集合得到的准入均无效。

**当前可写：**现有准入与安全结论明确依赖结构化合同；两种微时序是有限诊断。

**当前不能写：**已覆盖任意电网相位扰动、C1/C50就是慢服务相位效应、新命令能立即改首保持段。

### H10 DC端口响应代表真实BESS硬件

**类别：**物理适用性前置条件。**当前状态：**尚未标定。

**待检验命题：**锁定lag/ramp端口可代表目标真实设备故障下不可绕过的DC功率响应，因此相关边界有实物适用性。

**当前证据**

- dc_topology_scope.md §§1–5：模型有独立Pb指令、连续Pb、lag/ramp和固定效率，缺少电池I–V、DC/DC电感/占空比及内部储能。
- 已核验资料区分50ms通信、1s上层P/Q、SMA参考梯度、内环近似和输出阶跃；没有与本功率/电压/拓扑/故障状态相匹配的快速下降/反向数据。
- 更快端口仅改变行为参数；τ趋零不变成直连电池。

**先前碰撞：**[dc:Z1](https://arxiv.org/pdf/1910.04052)；[dc:Z2](https://library.e.abb.com/public/8b613f6b51914388b996de018db1dd22/2UCD190000E001_j%20PCS100%20ESS%20User%20Manual.pdf)；[dc:Z3](https://files.sma.de/downloads/MVPS-S2-SCS-US-B8-SH-en-11.pdf)；[dc:Z4](https://www.sungrowpower.com/us/en/newsdetail/336)；[dc:Z5](https://www.mdpi.com/2079-9292/9/10/1738)；[dc:Z6](https://www.mdpi.com/1996-1073/8/9/9969/pdf)。具体版本、锚点与访问限制见末尾来源登记。

**可能的独立新增：**目前可做明确标注的合成机制研究；实物证据可以改变适用性判断，但获得参数标定本身不等于新控制原理。

**最小改变判断的证据**

- 只有在计划作实物外推时，补一个明确目标拓扑及可溯源下降/反转数据，核验其限幅/保护是否能绕过所用硬R、内部能量是否被正确计入；否则保留合成范围即可，无需无目的扩展。

**反证或停止条件**

- 若真实响应或保护使排除区消失，撤回该设备上的主导机制解释；不反挑慢R或小C追回结论。
- 直连电池必须另有正确状态/端口方程，不能以快速行为端口冒名。

**当前可写：**全部本地结果属于合成受控DC端口；快慢参数均非实机校准。

**当前不能写：**已验证DC/DC、直连电池实证、一般utility BESS固有5MW/s极限。

### H11 AI阶段标签能够形成独立电气创新

**类别：**应用场景与数据真实性问题。**当前状态：**标签不构成机制 波形研究未准入。

**待检验命题：**非正弦阶段需求可作为有依据的外生合成输入；AI身份或阶段名称本身产生区别于相同工业电气输入的BESS机制。

**当前证据**

- exogenous_waveform_scope.md §§1–4：生产训练形态、单工作站PSU滞后与通用设施EMT是不同证据层；未确认可复现毫秒级设施PCC故障波形。
- GPU100ms数据不能插值冒充5ms电气测量，0.2–3Hz频谱摘要不是普遍基频；合成30s四阶段模板未执行健康资格或故障试验。
- 相同名义P/Q、欠压动态律、供电链状态、网络和控制信息的AI/工业重标签，应得到相同电气响应。

**先前碰撞：**[wave:W1](https://www.energy.gov/sites/default/files/2026-01/Data_Center_EMT_Models.pdf)；[wave:W2](https://arxiv.org/html/2508.14318v1)；[wave:W3](https://arxiv.org/html/2502.01647v2)；[wave:W4](https://arxiv.org/pdf/2108.02037)；[phase:C2](https://www.sciencedirect.com/science/article/abs/pii/S0378779626008503)。具体版本、锚点与访问限制见末尾来源登记。

**可能的独立新增：**有校准依据的电气负荷律/聚合差异可能增加应用辨识价值；仅换标签、波形形状或控制相位不构成新机制。当前仅支持结构启发的合成外生服务研究。

**最小改变判断的证据**

- 若后续科学命题确实依赖非正弦输入，先有同服务、损耗补偿和全部硬约束合格的健康持续轨道，并确认相同电气输入重标签等价；若要主张设施真实性，需测点与同步明晰的PCC/内部链数据。

**反证或停止条件**

- 相同电气输入只因AI标签不同而输出不同，应视为实现/信息泄露错误。
- 健康轨道不能闭合或引入无限UPS缓冲时停止故障机制研究；不能调度内部工作负载、控制UPS或给干净未来阶段标签制造收益。

**当前可写：**非正弦合成外生阶段是有结构依据的研究对象，尚无设施故障复现或AI独有机制证据。

**当前不能写：**典型真实PCC波形已标定、AI标签本身创新、GPU/PSU滞后等于设施或BESS时间常数。

## 最小决定性证据

1. **先区分存在性。** 在假设快端口、相同物理和因果信息合同下，一个完整硬安全且达到规定恢复目标的构造性见证即可改变H05；一个覆盖全部允许控制的更强必要排除也可改变它。只需回答这个具体问题，不应先扩大幅频、相位、设备或策略网格。成功意味着该条件存在解；普通控制成功不意味着新算法。
2. **再分别检验科学新增。** H07需要具体非平凡命题、最近文献差异、误差预算和有辨别力的外内边界；H08需要经过准入、同信息成熟动态对照下的预声明服务取舍增量。二者逻辑独立：普通MPC复现服务前沿会否定“新分配优越”，但不会自动否定一条另有依据的新解析定理。
3. **仅在提出外推时补物理证据。** 若结论坚持合成范围，当前不必漫无目的扩充拓扑或现场数据；若要声称真实BESS或真实设施适用性，则需与命题直接对应的端口/测点/时序证据。标定改变适用范围，不自动改变方法创新。

上述证据是判断门槛，不代表已获运行结论或执行授权。若结果仍能由常规动态能力分配、能量积分、周期MPC和成熟安全层完整解释，则应如实收束为高质量模型/工程分析；只有证据满足更强命题时才提升贡献判断。

## 必须分开的逻辑层级

- 某控制器失败不能推出所有同信息控制不可能；必要界未排除不能推出存在安全控制。
- 有限轨迹数值通过不能推出全称不变性；条件电流/调制保证不能推出DC/SoC/服务与恢复。
- 构造性可行见证不能推出最优或新方法优越；成熟MPC复现前沿不自动否定一个独立非平凡解析定理。
- 健康有限观察窗不是无限持续或库存周期闭合；服务透明性null不等于通过，也不能事后补为正式失败。
- 故障停止前I安全只是前缀；清除/恢复未观察就是未知，早停积分不可排名。
- 固定SLSQP墙钟超100μs不是成熟MPSC普遍无法实时的证据。

## 来源与证据时点

本轮没有新增网络核验、下载或复制论文/手册原件；复用既有2026年10月2日原始资料审计。来源登记保留出版商访问受限、仅索引段落、版本差异和未确认数据发布等限制，不把“未找到”写成“不存在”。Shamseldein条目的2027年1月为卷期，首次在线日期在原审计中仍未解决；不得将其写成已核实的首次发表日。

历史提案中的“未实现/未运行”指当时状态；本账本以六个主JSON和最新Gate1报告更新当前执行证据，不修改旧文件。完整输入SHA-256、逐案字段及来源索引见同名JSON。

### 文献索引

- **dc:Z7a** [10-kVA, DC bus, GFL](https://aalto-electric-drives.github.io/motulator/grid_examples/grid_following/plot_10kva_dc_bus_gfl.html)。锚点：configuration: Configure the system model and control system；external_current: Set the time-dependent reference and disturbance signals。登记：`protocol/phase_mechanism/dc_topology_sources.json`，原ID Z7a。
- **dc:Z7b** [DC-Bus Voltage Control](https://aalto-electric-drives.github.io/motulator/control/grid/dc_voltage_ctrl.html)。锚点：energy_balance: Eq.(3)；tuning: Eq.(5)。登记：`protocol/phase_mechanism/dc_topology_sources.json`，原ID Z7b。
- **dc:Z7c** [motulator.common.model._converter](https://aalto-electric-drives.github.io/motulator/_modules/motulator/common/model/_converter.html)。锚点：classes: VoltageSourceConverter; CapacitiveDCBusConverter；dynamics: CapacitiveDCBusConverter.rhs。登记：`protocol/phase_mechanism/dc_topology_sources.json`，原ID Z7c。
- **guard:S1** [Linear model predictive safety certification for learning-based control](https://arxiv.org/html/1803.08552v6)。锚点：Section II Eq. (1) and nonlinear/time-varying inclusion paragraph；Section III-A Eqs. (2)-(5)；Algorithm 1；Theorem III.5；Section III-B Theorem III.7；Section IV-A Eq. (8)。登记：`protocol/phase_mechanism/current_guard_sources.json`，原ID S1。
- **guard:S2** [A predictive safety filter for learning-based control of constrained nonlinear dynamical systems](https://arxiv.org/html/1812.05506v4)。锚点：Section 3 Eqs. (1)-(4)；Eqs. (5)-(6)；Algorithms 1-2；Section 4.2 assumptions and Theorem 4.6。登记：`protocol/phase_mechanism/current_guard_sources.json`，原ID S2。
- **guard:S3** [Advanced Safety Filter for Smooth Transient Operation of a Battery Energy Storage System](https://arxiv.org/html/2405.14427v1)。锚点：Section II-A Eqs. (1)-(2)；Section II-C Eq. (6) and Problem 1 assumptions；Section III Eq. (7)；Section III-B QCQP and Eqs. (18a)-(18b)；Section III-C Eqs. (19a)-(19c)；Section IV-A and Table I。登记：`protocol/phase_mechanism/current_guard_sources.json`，原ID S3。
- **guard:S4** [Multifunctional Control of Grid-Connected Converters with Model Predictive Control and Disturbance Observer](https://aaltodoc.aalto.fi/items/79bb654e-a84c-47b7-bb2f-39bc6a0e6763)。锚点：Institutional abstract；Indexed Section III-A reference-limiting discussion；Indexed cost discussion around Eq. (16), slack variable zeta and high lambda_zeta。登记：`protocol/phase_mechanism/current_guard_sources.json`，原ID S4。
- **phase:C3** [Optimal Provision of Concurrent Primary Frequency and Local Voltage Control from a BESS Considering Variable Capability Curves: Modelling and Experimental Assessment](https://arxiv.org/html/1910.04052v2)。锚点：Equations (3)-(14)；Section II；Section III, Table II。登记：`protocol/phase_mechanism/sources.json`，原ID C3。
- **phase:S10** [Optimal Grid-Forming Control of Battery Energy Storage Systems Providing Multiple Services: Modelling and Experimental Validation](https://arxiv.org/html/2110.10052v1)。锚点：Section III-B, equations (12a)-(12h)；Equations (16)-(25)；Section II。登记：`protocol/phase_mechanism/sources.json`，原ID S10。
- **phase:C1** [Service-Constrained Critical Energy-Headroom Boundaries for Current-Limited Grid-Forming Battery Converters](https://www.mdpi.com/1996-1073/19/18/4464)。锚点：Equations (30)-(34)；Table 2；Tables 4-5；Sections 7.8 and 8.4。登记：`protocol/phase_mechanism/sources.json`，原ID C1。
- **phase:C2** [Impedance-passivity coordination of hydrogen-coupled AI data centers for oscillation damping and fault ride-through at transmission interfaces](https://www.sciencedirect.com/science/article/abs/pii/S0378779626008503)。锚点：Equations (7)-(11)；Equations (31)-(34)；Sections 4.1-4.4；Section 5.3, Figure 10；Section 5.6。登记：`protocol/phase_mechanism/sources.json`，原ID C2。
- **dc:Z3** [Medium Voltage Power Station with Sunny Central Storage US for AC-coupled Storage Solutions: System Manual](https://files.sma.de/downloads/MVPS-S2-SCS-US-B8-SH-en-11.pdf)。锚点：direct_precharge: p205, Section 14.1.5.2；power_reference_ramp: p223, Section 14.4.2, Fig.90；ramp_parameter: p248, parameter 726 WGra；mode_override: p137, DC Voltage Control mode。登记：`protocol/phase_mechanism/dc_topology_sources.json`，原ID Z3。
- **phase:G1** [Consideration of Control-Loop Interaction in Transient Stability of Grid-Following Inverters using Bandwidth Separation Method](https://arxiv.org/html/2605.05932v1)。锚点：Section II-A, equations (1)-(4)；Section III-A, equation (7), Figures 2-3；Section III-D；Sections IV-A and IV-C；Appendix C, Table A1。登记：`protocol/phase_mechanism/sources.json`，原ID G1。
- **phase:C7** [Periodic constraint-tightening MPC for switched PV battery operation](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/iet-cta.2017.1174)。锚点：Section 3, equation (10)；Section 5, Proposition 1；Equations (28), (33)-(34)；Propositions 1-2 and Theorem 1；Section 6, equation (38)；Sections 2 and 8。登记：`protocol/phase_mechanism/sources.json`，原ID C7。
- **phase:P1** [Reference Governors and Maximal Output Admissible Sets for Linear Periodic Systems](https://arxiv.org/html/1804.09262v1)。锚点：Section III, Definition 1；Equations (11)-(12)；Section IV-A, equation (21)；Section IV-B。登记：`protocol/phase_mechanism/sources.json`，原ID P1。
- **phase:P2** [Finite Control Set Model Predictive Control with Limit Cycle Stability Guarantees](https://arxiv.org/html/2407.07615v1)。锚点：Section 2, equation (3)；Equation (14f)；Definition 5 and equation (18)；Equation (19)；Theorem 9；Section 4。登记：`protocol/phase_mechanism/sources.json`，原ID P2。
- **phase:P3** [Configuration-Constrained Tube MPC for Periodic Operation](https://arxiv.org/html/2512.04239v2)。锚点：Section 2.2, Definitions 1-2；Equation (8)；Section 3, equation (10)；Equation (13), Theorem 1；Section 3.3, Corollary 1。登记：`protocol/phase_mechanism/sources.json`，原ID P3。
- **phase:G2** [The Impact of Different Current Limiting Strategies on the Dynamic Behavior of Terminal Voltage in Grid-Following Converter After Faults](https://journals.sagepub.com/doi/10.3233/ATDE260653)。锚点：Section 2；Section 4, equation (9)；Section 5。登记：`protocol/phase_mechanism/sources.json`，原ID G2。
- **dc:Z1** [Optimal Provision of Concurrent Primary Frequency and Local Voltage Control from a BESS Considering Variable Capability Curves: Modelling and Experimental Assessment](https://arxiv.org/pdf/1910.04052)。锚点：ratings_and_modbus: PDF p4, Section III, Table I；TTC_equations: PDF pp2-3, Eqs.(4)-(9), Fig.2；efficiency: PDF p3, Eq.(11)；seven_string_parameters: PDF p5, Table III；supervisory_interval: PDF p6, Section IV。登记：`protocol/phase_mechanism/dc_topology_sources.json`，原ID Z1。
- **dc:Z2** [PCS100 ESS User Manual](https://library.e.abb.com/public/8b613f6b51914388b996de018db1dd22/2UCD190000E001_j%20PCS100%20ESS%20User%20Manual.pdf)。锚点：dc_connection_and_precharge: p60, Section 6.13, Fig.6-19；control_mode_response: p41, Section 6.3；analog_setpoints: p151, Appendix D。登记：`protocol/phase_mechanism/dc_topology_sources.json`，原ID Z2。
- **dc:Z4** [Sungrow Powers JEA’s SolarSmart Program with 1500VDC DC-Coupled System](https://www.sungrowpower.com/us/en/newsdetail/336)。锚点：system: project description and paragraph naming SG2500U and ST1918KWH-D750HV。登记：`protocol/phase_mechanism/dc_topology_sources.json`，原ID Z4。
- **dc:Z5** [Dynamic Improvement with a Feedforward Control Strategy of Bidirectional DC-DC Converter for Battery Charging and Discharging](https://www.mdpi.com/2079-9292/9/10/1738)。锚点：averaged_model: p8, Eqs.(6)-(7)；inner_loop: p10, Eqs.(19)-(21)；parameters: p10, Table 1；experiment_scale_and_load: pp13-14, Section 5.2；transient_response: pp14-15, Fig.16。登记：`protocol/phase_mechanism/dc_topology_sources.json`，原ID Z5。
- **dc:Z6** [Study and Implementation of a Two-Phase Interleaved Bidirectional DC/DC Converter for Vehicle and DC-Microgrid Systems](https://www.mdpi.com/1996-1073/8/9/9969/pdf)。锚点：compensated_loop_gain: PDF p15 / printed p9983, Eqs.(28)-(29), Figs.14-15；prototype: PDF p16 / printed p9984, Section 5, Table 1。登记：`protocol/phase_mechanism/dc_topology_sources.json`，原ID Z6。
- **wave:W1** [Electromagnetic Transient Modeling of Large Data Centers for Grid-Level Studies](https://www.energy.gov/sites/default/files/2026-01/Data_Center_EMT_Models.pdf)。锚点：详细页码/图表见原来源登记。登记：`protocol/phase_mechanism/waveform_sources.json`，原ID W1。
- **wave:W2** [Power Stabilization for AI Training Datacenters](https://arxiv.org/html/2508.14318v1)。锚点：Sections II-B and II-C; Figures 1-3；Section III-A；Section IV-C; Figure 7。登记：`protocol/phase_mechanism/waveform_sources.json`，原ID W2。
- **wave:W3** [AI Load Dynamics–A Power Electronics Perspective](https://arxiv.org/html/2502.01647v2)。锚点：Section III instrumentation statement；Section VI-A; Figure 11。登记：`protocol/phase_mechanism/waveform_sources.json`，原ID W3。
- **wave:W4** [The MIT Supercloud Dataset](https://arxiv.org/pdf/2108.02037)。锚点：Paper Section III, Tables I, II, V；Author repository: Data Organization / GPU utilization；MIT Data page January 2022 release listing；AWS Registry: Resources on AWS and License。登记：`protocol/phase_mechanism/waveform_sources.json`，原ID W4。

### 本地审计输入

- `GATE0_MPSC_REPORT_ZH.md`
- `G3_PORT_AND_CURRENT_AUDIT_REPORT_ZH.md`
- `GATE1_MPSC_MODEL_REPORT_ZH.md`
- `current_guard_gate1/REFINEMENT_COMPARISON.json`
- `protocol/phase_mechanism/literature_collision.md`
- `protocol/phase_mechanism/sources.json`
- `protocol/phase_mechanism/theory_proposal.md`
- `protocol/phase_mechanism/dc_topology_scope.md`
- `protocol/phase_mechanism/dc_topology_sources.json`
- `protocol/phase_mechanism/exogenous_waveform_scope.md`
- `protocol/phase_mechanism/waveform_sources.json`
- `protocol/phase_mechanism/dynamic_current_baseline_proposal.md`
- `protocol/phase_mechanism/current_guard_sources.json`
- `current_guard_gate1/results/C0-slow_h1e-05.json`
- `current_guard_gate1/results/C0-fast_h1e-05.json`
- `current_guard_gate1/results/C50-slow_h1e-05.json`
- `current_guard_gate1/results/C50-fast_h1e-05.json`
- `current_guard_gate1/results/C1-slow_h1e-05.json`
- `current_guard_gate1/results/C1-fast_h1e-05.json`

本账本无新仿真、无性能搜索、无新的四条基线执行协议。所有数学构造、数值轨迹、实物适用性和创新判断保持各自证据层级。
