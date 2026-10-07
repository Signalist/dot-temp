"""Reader report and machine summary from completed frozen constructive records."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];B=R/'current_guard_constructive';O=B/'results';ids=['P0-fast','R0-fast','P50-fast','R50-fast'];ds={c:json.loads((O/f'{c}_h1e-05.json').read_text()) for c in ids};rows=[];service=[]
for c,d in ds.items():
 m=d['metrics'];rows.append(f"|{c}|{d['stop_reason']}|{d['final_time_s']:.5f}|{m['I_peak_pu']:.9f}|{m['Vdc_min_pu']:.9f}–{m['Vdc_max_pu']:.9f}|{'是' if d['complete_hard_safe'] else '否'}|")
 if d['event']:
  s=d['observed_fault_service'];ref=d['matched_reference'];service.append(f"|{c}|{s['mean_P_W']/1000:.6f}|{s['mean_Q_var']/1000:.6f}|{s['P_absolute_request_error_integral_J']/1000:.6f}|{s['Q_absolute_request_error_integral_var_s']/1000:.6f}|{ref['battery_stored_energy_difference_J']/1000:.6f}|")
t='''# G3 构造性基线检查与有界结论

2026-10-02 UTC。四个授权条件及独立全记录审计均已完成；不新增控制/参数搜索。建议本轮G3以 **paper_ready=false** 收束，但保留有用的工程正结果。

## 1. 工程可行性与论文就绪性分开

**工程层面**：在固定合成受控DC端口、平衡平均模型、同一初态及声明的0.4pu/150ms事件下，标准P优先和径向分配，加上完全相同的已有tube-MPSC层，均给出了覆盖故障、清除及清除后2s的有限完整数值物理可行见证。快端口Q优先失败因此不是已证明的所有分配无解。它不推翻原慢端口约17.088ms的控制无关能量排除，因为端口动态假设不同。

**论文层面**：这里没有新算法、没有800kW/700kvar全请求联合交付、没有通过原“退出所有限制”恢复评分、没有部署或算力负荷特异性证据。标准方法给出正构造首先减少新算法必要性的理由；现有证据不足以支持独立高创新主张。H07/H08仅保留为有具体证明门槛、尚未建立的后续命题，不据此继续大搜索。

## 2. 冻结模型结果

全部使用假设快合成受控DC端口2ms/50MW·s⁻¹、原0.600000s完整检查点、800kW/700kvar请求与原设备/硬限制。共同guard/N/K/Ω/终端/求解器/信息合同、100μs采样、一拍队列与共同反饱和不变，仅改原标准分配块。

|条件|状态|实际末时刻s|I峰值pu|Vdc范围pu|完整窗无硬触边|
|---|---|---:|---:|---:|---|
'''+ '\n'.join(rows)+'''

每个故障都有自身分配的无故障参照；未借用旧Q优先作为P/径向匹配参照。四条均无近界或硬触边标志，按冻结规则不复制长5μs轨迹。物理与数值适用范围不因完成积分而扩大。

![标准分配的故障响应](current_guard_constructive/CONSTRUCTIVE_FAULT_RESPONSE.png)

## 3. 服务牺牲与库存

以下P/Q均值及绝对请求缺口只对完整150ms故障区间计算；库存差是完整观测窗结束时相对自身无故障参照的电池储能差，正值表示少放出的电量仍留在电池。

|分配|故障均值P kW|故障均值Q kvar|P绝对缺口kJ|Q绝对缺口kvar·s|终态电池库存差kJ|
|---|---:|---:|---:|---:|---:|
'''+ '\n'.join(service)+'''

P优先的负Q已由事件两侧状态、电功率公式及独立积分交叉检查确认，是真实模型无功吸收，不能写成“仍提供Q支撑”。径向保留较多Q并减少P，是标准分配的不同服务取舍；没有事前偏好权重就不选“总冠军”。两者均未完整交付800/700联合请求。

健康P0/R0均值服务也仅约705.44kW/644.79kvar，初次guard调制改动0.214580692。没有预先声明健康透明性容差，故保留未评分，不追加正式通过/失败门槛。没有同allocator且未加guard的健康原始参照，本阶段只给健康绝对误差，不伪造此类配对差。

![各分配的健康参照](current_guard_constructive/CONSTRUCTIVE_HEALTHY_RESPONSE.png)

图中首5ms后主要是100μs端点快照，平均P/Q来自连续quadrature；端点水平线不代表连续平均。详细初始响应另见 `CONSTRUCTIVE_INSERTION_TRANSIENT.png`。

## 4. 恢复判据的保守性和目标适配

原冻结主评分不改：P50/R50的37次恢复检查均未满足“150ms内退出全部限制（含guard）”，正式恢复时刻仍为null。与此同时，最终检查的自周期/同时间自身参照状态差均小于6e−13，PLL频差约1.8e−11Hz以内，物理硬界保持安全。两类判断必须分别报告。

只读兼容性核查显示：**P0/R0健康参照本身**与P50/R50在2.60–2.75s的各1500个完整采样区间中，参考电流、调制电压、DC源指令、PLL限幅均未激活，但guard每拍仍介入，调制改动约3.37557e−4。因而精确回到这些已记录的受限健康目标，也不能满足该窗的“guard完全退出”条件。

这说明当前严格退出判据与所选持续作用的鲁棒目标轨道不适配；不是物理不能回轨的反例，也不证明所有未来或所有控制器必然介入。原评分保留，解释其限制，不能事后去掉guard门就宣布正式恢复通过。`RECOVERY_CRITERION_COMPATIBILITY.json`记录全部计数与未改分声明。轨道比较本来排除电池库存，库存差也没有被宣称已经再平衡；日后补能不能抹去过去P/Q服务缺口。

## 5. 复核与计算时间

独立静态审计覆盖72个透传fixture、6个零压/轴向请求、24个AW/queue样本和37个driver负例。四条原始产物共86,004次采样/优化计划全部独立重算，检查每个完整100μs转移的Ω数值包含、保留dense节点管、事件左右连续性、实际P/Q/损耗/库存、源/PLL/PI/队列、同分配参照与恢复子项。末尾50μs段不冒充完整一步包含。未发生真实备份切换，备份执行证据仍为函数级故障注入。

所有控制调用wall time均超过100μs，本阶段使用离线虚拟时钟，没有实时部署资格。固定冷启动SLSQP只代表此实现，不能据此否定合理缓存、warm start或专用QP/SOCP的成熟MPSC；也不能用该用时为新算法制造计算优势。

## 6. G3的有界收束

- **新颖性**：模型纠错、实际限流和标准分配构造属于已知控制的工程补齐。慢源能量排除有明确适用条件；常规相位滞后、静态能力组合与AI标签不构成新增。尚无独立定理或同信息成熟动态基线下的增量
- **显著性**：服务牺牲与物理成败是固定模型上的清晰工程量级；不是新策略总体成功率、统计显著性或确认集收益。健康压缩也不是所有安全控制的不可避免代价
- **消融**：已有源速度、静态优先级/径向、已有共用层及本次名义分配对照；快慢闭环同时改变τ和R，不能把闭环全部差异单独归因。此前解析包络显示5MW/s硬爬坡主导所查必要障碍。未做N/K/终端/噪声/持续波形等大搜索
- **迁移**：平均模型坐标复核与合成端口反事实不是实机、设施或网络迁移。20ms/5MW·s⁻¹与2ms/50MW·s⁻¹均未实机校准；无直连电池、开关、不平衡或任意相角跳变全资格

本轮全部guard条件为恒定800/700参考轨道诊断；此前300kW周期只是周期存在与损耗记账检查。尚未建立持续算力阶段波形、供电链滤波或数据中心PCC实测迁移，也没有算力负荷特异性。完整假设账本与四轴矩阵见 `protocol/next_constructive/`。

结论是“有限合成模型工程见证成立，高创新论文候选尚未成立”。建议停止本轮G3参数/策略扩展，保留可复核数据与有限后续命题；不把本轮收束写成所有BESS、所有分配或整个研究问题的普遍否定。
'''
(R/'G3_CONSTRUCTIVE_AND_CLOSURE_REPORT_ZH.md').write_text(t)
s={'status':'FOUR_FROZEN_CONDITIONS_COMPLETE_AND_AUDITED','engineering_evidence':'Two finite complete hard-safe fault/clearance trajectories in the locked synthetic average model','finite_hard_safe_fault_witnesses':['P50-fast','R50-fast'],'all_four_hard_safe':all(d['complete_hard_safe'] for d in ds.values()),'paper_ready':False,'current_guard_qualified':False,'original_joint_service_fulfilled':False,'frozen_formal_recovery_passed':False,'recovery_criterion_target_incompatibility_observed':True,'joint_DC_SOC_invariant_certificate':False,'real_time_qualified':False,'compute_load_specificity_established':False,'hardware_or_facility_transfer_established':False,'additional_search_planned':False,'cases':{c:{'result_file':f'current_guard_constructive/results/{c}_h1e-05.json','sha256':hashlib.sha256((O/f'{c}_h1e-05.json').read_bytes()).hexdigest(),'complete_hard_safe':d['complete_hard_safe'],'stop_reason':d['stop_reason']} for c,d in ds.items()}}
(B/'CLOSURE_SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n')
