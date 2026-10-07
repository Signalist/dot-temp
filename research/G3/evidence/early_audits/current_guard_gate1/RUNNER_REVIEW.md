# Gate1 runner 只读复核

日期：2026-10-02 UTC。runner SHA256：`9e4ca7f83570e6e62bf7f3fef9096cde5c44782a0ca7b27026dcd47978662eae`。

审计不调用物理run、RHS或积分器，不修改runner、已审计guard/wrapper、冻结协议或既有轨迹。审计只阅读源码、运行独立静态/评分函数检查，并复算新生成的模型记录。

## 静态结论

未发现要求立即停止已获批C0执行的driver阻断项。`audit_runner_checks.py` 的纯函数/静态检查通过，输出为 `audit_runner_results.json`。该结论不代表C0或故障门结果已通过。

### 时钟、队列及接口

- 物理采样时刻为整数k乘100μs，从k=6000的.6s起；guard相对样本为k−6000。六个原定结束时刻的离线时钟算术已逐一核对，末段50μs或1μs截断不会被伪装成完整100μs保持段
- 名义控制器及wrapper均从pre-update状态取样；实际保持段使用提升后的旧queued，新safe modulation仅进入queued。原队列推进/抗饱和不变量逐拍写入raw记录
- 源、故障事件和评分对象只在driver；guard只获得当前电气测量及数值参数。事件准确分割物理积分段，不泄露给预测器
- wall-clock测量使用perf_counter/monotonic；仿真时间由整数采样钟推进，求解器耗时不改变仿真时钟。这是离线虚拟采样模型，不能声称真实100μs调度

### 左右点、root与终止保存

- pre-sample旧applied点、queue提升右点、事件左右点均分别计分。`row_margins`直接读取存储行的I/Vdc/P/Q/Pb/SoC列，已用人工行复核索引；没有再用更新后的ctl重算旧行P/S
- 每段DOP853采用原rtol1e−10、atol1e−8、10μs最大步，并对全部声明的硬限构造向下穿越root；source幅值或applied调制引发的代数跳变在右点显式检查
- C0在实际I=1接触即停。故障门可记录I=1并按原更高数值阈值继续作诊断，但该接触不会从最终失败证据中消失；guard失域仍独立停止
- root保存完整13维augmented state、正确推进到root时刻的PLL相位、controller和源左/右水平。terminal记录与NPZ最终状态均保留；没有物理state projection
- extrema是内部数值节点和边界左右点的观测，另存root；它们不是严格区间外界。未以采样极值替代连续形式证书

### 日志、用时与健康门控

- 每个成功采样保留完整pre/post plant、PLL/PI/source/queue、名义/安全输入、AW、solver/primal、完整backup plan；失败保留原状态与异常。压缩日志不省略100μs样本
- 纯函数测试用9999s等人工仿真timestamp注入TimingSummary，确认其没有进入wall-time统计；setup/solve/validation/point-total、guard total与wrapper total分别保留
- C0-fast必须在C0-slow记录之后；任何fault之前要求两个C0记录。对应端口C0未物理准入时fault拒绝，并维护NOT_RUN_PENDING_REVIEW。前序可准入端口按冻结顺序执行
- 10μs主记录和5μs同条件细化受严格路径保护；没有hard contact/near-boundary理由的细化拒绝。已有started或结果文件不覆盖、不静默重试
- 健康physical admission必须完整完成、无硬接触/超限、无guard失败。service transparency没有预注册容差，故保持未判定，单独保留800/700绝对误差、匹配参考差与初始.21458干预
- 既有slow无guard参考仅覆盖.6–1.4s且缺完整normalized state；代码明确只报共同观测窗口、缺失后续覆盖，不伪造其尾段。fast参考列定义与本次26列一致，已直接核对

## 闭环记录复核方案与当前状态

完整产物审计将交叉核对raw/NPZ/summary的hash、样本计数、状态与queue连续性、逐拍接口、硬接触、终态、service/inventory、extrema和timing统计。还将逐个完整100μs保持段把已保存实际末态变换到同一因果source frame，独立求解相对对应z_{j+1}或终端中心的两个Ω见证。最后不足100μs保持段单独列出，不计作一步递归包含。

