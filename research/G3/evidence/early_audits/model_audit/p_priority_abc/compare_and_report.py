"""Read-only reconstruction of saved DQ diagnostics; no DQ simulation/import."""
from pathlib import Path
import json,hashlib,math
import numpy as np
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
jread=lambda p:json.loads(Path(p).read_text())
jwrite=lambda p,x:Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
p=jread(ROOT/'protocol/GATE_A_LOCKED_V2_1.json');dq=np.load(ROOT/'baseline_allocation/results/fast_p_priority_h1e-05.npz');ds=jread(ROOT/'baseline_allocation/results/fast_p_priority_h1e-05.json')
cp=jread(ROOT/'gate_a/preconditioned_dq/h1e-05_checkpoint.json');w=p['omega_base_rad_s'];I=p['I_phase_peak_base_A'];V=p['V_phase_peak_base_V'];W=.5*p['C_dc_F']*1400**2;Eb=p['battery_energy_MWh']*3.6e9

def ctl(n,t):
    ma=complex(n[8],n[9])*np.exp(1j*w*t);mq=complex(n[10],n[11])*np.exp(1j*w*t)
    return np.array([n[4]+w*t,n[12]*w,n[5]*w,n[6]*V,n[7]*V,ma.real,ma.imag,mq.real,mq.imag,n[13]*1e6])
def pair(x):return complex(*x)
def dqdiagnostics():
    before=[];after=[];rows=[];identity=[]
    for k,cc in enumerate(dq['control']):
        t=cc[0];tt=dq['normalized_state'][k+1,0];pre=ctl(dq['normalized_state'][k,1:],t);post=ctl(dq['normalized_state'][k+1,1:],tt);post[0]-=post[1]*(tt-t)
        ep=dq['endpoint_trace'][k];idq=complex(ep[1],ep[2]);vdc=ep[15]*1400;lev=1. if t<.60005 else .4
        udq=pair(pre[5:7])*vdc*np.exp(-1j*w*t);e=V*lev
        vp=(p['grid_L_H']*(udq-p['filter_R_ohm']*idq)+p['filter_L_H']*(e+p['grid_R_ohm']*idq))/(p['grid_L_H']+p['filter_L_H'])
        rot=np.exp(1j*(w*t-pre[0]));ic=idq*rot;vc=vp*rot;vn=abs(vc);floor=.1*V
        a=.8e6/(1.5*max(vn,floor));b=.7e6/(1.5*max(vn,floor));ir=(cc[5]-1j*cc[6])*vc/max(vn,1e-30);ei=ir-ic
        er=vc.imag/max(vn,floor);wu=w+p['pll_Kp_per_s']*er+pre[2];wn=cc[3]*(2*np.pi)
        uu=vc+1j*wn*p['filter_L_H']*ic+p['current_Kp_ohm']*ei+pair(pre[3:5]);us=pair(post[7:9])*vdc*np.exp(-1j*pre[0])
        ki=p['current_Ki_ohm_per_s']*ei;aw=p['current_Kaw_per_s']*(us-uu);S=1.5*vp*idq.conjugate()
        row=[t,abs(idq)/I,vdc/1400,vn/V,er,wu,wn,a,b,cc[5],cc[6],ir.real,ir.imag,abs(ir)/I,ic.real,ic.imag,vc.real,vc.imag,uu.real,uu.imag,us.real,us.imag,abs(us)/abs(uu),ei.real,ei.imag,ki.real,ki.imag,aw.real,aw.imag,cc[4],cc[7],S.real,S.imag]
        rows.append(row);before.append(pre);after.append(post)
        us_expected=uu*min(1,.95*vdc/math.sqrt(3)/abs(uu));zi_expected=pair(pre[3:5])+p['control_sample_s']*(ki+aw)
        identity.append([t,abs(us-us_expected),abs(pair(post[3:5])-zi_expected),abs(post[2]-(pre[2]+p['control_sample_s']*(p['pll_Ki_per_s2']*er+p['pll_Kaw_per_s']*(wn-wu)))),abs(pair(post[5:7])-pair(pre[7:9])),abs(post[0]-pre[0])])
    return np.array(rows),np.array(before),np.array(after),np.array(identity)

