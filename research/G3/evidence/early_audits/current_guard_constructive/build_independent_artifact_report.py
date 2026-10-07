"""Build a read-only-audit report from checked completed artifacts. No simulation."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=json.loads((HERE/'audit_artifact_results.json').read_text())
event=json.loads((HERE/'audit_event_results.json').read_text()) if (HERE/'audit_event_results.json').exists() else {'results':[]}
events={r['case']:r for r in event['results']}
rows=checks['completed_artifacts'];summaries={r['case']:json.loads((HERE/'results'/f"{r['case']}_h{r['h_s']:g}.json").read_text()) for r in rows}
assert all(r['status']=='PASS_COMPLETED_ARTIFACT_RECONCILIATION' for r in rows)
for r in rows:assert sha(HERE/'results'/f"{r['case']}_h{r['h_s']:g}.json")==r['summary_sha256']
lines=['# 构造性基线：独立只读产物审计','',f"当前状态：**{checks['status']}**。已核对 {len(rows)} 份完成产物；尚未完成审计的 primary 条件：{', '.join(checks['pending_primary_artifacts']) or '无'}。",'',
'本审计不运行物理模型或真实优化器。对既存 summary、NPZ 和 gzip 记录进行独立代数重算，物理轨迹数和真实优化调用数均为 0。`INDEPENDENT_AUDIT.md` 记录此前的冻结接口/runner 静态审计；本文件补充实际已完成产物。','',
'## 1. 全窗口事实与证据一致性','',
'| 条件 | 样本数 | 完整物理硬限通过 | I峰 pu | Vdc范围 pu | 全窗口平均P kW | 全窗口平均Q kvar | 冻结联合恢复时刻 |',
'|---|---:|---|---:|---|---:|---:|---|']
for r in rows:
 q=summaries[r['case']];m=q['metrics'];t=q['recovery']['joint_recovery_time_s']
 recovery='无故障不适用' if q['event'] is None else ('未达到' if t is None else f'{t:.8f}s')
 lines.append(f"| {r['case']} | {q['accepted_control_count']} | {q['complete_hard_safe']} | {m['I_peak_pu']:.9f} | {m['Vdc_min_pu']:.9f}–{m['Vdc_max_pu']:.9f} | {q['service']['mean_P_W']/1000:.6f} | {q['service']['mean_Q_var']/1000:.6f} | {recovery} |")
lines+=['','每一行的完整时段均从 0.6 s 到 2.75005 s。健康通过是执行对应 fault 的物理/guard 准入，不表示预先未定义的服务透明容差已经通过。健康 reference 正确保留 NOT_AVAILABLE；故障按同一 allocator 的 P0 或 R0 配对，未把旧 Q-priority reference 冒充成配对参考。','',
'## 2. 每个采样和计划的独立重算','',
'| 条件 | 独立重算样本/optimized计划 | nominal最大差 | 共同AW最大差 | plan/index/frame command最大差 | 独立plan最大primal残差 |',
'|---|---:|---:|---:|---:|---:|']
for r in rows:
 x=r['independent_allocator_reference_recovery_checks']
 lines.append(f"| {r['case']} | {x['all_accepted_samples_replayed_algebraically']}/{x['accepted_optimizer_plans_independently_revalidated']} | {x['max_nominal_modulation_error']:.3e} | {x['max_common_AW_error']:.3e} | {x['max_command_plan_index_frame_error']:.3e} | {x['max_revalidated_plan_primal_residual']:.3e} |")
lines+=['','所有已接受 sample 均以独立显式电路/标准分配/PLL/PI/源反馈方程重算名义量，再应用相同 Kaw 的实际新队列修正；逐字段检查全 controller、plant 不变、旧队列晋升和日志。每个 accepted optimized plan 另用独立动力学/terminal/输入/队列/电流/Omega 方程全约束复算。没有以抽样重算替代全 sample 检查。','',
'## 3. 已保存的管、能量、硬限与wall-time','',
'| 条件 | 完整拍Ω/排除部分拍 | Ω最大disk超出 | 保留dense区间/节点 | dense误差减固定管半径最大值 | 硬接触/guard失败 |',
'|---|---:|---:|---:|---:|---:|']
for r in rows:
 x=r['legacy_energy_tube_root_timing_checks'];t=x['observed_next_step_and_dense_tube_check']
 lines.append(f"| {r['case']} | {t['complete_sample_transitions']}/{t['partial_intervals_excluded']} | {t['max_witness_disk_excess']:.3e} | {t['dense_intervals_checked']}/{t['dense_nodes_checked']} | {t['max_observed_error_minus_tube_radius']:.3e} | {x['contacts']}/{x['guard_failures']} |")
lines+=['','Ω判定沿用原 1e−8 数值容差；微小正浮点残差未被改写成精确零。每例末尾 50 us 部分拍单独排除完整一拍Ω声明。dense 只核对实际保留的节点/区间，不能升级成未保留连续时刻的认证或区间证明。','',
'每例还核对全部 summary/NPZ/raw hash、最终全状态、列定义、端点电功率、P/Q/绝对误差积分、SoC、电池/DC/RL能量及守恒残差、contact列表、solver/backup计数和wall-time分位数。','',
'| 条件 | controller实际wall-time median ms | p95 ms | 最大 ms | >100us次数/调用数 |',
'|---|---:|---:|---:|---:|']
for r in rows:
 q=summaries[r['case']];x=q['timing']['seconds']['controller_total_wall_s_including_PI_guard_AW']
 lines.append(f"| {r['case']} | {1000*x['median_s']:.5f} | {1000*x['p95_s']:.5f} | {1000*x['maximum_s']:.5f} | {x['over_100us_count']}/{x['n']} |")
lines+=['','记录的wall-time只用于披露离线成本；100 us虚拟采样时钟没有被当成真实计算deadline已满足。','',
'## 4. 实际150 ms故障服务与边界连续性','',
'| 条件 | 故障平均P kW | 故障平均Q kvar | Q实际积分 var·s | Q绝对请求误差 var·s | 故障段能量守恒残差 J |',
'|---|---:|---:|---:|---:|---:|']
for cid,r in events.items():
 s=r['actual_fault_service'];e=r['actual_fault_energy']
 lines.append(f"| {cid} | {s['mean_P_W']/1000:.6f} | {s['mean_Q_var']/1000:.6f} | {s['Q_actual_integral_var_s']:.6f} | {s['Q_absolute_request_error_var_s']:.6f} | {e['conservation_residual_J']:.3e} |")
lines+=['','实际Q来自 onset/clearance 精确split处的PCC无功quadrature差，并非Q请求误差字段。边界审计确认 .60005/.75005 s 的13维plant/passive/quadrature状态左右精确相同，applied/queued和控制积分器不重置，没有额外控制sample；PCC的P/Q代数跳变按同一瞬时电流和同一held电压独立重算。','',
'保留每个sample左/右电压跳变的dense梯形积分仅作描述性交叉检查，正式服务数值使用已保存的积分状态。','',
'## 5. 冻结恢复判据逐项核对','']
for r in rows:
 if summaries[r['case']]['event'] is None:continue
 x=r['independent_allocator_reference_recovery_checks']['conservative_recovery']
 lines.append(f"- {r['case']}：复算 {x['checks_recomputed']} 次恢复检查，qualifying={x['qualifying_count']}，联合恢复时刻={x['joint_recovery_time_s']}；失败子项次数={x['failed_subitem_counts']}")
 if x['last_check']:
  z=x['last_check'];lines.append(f"  - 最后检查：self={z['self_50ms_difference']:.3e}，matched target={z['same_time_guarded_no_fault_difference']:.3e}，150ms hard safe={z['safe_150ms']}，unclipped including guard={z['unclipped_including_guard_150ms']}，PLL频差={z['PLL_max_error_Hz']:.3e}Hz")
lines+=['','同自身健康参考的轨道误差变小不能替代原联合恢复要求。只要guard仍介入，150 ms无active-limiting项不通过，恢复时刻必须保持None；未放宽定义。独立审计器另经11个合成数组自测，覆盖每个limiting标志、硬限、self/target误差、PLL和“早期违例不能抹除”。','',
'## 6. 有限结论与交付物','',
'通过说明这些冻结条件的数值物理轨迹与其保存证据一致，并提供本条件下的已知标准基线构造性结果。它不表示800/700服务被完整保持，不构成新算法优越性、普遍fast-port可行性/不可行性、联合DC/SoC不变性、机器区间证明、100us实时性或paper-ready声明。','',
'- `audit_artifact_checks.py` / `audit_artifact_results.json`：完整记录、逐sample、plan、管、能量、wall-time和恢复检查','- `audit_event_boundaries.py` / `audit_event_results.json`：故障边界、真实服务及段能量','- `audit_recovery_fixture_tests.py` / `audit_recovery_fixture_results.json`：恢复审计器的11个有限合成反例/正例','- `ARTIFACT_AUDIT_MANIFEST.json`：审计交付物hash','']
(HERE/'INDEPENDENT_ARTIFACT_AUDIT.md').write_text('\n'.join(lines))
files=['audit_artifact_checks.py','audit_artifact_results.json','audit_event_boundaries.py','audit_event_results.json','audit_recovery_fixture_tests.py','audit_recovery_fixture_results.json','build_independent_artifact_report.py','INDEPENDENT_ARTIFACT_AUDIT.md']
manifest={'status':checks['status'],'physical_trajectories_executed_by_audit':0,'real_optimization_calls':0,'files':{f:sha(HERE/f) for f in files if (HERE/f).exists()},'audited_summaries':{r['case']:r['summary_sha256'] for r in rows},'frozen_runner_sha256':checks['source_sha256']['run_constructive.py'],'frozen_wrapper_sha256':checks['source_sha256']['guarded_allocator_controller.py']}
(HERE/'ARTIFACT_AUDIT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':manifest['status'],'report':'INDEPENDENT_ARTIFACT_AUDIT.md','audited':list(summaries)},indent=2))