保留dense节点将相对该拍起始坐标，用独立复数RL公式重算名义flow并比较固定电流误差管半径。这只核验已保存节点，不生成新轨迹，也不替代未采样区间的证明。

在C0-slow仍运行时，先读raw前100个完整区间（.6–.6100s）：全部满足1e−8数值Ω判据；最大disk超量为+8.1836e−13。该正微差已保留，因此只能称数值包含，不能升级为严格实数/区间包含。完整记录结论见下方已完成的追加复核。

## 保留范围

本runner审计不增加场景、不调整N/K/限值、不改变既有控制策略；不声称机器外向舍入、联合DC/SoC不变性、硬件实时性、服务透明性或六门完成。固定冷启动实现的wall time不代表成熟MPSC极限。

## C0-slow 完整记录复核

已完成.6–2.75005s全记录复核，结果为 `PASS_COMPLETED_ARTIFACT_RECONCILIATION`：

- 21,501个sample update和interval；raw、NPZ与summary的计数、完整状态、队列、终态、hard-contact、service及timing统计一致
- 所有21,501次选择均为数值可行optimized计划；guard失败、硬接触与非最优接受均为0。模型完成，故该端口physical admission=true；不等于service transparency通过
- 21,500个完整100μs实际末态的独立Ω逆见证全部满足1e−8数值判据。最后50μs段仅作为已观测partial interval保存，未计作完整一步包含
- 最大见证disk范数为.08638673804243822，对r的最大超量为+8.18359269239e−13；最大逆重构残差2.77556e−17。正微差没有隐藏，不将其称为严格实数归属
- 首5ms保留的50个interval共核查846个节点计次（边界有重复）：最大观测电流误差为.14298892347313594pu，较固定误差管半径.17251346147039706pu尚余.029524537997261124pu；无数值管外点。其余未保留dense区间没有冒充逐节点观测
- 原AW公式逐拍误差最大7.10543e−15；sample/frame/queue记录一致。真实闭环未发生backup切换，故backup的动态执行不能从本C0结果宣称已经验证；其函数级强制测试结论仍独立保留
- 平均实际P=705.517069920kW、Q=644.839353594kvar；相对800/700请求的平均绝对误差为94.482930079kW、55.161146658kvar。21,500次guard干预及.214580692240首次干预完整保留
- raw SHA256：`ae002dd18174105fba3857a90334ddfb82de9c972e1678dcebabebcc0ed583b0`
- NPZ SHA256：`15691ce04b6a0b889d4ce53e1b374eed2e91b8a094bfc6eea4232374627bd60b`

该复核区分了计划primal与实际模型转移：前者不足以替代后者；这里已对完整实际采样转移逐一复算，但结论仍是冻结模型与有限精度下的数值包含，不是外向舍入证明、无限时域保证或联合DC/SoC证书。

补充：独立按冻结公式复算所有endpoint的PCC P/Q、逆变器P、电流范数、Vdc、SoC和能量余额，并复算末态inventory各差量，全部与保存行和summary一致。未重新积分。


## C0-fast 完整记录复核

21,501个update/interval与raw/NPZ/summary一致；所有调用为optimized，零guard失败、硬接触或非最优接受。物理模型完整到2.75005s，physical admission=true。

21,500个完整100μs实际转移的独立Ω逆见证全部满足1e−8数值判据，最后50μs不计入整步。最大disk超量+4.30282198760e−12，最大逆重构残差5.55112e−17；这些数值微差仍不等于严格集合归属。首5ms保留50个interval、846个节点计次，最大观测电流误差.1433868570366351pu，误差管余量.02912660443376197pu。零管外节点；AW最大误差7.10543e−15。

全部endpoint的P/Q/Pinv、能量、库存、计时及控制状态连续性独立复算一致。真实运行没有触发shifted/terminal backup，不能把函数级故障注入测试说成真实闭环切换已经发生。