D,DB,DA,DI=dqdiagnostics()
np.savez_compressed(OUT/'dq_saved_state_diagnostics.npz',diagnostics=D,controller_before=DB,controller_after=DA,identity_residual=DI,identity_columns=np.array(['t','us_reconstruction_V','zi_update_V','PLL_z_update_rad_per_s','queue_promotion','theta_same_sample_rad']),control_columns=np.load(OUT/'fast_p_priority_abc_h1e-05.npz')['control_columns'])
comparison={};abcdata={}
for h in [1e-5,5e-6]:
    tag=f'fast_p_priority_abc_h{h:g}';a=np.load(OUT/f'{tag}.npz');s=jread(OUT/f'{tag}.json');abcdata[h]=(a,s)
    assert np.max(abs(a['control'][:,0]-D[:,0]))<1e-14
    names=a['control_columns'];diagdiff=abs(a['control']-D);ctscale=np.array([1,w,w,V,V,1,1,1,1,1e6]);scale=np.ones(len(names))
    for k,n in enumerate(names):
        if n in ['a_raw','b_raw','a_limited','b_limited','iref_re','iref_im','i_PLL_re','i_PLL_im','current_error_re','current_error_im']:scale[k]=I
        elif n in ['v_PLL_re','v_PLL_im','uu_re','uu_im','us_re','us_im']:scale[k]=V
        elif n in ['PLL_wraw','PLL_omega_new']:scale[k]=w
        elif n in ['source_command','Ppcc_W','Qpcc_var']:scale[k]=1e6
        elif n in ['Ki_error_re','Ki_error_im']:scale[k]=p['current_Ki_ohm_per_s']*I
        elif n in ['Kaw_residual_re','Kaw_residual_im']:scale[k]=p['current_Kaw_per_s']*V
    before_diff=abs(a['sample_before'][:,-10:]-DB);after_diff=abs(a['sample_after'][:,-10:]-DA)
    ev=a['trace'];last=ev[-1];final=ds['final_plant_state'];abc_i=(2/3)*np.dot(last[3:6],np.exp(-1j*np.array([0.,-2*np.pi/3,2*np.pi/3])))*np.exp(-1j*w*last[0])
    comparison[f'h{h:g}']={'actual_1pu_time_error_s':s['actual_1pu_crossings_s'][0]-ds['current_continuous_crossings_s'][0],'stop_time_error_s':s['stop_s']-ds['final_time_s'],'pre_sample_normalized_state_max_error':float(max(abs(a['normalized_before'][:,1:]-dq['normalized_state'][:-1,1:]).ravel())),'controller_before_normalized_max_error':float(max((before_diff/ctscale).ravel())),'controller_after_normalized_max_error':float(max((after_diff/ctscale).ravel())),'diagnostics_normalized_max_error':float(max((diagdiff/scale).ravel())),'diagnostics_max_absolute_error_by_field':{str(n):float(max(diagdiff[:,j])) for j,n in enumerate(names)},'final_nominal_dq_current_error_pu':float(abs(abc_i-complex(*final[:2]))/I),'final_Wdc_error_J':float(last[6]-final[2]),'final_Pbat_error_W':float(last[7]-final[3]),'final_battery_energy_error_J':float(last[8]-(.5*Eb+final[4]))}
