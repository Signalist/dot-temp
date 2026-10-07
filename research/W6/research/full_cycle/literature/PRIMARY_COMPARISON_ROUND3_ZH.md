# W6第三轮：一手文献对照与主张收窄

核查日期：2026-10-04，05:35–05:58 UTC。只读原论文、作者/机构页面、正式数据卡和厂家文档；未下载论文全文或外来可执行程序，未操作GPU。05:52补充取得一个719KB官方Azure长度CSV及其开放许可，见data_candidate/。

## 1. 先给结论

本轮没有找到同时处理“未知任务工作量W、真实功率连续slew、一般递增凹服务s(p)、EOS后恢复成本”的同一全局结构定理。这个否定检索结果不是首创证明。

**相比第二轮必须补强的前史是转换成本文献。** PPACE 2004、Xu–Melhem–Mossé 2007和Bini–Scordino 2009已经处理随机任务、速度转换时间/能量、idle功率；2007文献还保留当前速度状态并给全局动态规划/近似保证。因此不能把“未知结束＋非零初态＋恢复/转换费用＋不用局部启发式”这一整组词当作新意。

仍可审慎保留的窄候选是：对特定连续实际功率模型，primitive换元、可行支配投影、terminal-cost曲率之间的组合结构。高初态的强制最快下降段若成立，是该结构的边界扩展，不是首次处理带状态转换成本的随机调度。本轮新的全周期双重支配、hazard阈值与最大桥结果另见NEW_STRUCTURE_POSITIONING_ZH.md，其数学核验见theory/audit文件；“旧变换后终端项非凸”本身不是新算法或不可解性的证明。

## 2. 四个指定近邻：逐式核对

### L01 PACE，Lorch–Smith，SIGMETRICS 2001

[作者机构PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2004/07/pace.pdf)，§3–4.2。本轮重新读到work-coordinate schedule、tail distribution和期望能量推导。§4.1的立方功率案例为

`min ∫_0^L S(x) v(x)^2 dx，约束 ∫_0^L dx/v(x)=D`，从而速度按`S(x)^(-1/3)`变化，并受可用速度范围限制。

这里L是既有算法的pre-deadline cycles；PACE保持其pre-deadline work和post-deadline profile，因此保持原文的effective completion-time表现。不能把它笼统改写为W有界且必达hard deadline的模型。§4.2是有限跳变的piecewise-constant近似，没有连续真实功率斜率约束或EOS恢复终端费。

### L02 Anselmi–Gaujal，MASCOTS 2022