健康平均实际P=705.440974962kW、Q=644.794605454kvar；平均绝对请求误差P=94.559025037kW、Q=55.205894798kvar。physical admission不等于800/700服务保持。

raw SHA256：`27aec08b83df375bbaf1025aeb44ddea9033aa502e0570599b1cf4f817f28c22`；NPZ SHA256：`9b08b8226fffcf29d072822cd5eb52254690e9dc77709f08a4ac7c78b4226259`。

## 四个故障主记录：审计通过，物理门失败

以下“审计通过”只说明产物与代码/保存数据一致。四故障均在DC上界1.1pu停止，清除及恢复均未观测；没有完整150ms故障轨迹。电流和Ω检查仅限各自DC停止之前。

|条件|DC高界停止时刻s|故障后观测时长ms|观察到的峰值I pu|完整100μs转移数|partial段|
|---|---:|---:|---:|---:|---:|
|C50-slow|0.606274325705|6.224325705|0.888168876370|62|1|
|C50-fast|0.608646762771|8.596762771|0.888169283936|86|1|
|C1-slow|0.606193109520|6.192109520|0.908225709781|61|1|
|C1-fast|0.608363635476|8.362635476|0.908225709781|83|1|

四条主记录均有完整root/terminal状态及PLL/PI/source/queue，二者逐字段完全相等。保存的真实完整采样转移均满足Ω数值判据，所有保留dense节点均位于电流误差管中；每条停止前的全部interval均保留dense。末不足100μs保持段没有冒充一步包含。

所有solver均返回成功并通过primal；没有guard失效或backup选择。现象是条件电流层没有阻止DC充能越过上界，不是以SLSQP失败为物理不可行依据。当前层资格不能因电流未触1.0而升级为全装置安全。

独立重算实际onset的必要能量不等式：慢端口的峰前缀积累外下界约8870.6136J，高于约4341.2501J联合DC/RL余量，首次外障碍约17.0882ms；本固定controller在约6.2ms已提前触DC界，两者不矛盾。快端口的相同放宽不等式峰前缀仅约887.0614J，未排除其他安全控制；快端口本次guard失败不能扩大成“任何控制都不可能”。

## 同条件5μs细化复核

依据 `REFINEMENT_RULE_APPLIED.json`，只细化四个已触DC硬界的原故障条件。没有重复C0长轨迹、增加场景或更改控制钟、冷启动solver、N/K、初态、事件/清除时刻及端口参数。所有5μs结果另存，10μs主记录完整保留。

|条件|5μs DC停止时刻s|相对10μs停止差s|峰I差pu|
|---|---:|---:|---:|
|C50-slow|0.606274325508|-1.97371e-10|3.94018e-13|
|C50-fast|0.608646762899|1.28033e-10|-5.57332e-14|
|C1-slow|0.606193109294|-2.25473e-10|-2.5091e-14|
|C1-fast|0.608363635275|-2.01896e-10|-2.498e-14|

最大停止时间差2.255e−10s，最大峰I差3.941e−13pu；这说明所观察DC硬停止对10/5μs数值步长稳定，但不是区间误差认证。四个refined raw/NPZ/summary、root/terminal状态、库存/能量/计时与每步Ω/dense误差管全部核对通过。

另由冻结功率与损耗代数独立计算，DC触界处Wdot仍为正277–669kW，确属明显向外穿越而非接近零导数的擦边接触。该判断只用保存终态与held modulation，没有新积分。

## 最终审计结论

六个主条件加四个同条件数值细化产物全部可复核：两个C0完成并取得数值物理准入；四故障均在清除前触DC高界并停止。因此不能宣布current_guard_qualified、paper_ready、全故障电流安全、完整恢复、全装置认证或100μs实时可用。

最终结果文件：`audit_runner_results.json`（每条含case与h_s，主记录/细化清楚区分）、`audit_refinement_results.json`。独立复核入口为 `audit_runner_checks.py`；审计本身执行物理轨迹数始终为0。原guard/wrapper/runner及冻结协议hash未变。