# Constants, coordinate signs, clipping and antiwindup identities use abc data only.
a,s=abcdata[1e-5];tr=a['trace'];d=a['control'];ctlcols=a['sample_state_columns']
iab=(2/3)*(tr[:,3:6]@np.exp(-1j*np.array([0.,-2*np.pi/3,2*np.pi/3])))
const={'Vpeak_from_LLrms_error_V':V-p['V_LL_rms_base_V']*math.sqrt(2/3),'Ipeak_from_Irms_error_A':I-p['I_rms_base_A']*math.sqrt(2),'Sbase_from_peak_convention_error_VA':1.5*V*I-p['S_base_VA'],'Iabc_vs_complex_norm_max_error_pu':float(max(abs(abs(iab)/I-tr[:,16]))),'P_positive_Q_positive_reference_check':'iref=(a-jb)*v/|v| gives 1.5*v*conj(iref)=1.5*|v|*(a+jb); positive b means positive exported Q under saved convention','iref_power_identity_max_error_VA':float(max(abs(1.5*(d[:,16]+1j*d[:,17])*np.conj(d[:,11]+1j*d[:,12])-1.5*np.hypot(d[:,16],d[:,17])*(d[:,9]+1j*d[:,10])))),'a_clip_max_error_A':float(max(abs(d[:,9]-np.clip(d[:,7],-.95*I,.95*I)))),'b_clip_max_error_A':float(max(abs(d[:,10]-np.clip(d[:,8],-np.sqrt(np.maximum(0,(.95*I)**2-d[:,9]**2)),np.sqrt(np.maximum(0,(.95*I)**2-d[:,9]**2)))))),'general_source_differences_inactive':{'P_preclip_in_DQ_only':'800kW is below950kW cap','reference_basis_denominator':'ABC uses max(V,0.1Vbase), DQ uses max(V,epsilon); minimum sampled V=.3666405837pu > .1pu, so identical on this trajectory','auxiliary_power_in_ABC_only':'locked auxiliary_power_W=0'}}
pre=a['sample_before'][:,-10:];post=a['sample_after'][:,-10:];zi_delta=(post[:,3]+1j*post[:,4])-(pre[:,3]+1j*pre[:,4]);expected=p['control_sample_s']*((d[:,25]+1j*d[:,26])+(d[:,27]+1j*d[:,28]));const['abc_current_PI_update_identity_max_error_V']=float(max(abs(zi_delta-expected)))
const['abc_queue_promotion_max_error']=float(max(abs((post[:,5]+1j*post[:,6])-(pre[:,7]+1j*pre[:,8]))))
const['abc_voltage_limit_never_active']=bool(np.all(d[:,22]>=1-1e-12));const['abc_antiwindup_zero']=bool(np.max(abs(d[:,27:29]))==0)
# All explicitly compared states and signals are pre-update or post-update aligned.
firstclip=int(np.flatnonzero((abs(d[:,7]-d[:,9])>1e-7)|(abs(d[:,8]-d[:,10])>1e-7))[0]);firstpll=int(np.flatnonzero(abs(d[:,6]/(2*np.pi)-75)<1e-10)[0])
windows=[]
for k in sorted(set([0,firstclip,3,4,firstpll,len(d)-1])):
    windows.append({'t':float(d[k,0]),'Iactual_pu':float(d[k,1]),'PLL_error':float(d[k,4]),'PLL_Hz':float(d[k,6]/(2*np.pi)),'raw_a_A':float(d[k,7]),'raw_b_A':float(d[k,8]),'limited_a_A':float(d[k,9]),'limited_b_A':float(d[k,10]),'Iref_pu':float(d[k,13]),'uu_PLL_V':d[k,18:20].tolist(),'us_PLL_V':d[k,20:22].tolist(),'zi_before_V':pre[k,3:5].tolist(),'zi_after_V':post[k,3:5].tolist(),'current_aw_term_V_per_s':d[k,27:29].tolist()})