[作者PDF](https://polaris.imag.fr/jonatha.anselmi/single-task-energy-opt.pdf)，§II-C、式(3)–(10)、Propositions 1–2、Theorem 1、§V。

§II-C明确假设变化即时、无额外能耗，忽略ramp，EOS立即休眠。式(10)优化有序work切换点：`min Σ_i Q(v_i)∫_(x_(i−1))^(x_i)S(w)dw`，约束`Σ_i(x_i−x_(i−1))/v_i≤D`。Proposition 1给凸性；在既有速度/功率假设下，F严格递增给严格凸，F连续给可微。两者不能互换。Proposition 2证明存在不降速度profile。§V的提前δ激活只是建议启发式，明确留下详细分析。

**覆盖**：随机work＋凸优化和结构；**未覆盖**：连续slew、EOS功率依赖恢复费、本文primitive变换。

### L03 Anselmi–Gaujal，ORL 64 (2026), 107379

[2025-09-26作者稿](https://polaris.imag.fr/jonatha.anselmi/Energy-WC.pdf)，[出版页](https://www.sciencedirect.com/science/article/pii/S0167637725001403)。本轮重新读六页作者稿，而非假定最终排版内容逐字一致。

式(1)–(4)：`Q(v)=P(v)/v`，`E=∫S(w)Q(v(w))dw`，`∫dw/v(w)≤D`。Assumption 1要求Q凸且增。Theorem 1式(6)在未触及速度上限时为`v(w)^2 Q′(v(w))=λ*/S(w)`。未见ramp或EOS恢复项。其`λ*`是hard-deadline对偶量，不是W6的期望完成时间权重。独立代入`s(p)=kp^β`可见Q凸条件通常仅对应`β≤1/2`，不能用这篇稿件直接包办所有`0<β<1`。

### L04 Lipp–Boyd，International Journal of Control 87(6), 2014

[作者页](https://web.stanford.edu/~boyd/papers/speed_opt.html)，[作者PDF](https://web.stanford.edu/~boyd/papers/pdf/speed_opt.pdf)。网页抽取失败后，本轮在dot云浏览器直接读PDF页3、7–8。§3式(2)要求`(q_dot²,q_ddot,u)∈C(q)`且C为凸集；§5式(24)–(26)用`a=theta_ddot,b=theta_dot²`得到`b′=2a`及`min∫b^(-1/2)dtheta`。

该方法是强工具前史，作者也追溯更早路径参数化。独立映射W6时`b=s(p)^2,a=s′(p)p_dot`，于是`|a|≤R s′(s^(-1)(sqrt(b)))`。幂函数凹服务时右侧是负幂凸函数，其下图一般非凸。故不能直接把W6当作式(26)已覆盖的凸约束特例。反之，使用进度换元本身不能列为新工具。

## 3. 本轮新增的近邻：不能漏掉转换成本

### L05 Xu–Xi–Melhem–Mossé，Practical PACE，EMSOFT 2004

[会议原论文](https://websrv.cecs.uci.edu/~papers/emsoft0405/docs04/p54.pdf)，§2.2–2.3、§5.4、Theorem 2。固定work相位边界、离散速度、不限制功率函数；idle可用`e(v)=(P(v)−P_idle)/v`扣除固定基线。§5.4讨论在energy-time labels加上依起止速度变化的time/energy overhead；Theorem 2给FPTAS。

**关键限定**：正文随后明确为与PACE/GRACE比较而把overhead设为零；不能把实验读成验证了非零转换开销。它也不优化连续ramp内有用服务。此文适合引用“实际转换开销早已被纳入随机DVS”，不适合冒充W6的硬slew全局定理。

### L06 Xu–Melhem–Mossé，A Unified Practical Approach to Stochastic DVS Scheduling，EMSOFT 2007

[会议原论文](https://www.cecs.uci.edu/~papers/esweek07/emsoft/p37.pdf)，§3.1式(1)(2)、§5.2–5.3、Figures 6–7。模型为重复固定frame、固定任务次序、离散速度；转换penalties为`PT(vi,vj)=ξ1|vi−vj|`、`PE(vi,vj)=ξ2|vi²−vj²|`。§5.2的值函数显式依赖当前速度；§5.3再加work-bin状态，使用条件survival并允许随机EOS转入下一任务。全frame固定基线被扣除，末任务后初始化为零值。

**必须正面对照**：随机任务＋不reset速度状态＋转换成本＋全局DP/近似保证已有明确先例。其转换是附加时间/能量penalty，不是`dx/dt=s(p)`在连续ramp全程服务；末端也不是W6的`H(p_EOS)`恢复收费。改用同状态DP检验W6是合理基准，但不能直接复用其penalty公式替代物理slew。

### L07 Bini–Scordino，Optimal two-level speed assignment，IJES 4(2):101–111，2009

[机构记录](https://iris.unito.it/handle/2318/1608658)，[公开最终PDF](https://iris.unito.it/retrieve/e27ce42a-d6e3-2581-e053-d805fe0acbaa/officialPaper.pdf)。本轮云浏览器直接读最终页103–106，避免只引2006预稿或摘要。

§2.1定义mode`(α_k,p_k,o_k,e_k)`；转换时间/能量只依目的mode，独立于出发mode及当前状态。§3.1式(7)是expected active energy；式(9)(10)计入EOS以后直至固定周期T的idle能量。令`γ(x)=E[min(C,x)]`，式(10)包含`(e_H−p_I o_H)S(C_x)`及两段`(p_k−p_I)/α_k`的work项。§3.2优化的是两个速度及一个切换点。

**最紧边界**：已有随机任务active＋idle＋转换费用的解析优化；但这里idle-entry overhead不依EOS功率，时间边界是固定T，且政策限两档。它不是可变cycle结束时刻、连续slew、任意profile的完整覆盖。

## 4. 非零初态与全周期：怎样准确描述候选贡献

下面是本审计对W6的建议，**不是上述论文中的结论**。

- 高初态不应写成“以前随机调度只能从零开始”；L06明确以当前速度作状态
- 如能证明`z_0>A(p*)`时任意可行profile受`z≥z_0−Rx`约束，并被某个保持初态/斜率的pointwise projection支配，可准确称为“高初态下无需优化的最快下降前缀＋剩余凸子问题”
- 下降前缀应含其间随机EOS的成本，尾问题应明确是否条件于生存到接合work点；不能只在仿真里裁掉前缀
- 当收费到恢复完成时，`H(z)=[p²/2+c p]/R`中的c必须说明由哪些时间/idle费用组成。`H″=(s−(p+c)s′)/(R s³)`，terminal非凸仅说明旧充分凸性论证失效；不说明全体可行profile上的泛函必非凸，更不排除另一个变量或端点分解
- 要排除“只是普通DP重新命名”，需要给可核验全局结构、复杂度/误差保证或可计算证书，再和同信息同成本DP比较

## 5. 推荐的公平文献基准

1. **同模型全状态DP/最短路**：状态含work和当前真实p，使用相同F、ramp内服务、EOS恢复费、p0及功率边界。L06是方法前史，不是可以原封不动搬来的数值模型
2. **受限简单政策**：一个目标功率、最快可行升降、EOS最快恢复；优化目标功率，给所有成本。用于量化复杂profile是否值得，不称现有文献最优
3. **clairvoyant W下界**：每个W分别优化再取期望，明确拥有额外信息；不得作为可部署对手
4. **PACE/Anselmi近邻**：如展示其profiles，应在同deadline或同latency条件下重求，并加物理ramp可行化与恢复计费；裸能量不能直接比较，因为hard deadline与`λ E[T]`不是同一合同
5. **全周期结构的压力测试**：高/低hazard、原子EOS、非零高p0、facility-idle费用、s的线性/严格凹/无critical-root边界。展示局部解是否与global bound闭合，比增加几个profile图更有论文价值

## 6. 可立即利用的公开数据证据与边界

详见同目录`PUBLIC_DATA_SCOPE_ZH.md`。本轮找到NLR 2026的公开H100时序数据页与Azure真实output lengths；后续实际取得719KB的Azure 2023 conversation文件并计算经验PMF。两者**不能拼成同一实测“EOS＋可控p＋s(p)”实验**。NLR整包约1GB且原站许可与镜像标记不同，未下载。ML.ENERGY v3 schema更接近所需字段，但原始文件有联系信息分享gate，未访问。

## 7. 检索范围与停止条件

完成指定四篇直接复核，并向前/后追至PPACE 2004、统一随机DVS 2007、二速active-idle 2009。额外检索了unknown-size、stochastic speed scaling、slew/ramp/derivative constraints、transition overhead、initial/current speed、recovery/full-cycle等组合。未找到连续slew全周期精确同模型结构；不声称穷尽控制、运筹、专利或所有2026文献。

网页抽取失败与访问gate分开记录：Lipp–Boyd和IRIS PDF通过正常云浏览器公开界面读取；ML.ENERGY文件gate未尝试替代路径。论文只保存自主总结、最少必要公式、书目信息和URL；另外保留获开放许可的Azure CSV、许可和派生统计。旧文献目录哈希校验文件另附。