refinement={'purpose':'Only same physical condition refined because both actual-current contacts occur; no strategy/parameter/physical-condition search','stop_time_5us_minus_10us_s':abcdata[5e-6][1]['stop_s']-s['stop_s'],'current1_time_5us_minus_10us_s':abcdata[5e-6][1]['actual_1pu_crossings_s'][0]-s['actual_1pu_crossings_s'][0],'sample_normalized_max_difference':float(max(abs(abcdata[5e-6][0]['normalized_before'][:,1:]-a['normalized_before'][:,1:]).ravel())),'dc_max_difference_pu':abcdata[5e-6][1]['Vdc_max_pu']-s['Vdc_max_pu']}
summary={'verdict':'SAME_MODEL_DYNAMICS_REPRODUCED','scope':'One frozen fast P-priority physical condition, independent abc integration at10us and5us. DQ state/trajectory files are read only for shared initialization and offline comparison; no DQ runtime controller/allocator/RHS imports.','comparison':comparison,'refinement':refinement,'units_signs_and_control_identities':const,'same_window_control_snapshots':windows,'DQ_saved_state_reconstruction_max_identity_residual':dict(zip(['us_V','zi_V','PLL_z','queue','theta'],np.max(abs(DI[:,1:]),axis=0).tolist())),'limitations':['Model-level independent coordinate/integration check only; not hardware/DC/DC topology calibration or validation','Physical actual-current hard constraint is1.0pu with zero overload allowance;1.1pu is a numerical emergency termination only','No clearance, post-stop recovery or service feasibility is demonstrated','Tiny roundoff/integration differences are not independent physical evidence; general low-voltage/control request branch differences remain outside this single trajectory']}
jwrite(OUT/'COMPARISON.json',summary)
np.savetxt(OUT/'same_window_control_snapshots.csv',d,delimiter=',',header=','.join(a['control_columns']),comments='')
report=f'''# 严格 P 优先基线的独立 abc 复核

## 结论

同一合成受控 DC 端口、同一完整初态、同一控制时钟与调制队列下，独立 abc 实现复现了既有 DQ 的动态：实际电流先越过 1.0 pu 硬约束，随后在 1.1 pu 数值紧急阈值终止。电流参考始终不超过 0.95 pu；DC 电压没有接触上界。这支持“本单一工况结果属于相同模型动态”，不支持硬件保护、实际 DC/DC 拓扑或完整故障穿越的验证结论。

- abc 10µs：实际 1.0pu 接触 {s['actual_1pu_crossings_s'][0]:.16f}s；数值停止 {s['stop_s']:.16f}s
- 既有 DQ 10µs：实际 1.0pu 接触 {ds['current_continuous_crossings_s'][0]:.16f}s；数值停止 {ds['final_time_s']:.16f}s
- abc 5µs：实际 1.0pu 接触 {abcdata[5e-6][1]['actual_1pu_crossings_s'][0]:.16f}s；数值停止 {abcdata[5e-6][1]['stop_s']:.16f}s
- abc 10µs 的 DC 电压范围 {s['Vdc_min_pu']:.12f}–{s['Vdc_max_pu']:.12f}pu；Iref 峰值 {s['iref_max_pu']:.15f}pu
- 10µs abc 与既有 DQ 的采样前完整归一化状态最大差 {comparison['h1e-05']['pre_sample_normalized_state_max_error']:.3e}；采样后控制状态最大归一化差 {comparison['h1e-05']['controller_after_normalized_max_error']:.3e}
- abc 10/5µs 采样前状态最大归一化差 {refinement['sample_normalized_max_difference']:.3e}；停止时间变化 {refinement['stop_time_5us_minus_10us_s']:.3e}s

## 固定条件和独立性

唯一物理条件是 fast_p_priority：P=800kW、Q=700kvar；源电压在 .60005–.75005s 为 .4pu；端口 tau=.002s、爬坡±50MW/s；其余 V2.1 参数保持。100µs 控制采样、先测量旧 applied 调制、再释放 queued、一拍归一化静止坐标调制队列均保留。实际电流 1.0pu 是硬约束，1.1pu 仅用于阻止继续无意义积分，不是经验证的保护动作。

运行仅导入原 reference_abc.py 与 preconditioned_abc.py。复用原 abc 电路 RHS、代数、RK4、轨道归一化和停止裕量；原文件未修改。sample 的控制文本只把 Q 优先两行换成严格 P 优先：先裁剪 a，再按剩余圆半径裁剪 b；诊断仅返回局部变量、保存只读快照。PI、PLL、反饱和与所有控制增益未改。运行时未导入 DQ 控制器、allocator 或 RHS。IMPLEMENTATION_AUDIT.json 保存精确差分、输入散列与参数变更清单。

独立性是坐标、电路积分实现与控制代码实现的独立复核，仍共享冻结数学模型和输入参数，不是另一物理拓扑或实机证据。

## 完整共同初态

直接转换冻结的 .6s DQ 检查点：iabc=Re((id+j iq)exp(j omega0 t)exp(j[0,−2pi/3,+2pi/3]))；Wdc、Pbat、Ebat、PI/PLL 积分、绝对 PLL 角度/频率、applied/queued 调制和源命令全部保留。共同初态归一化误差 {s['full_same_initial_state_normalized_max_error']:.3e}。原独立 abc .6s 检查点与共同 DQ 检查点差 {s['independent_original_abc_checkpoint_normalized_max_difference']:.3e}，作为旁证列出，本次不使用其微小偏差启动。

abc 的累积功率诊断从本次 .6s 起置零，不进入 RHS 的动力状态反馈；原 DQ 累积诊断仍完整保存在输入检查点。DQ 检查点未保存“上次参考电流”，它不进入动力学；首采样前明确记 NaN，首采样后逐点保存。因此不把缺失的无反馈诊断量伪称为已恢复。

## 符号、基值与同窗控制检查

相电压峰值=线电压 RMS×sqrt(2/3)，相电流峰值=相电流 RMS×sqrt(2)，三相功率=1.5×峰值空间矢量乘积。abc 的 sqrt(2/3 sum(iabc²))/Ipeak 与复空间电流范数一致。iref=(a−jb)v/|v| 对应正 P、正 Q；正 b 是正无功注入，未翻转符号。

采样 PCC 最低 {s['sample_Vpcc_min_pu']:.12f}pu，大于 .1pu floor。原 abc 与 DQ 在极低压参考基矢分母写法不同，以及 abc 未预裁剪 P 请求的通用差别，在本窗均未激活：P=800kW<950kW；辅助功率冻结为零。

故障后首次控制更新 .6001s 即把 a 裁到 .95Ibase，b=0；裁后 Iref 范数仍 .95pu。原始/裁后参考、电流反馈、PLL 误差、uu/us、PI 更新前后值和 Ki/反饱和项全部逐采样保留。电压限幅比始终 1，因此电流 PI 反饱和残差恰为零，并不能把实际越界归咎于已激活的电压反饱和。PLL 在 {float(d[firstpll,0]):.7f}s 首次达到75Hz上界；该时间晚于电流首次1.0pu接触，不将相关性单独当作因果证明。

DQ 比较诊断仅从既有 endpoint/control/normalized_state 重建，同窗分别匹配更新前和更新后；不再次运行 DQ，不偷换控制器。COMPARISON.json 含逐字段误差、队列提升/PI/PLL 更新恒等式，以及关键同窗快照。

## 数值与输出边界

10µs 发生边界接触，因此只对完全相同物理条件作5µs必要细化。每100µs边界与外部事件精确切分，1.0pu向上根和终止根以独立 RK4/二分定位，状态不投影。保存每积分步原始 abc 状态及完整控制状态、每采样前后完整状态、全部控制局部量。此复核没有运行故障清除或恢复阶段，也不判断原请求的长期 P/Q 服务成功。

10µs 后检查点能量守恒残差：AC {s['energy']['ac_residual_J']:.3e}J，DC {s['energy']['dc_residual_J']:.3e}J，电池 {s['energy']['battery_residual_J']:.3e}J；电池残差含约3.6GJ绝对能量减法的浮点抵消。本窗微小残差与10/5µs一致性共同支持数值复核，未替代硬约束检查。

文件：fast_p_priority_abc_h1e-05.* 与 h5e-06.* 为原始结果；dq_saved_state_diagnostics.npz 为既有 DQ 的离线重建；same_window_control_snapshots.csv 为逐采样可读导出；COMPARISON.json 为判定与误差；diagnostic_window.png 为同窗六面板图；README_REPRODUCE.md 说明复现命令和数组语义；VALIDATION.json 为自检；MANIFEST.json 为文件散列。
'''
(OUT/'REPORT_ZH.md').write_text(report)
# All source and baseline input bytes are checked again after both runs/reporting.
audit=jread(OUT/'IMPLEMENTATION_AUDIT.json')
assert all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in audit['input_sha256'].items())
files=[f for f in sorted(OUT.iterdir()) if f.is_file() and f.name!='MANIFEST.json']
manifest={'scope':'Single-condition independent abc P-priority verification','verdict':summary['verdict'],'source_inputs_unchanged':True,'files':[{'path':str(f.relative_to(ROOT)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files],'input_sha256':audit['input_sha256']}
jwrite(OUT/'MANIFEST.json',manifest)
print(json.dumps({'comparison':comparison,'refinement':refinement,'units_and_signs':const},ensure_ascii=False,indent=2))
