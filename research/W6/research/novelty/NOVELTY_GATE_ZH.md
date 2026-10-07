# W6第一关主贡献与原始文献的定理级比较

核查日期 2026年10月4日 UTC

## 结论

**本关判定为 CONDITIONAL（窄理论稿可以继续，首创性和高创新性未确认）。** 直接原文检查支持把主线收窄为“特定连续实际功率全周期模型中的无损恢复域，以及幂律服务的尖锐尾hazard凸性边界”。在已逐式核对的近邻中，这两个连在一起的结论没有被直接包含；这是一项有明确数学内容的模型专属组合结果，不是从检索未命中推导“首次”。

“未知工作量”“状态相关恢复费”“完整周期记账”“当前速度/非零初态”“全局随机DP”“临界节能速度”“连续ramp内执行”“最大Lipschitz桥”都有明确前史。它们各自作为独立创新均不通过。不能用把这些词排列到同一个标题中的方式取代定理比较。

本轮新增最有分量的近邻是Yuan–Qu 2005、Simunic等2001/2004、Irani等2003和Rao–Vrudhula 2005。它们进一步降低了宽叙事的可信度，但没有在已读定理中消去恢复投影与尖锐凸性分类的特定耦合。

本报告只判断创新定位。第三轮证明、反例、数值证书的正确性应由理论审查关负责；这里没有运行新优化或实验，也没有把浮点成本界升级为向外舍入证书。

## 模型与比较口径

比较对象为第三轮FULL_CYCLE_THEOREMS.md第1–8节及第10节：W∈[0,M]未知但分布已知；实际功率p≥0，|ṗ|≤R；未结束时ẋ=s(p)，s递增凹；EOS瞬时；EOS以后按−R回零，真实耗散和全过程时间均收费。目标是E[E_dynamic]+cE[T_cycle]，c>0。没有并发、到达、热状态、储能或额外阶段信息。回零以前不启动下一任务。

定义A(p)=∫₀ᵖs(q)dq、z=A(p)、P=A⁻¹、G(z)=(P(z)+c)/s(P(z))、H(z)=(P(z)²/2+cP(z))/R。关键特殊恒等关系为H′=G/R，进而

J[z]=H(z₀)+∫₀ᴹS(x)G(z(x))(1+z′(x)/R)dx。

这不是固定日历窗口的能量账本，也不是renewal-reward平均功率比值。完全复位的串行解释不自动把加权每任务成本变成长期平均功率最优。

## 主张与最接近原文的矩阵

P编号对应后面的原始文献定位；CSV/JSON中另有可排序版本。

| 主张 | 已包含的部分 | 未被直接包含的准确差异 | 增量评价与关口 |
|---|---|---|---|
| C01 工作坐标、survival期望、primitive换元 | P01–P03的工作坐标和尾分布；P07的路径参数化 | z′=ṗ由本模型的A定义给出 | 成熟表示加一行chain rule；独立创新FAIL |
| C02 完整回零周期与随机终态费 | P06、P12–P14已有active/idle、renewal、随机终止返回费 | 同一p在ramp中生产工作，EOS后按同一物理律耗散，故H′=G/R | 记账思想已知；恒等式是支持引理；独立创新FAIL |
| C03 无损恢复投影min{z,R(M−x)} | P08/P09已有端点cone几何；P12–P14已有返回成本 | 原问题未强制z(M)=0，仍可用完整周期支配证明无损加入；适用于所有EOS实现及任意work law | 与C06联合作主结果；CONDITIONAL |
| C04 临界功率cap | P11已有能量/工作临界速度；P09有受限ramp结构 | min投影需同时保持真实slew与EOS终态成本 | 简短模型引理；独立创新FAIL |
| C05 非零高初态最快下降前缀 | P05当前速度状态；P09任意起终速度 | 下cone z≥z₀−Rx与critical cap强制一致至接合点 | C04的直接边界扩展；独立创新FAIL |
| C06 幂律κβ=(1+2β)/(1+β)与sharp hazard界 | P02/P03已有随机work凸优化；P14已有hazard成本权衡；一般Hessian判据为标准工具 | 先无损缩域，再控制负终态曲率；α>κβ的可行终端bump给泛函中点反例 | 本稿最有辨认度的模型专属分类；CONDITIONAL |
| C07 一般凹s及内部原子反例 | 一般“非凸”并非新概念 | 反例在两个真实可行包络内部，说明C06不能扩张 | 主定理必要边界；支持项PASS |
| C08 原子EOS精确最大桥与K | P08直接给最大Lipschitz延拓；P05已有条件EOS链 | G递减使每个无EOS区间恰由最大桥代表；H′=G/R给闭式K | 几何与积分是直接推论；精确降维有用但不宜独立包装为新方法 |
| C09 Bellman上下界 | P04/P05/P13已有DP、近似和全局优化 | 本模型的连续endpoint转移核与box乐观松弛 | 实例化与复现价值；没有新DP/FPTAS结论；独立算法创新FAIL |
| C10 已知W时ramp–hold–ramp | P09的精确确定性结构；P10加速受限调度 | 实际功率slew、全周期权重不同 | 形状不新；只作推论/基线 |
| C11 新的物理时间逐点功率支配及正系统兼容 | order-preserving映射、卷积范数界是标准性质 | 若C03加强为完整波形p_C,w(t)≤p_z,w(t)，可传递到同初态的单调上限约束 | 新加强需独审；映射结论是直接推论，不独立称电网稳定定理 |

## 为什么最近定理不能直接给出核心结论

### 随机速度调度并不直接推出恢复域

PACE及Anselmi模型的基本期望是∫S(x)Q(v(x))dx；没有EOS功率相关H。把恢复项“加进去”后，原凸性结论不能直接引用，因为H在临界域内可能凹。W6先证明添加回零cone不损失原问题最优值，才把可行域里的负曲率约束住。这一步不是把旧凸优化器换一个名字。

进一步核对P03的Assumption 1：在不含c的幂律反函数映射下，Q(v)∝v^(1/β−1)，0<β<1时只有β≤1/2满足其Q凸条件。若把c一起放入每工作成本，则增加c/v，而且W6保留的critical以下G恰为递减；不能只看总功率P(v)凸就宣称满足P03的Q凸且增假设。

不过，survival表示、integration by parts、cost-to-go/potential抵消本身都属标准分析。恰当的贡献单位是一条完整的无损域归约，而不是每个推导等式分别列为创新。

### 连续productive ramp有前史 但斜率变量不能偷换

P09正式写出|v̇|≤K、∫vdt=W和给定起终v；这已经否定“以往连续转换期间不执行”及“以往只能从零启动”的宽说法。

对W6取v=s(p)，则|v̇|≤R s′(p)。若s=kp^β且0<β<1，右侧依v而变。直接套P09的常数速度slew定理不保留可行集；把其速度改名为p又会把工作积分误改成∫pdt。再者，P09已知W、固定时间和指定终态，不能独立给随机EOS情况下无损选择终态及law-dependent凸性边界。

P07的标准变量为b=v²、a=v̇，b′=2a。W6约束变成|a|≤R s′(s⁻¹(√b))。幂律0<β<1时右侧是b的负幂凸函数，允许集一般不是P07要求的凸集。因此其标准变换并不直接覆盖W6。β=1是特殊线性边界，不应据一般非包含论证将其排除。

### 转换成本DP是严格方法前史

P05明确包含当前速度、work-bin、条件survival和随机EOS转入下一任务。W6若只增加真实p状态写一个Bellman方程，是普通随机控制实例。其可保留的贡献是先消除无EOS区间的无限维控制，再给本模型的精确转移核及可核验上下界；仍不得宣称发明Bellman原则或全局随机调度。

P05的PT/PE是转换的附加penalty，bin内恒速，最后任务后的值初始化为零。它不能直接把ramp内有效服务、EOS相关返回费和H′=G/R自动带入。把这些替换进去是重新建立模型，不是原定理的无条件实例。

### 阈值为何比单纯Hessian计算多一步 又为何不算通用新凸化方法

在恢复和critical域上，F″=S[G″+(h/R)G′]，其中G′≤0。充分条件归结为h z/R≤zG″/(−G′)。包络z≤R(M−x)和幂律下右侧的最小极限共同给κβ。

独特内容在于：这个包络是无损获得的，κβ对整个约化profile类是尖锐的，且α>κβ时存在同时保持positivity、两cap及slew的变分反例。Hessian与bump证明技巧本身平常。它更像一篇紧凑的结构分类论文，不足以凭现有证据宣称广泛的新优化原理或高创新系统方案。

P14两态终止问题的式(1)微分得到J′(τ)=S(τ)[a−b h(τ)]（这是本次独立比较计算，不是原文命名定理），故hazard参与运行/恢复权衡也不是新思想；W6需强调的是全路径泛函的凸性阈值。

### 原子和非零初态应降为紧邻推论

最大桥是P08在两个端点上的直接代入，截断到常数cap仍Lipschitz。G递减与H′=G/R分别完成“选最大桥”和“积分得K”，之后套Bellman。该链条有模型化与算法实现价值，但每一步都很短。非零高初态前缀同理，属于critical投影遇到Lipschitz下边界的确定性后果。二者可以增强完整性，不宜各列为同等强度的主创新。

## 原始文献定位与确实读取的内容

以下均为作者、机构、会议或期刊提供的原始全文。读取的是模型、定理及相关证明位置；没有声称逐字通读每篇实验。P11、P13、P16的阅读由同任务专项复核完成，详情见regenerative_priors.md。

- P01 Lorch–Smith，PACE，SIGMETRICS 2001。[原文](https://www.microsoft.com/en-us/research/wp-content/uploads/2004/07/pace.pdf)，§3–4.2，PDF第2–4页。明确pre-deadline工作与post-deadline安排共同保持effective completion time；不能改写为任意有界W的hard deadline模型
- P02 Anselmi–Gaujal，MASCOTS 2022。[作者稿](https://polaris.imag.fr/jonatha.anselmi/single-task-energy-opt.pdf)，§II.C–D，式(3)–(10)，Propositions 1–2。凸的是有序work切换点问题；F连续对应可微，F严格递增对应严格凸
- P03 Anselmi–Gaujal，2025-09-26作者稿，对应ORL 64 (2026) 107379。[作者稿](https://polaris.imag.fr/jonatha.anselmi/Energy-WC.pdf)，§2.3–2.4，Assumption 1，式(1)–(6)，Theorem 1。明确忽略ramp及转换费用；Q=P(v)/v凸且增，不能把P凸与Q凸混同。未假定作者稿与出版终稿逐字一致
- P04 Xu–Xi–Melhem–Mossé，Practical PACE，EMSOFT 2004。[会议全文](https://websrv.cecs.uci.edu/~papers/emsoft0405/docs04/p54.pdf)，§5.4，Figure 4，Theorem 2，印刷59–60页。转换penalty扩展和FPTAS已有；比较实验把overhead设零
- P05 Xu–Melhem–Mossé，EMSOFT 2007。[会议全文](https://www.cecs.uci.edu/~papers/esweek07/emsoft/p37.pdf)，§3.1式(1)(2)，§5.1.3 Lemma 1，§5.2–5.3，Figures 6–7，印刷39、42–43页。当前速度与条件EOS状态可直接核对
- P06 Bini–Scordino，IJES 4(2):101–111，2009。[机构终稿](https://iris.unito.it/retrieve/e27ce42a-d6e3-2581-e053-d805fe0acbaa/officialPaper.pdf)，§2.1印刷103页及§3.1式(6)–(10)印刷105页，本次在dot云浏览器直接读。目的mode独立entry cost、固定T内idle记账与W6不同；§3.2的细部继承第三轮阅读
- P07 Lipp–Boyd，2014。[作者PDF](https://web.stanford.edu/~boyd/papers/pdf/speed_opt.pdf)，§3.2式(2)，§5式(24)–(26)，§6.1.1式(27)–(29)。原文要求变换后控制集凸；不可忽略这一假设
- P08 Petrakis，LMCS 16(1:18)，2020。[期刊全文](https://lmcs.episciences.org/6105/pdf)，Definition 2.1，Theorem 2.3(iii)，正文18:9–18:10页。端点cone的最大延拓结论直接包含桥的几何公式；1934原版没有在本次重新取得
- P09 Yuan–Qu，TCAD 24(12):1827–1837，2005。[UMD原稿](https://api.drum.lib.umd.edu/server/api/core/bitstreams/cd02311f-10c6-4c6d-ab4e-3866dd4d51ab/content)，[机构记录](https://drum.lib.umd.edu/items/ffc9f70d-f735-49dc-9522-03b4a7aa721d)。§IV式(3)–(7)、§IV.B Lemma IV.1/Theorem IV.3，附录证明，稿件4–5、9–10页
- P10 Wu–Li–Chen，TCS 412:1122–1139，2011。[作者机构全文](https://www.cs.cityu.edu.hk/~minmli/files/TCS10Accelerate.pdf)，§2及Theorems 1–2、4。其pessimistic模型在转换期间不执行工作，且定义能量只在恒速执行部分计费；不能当W6的同成本基线
- P11 Rao–Vrudhula，DAC 2005，901–904页。[会议全文](https://websrv.cecs.uci.edu/~papers/dac05/papers/2005/dac05/pdffiles/p901.pdf)，§3、Corollary 2及Theorem 1。短论文省略证明；2006扩展终稿本次只核到机构metadata，未读取其证明
- P12 Simunic–Boyd–Glynn，TVLSI 12(1):96–107，2004。[作者终稿](https://web.stanford.edu/~glynn/papers/2004/SimunicBoydG04.pdf)，§V，Figs.4–5，式(7)–(14)，§VI式(15)。完整renewal的时间/能量及LP目标已直接核对
- P13 Simunic–Benini–Glynn–De Micheli，TCAD 20(7):840–857，2001。[作者终稿](https://web.stanford.edu/~glynn/papers/2001/SimunicBeniniGMicheli01.pdf)，§IV.A、§V.A Theorem V.1及式(12)–(20)、§V.B。semi-Markov与非memoryless elapsed time状态是明确方法前史
- P14 Irani–Shukla–Gupta，TECS 2(3):325–346，2003。[作者实验室全文](https://mesl.ucsd.edu/pubs/irani_tecs03.pdf)，§3、§5.1式(1)–(4)、Theorem 2与附录。随机idle终止的running+return cost不是W6新发明
- P15 Chan等，Nonclairvoyant Speed Scaling for Flow and Energy，Algorithmica对应最终作者稿。[作者PDF](https://www.eecs.yorku.ca/~jeff/research/schedule/energy.pdf)，§1.2、§2、Lemma 6/Theorem 7。未知size、flow+energy和竞争分析已知；其信息/目标不同，不宜与已知law的期望全周期最优互换
- P16 Stanford EE364a，[官方课程PDF](https://see.stanford.edu/materials/lsocoee364a/final.pdf)，Problem 5第7页。确定性、离散日历速度slew的凸调度只是教学诊断；PDF日期未确认，不作定年研究优先权证据

## 最小可独立成文范围

建议题目范围为“未知工作量任务完整恢复周期的无损状态投影与凸性边界”。正文只设两个相连的主结果：

1. 返回reserve与无损恢复域，包含逐路径能量/周期时间支配，非零初态分支作为其边界
2. 幂律服务的sharp tail-hazard凸性分类，紧接一般凹服务与内部原子失败例

原子EOS最大桥、Bellman界和确定性目标政策放入求解/推论部分，明确引用前史。简单政策、Azure经验law与第三轮强基线用于说明结构有后果，而非“战胜已有最优随机DP”。新物理时间支配若独审通过，可给一个短兼容性命题：它保持同初态、order-preserving负荷映射下的all-time单调上限；正kernel和诱导范数cap是成熟工具，sign-changing swing不能据此继承安全。

**对充分性的判断：** 两项核心合在一起有可辨认的新定理候选，不是已读某一个定理的一行代入；但多数附加结果是直接推论，核心计算技术也基础。建议按紧凑理论论文/研究短文的强度推进，不能现阶段许诺高创新系统/控制论文。新模型并置本身不等于足够发表，需用无损量词与sharp边界的实际数学后果来说服审稿人。

## 通过条件与停止条件

- **本轮完成项 PASS：** 指定PACE、随机DVS/转换DP、路径参数化原文模型及关键定理比较；新增productive-ramp、renewal、随机返回成本、critical-speed前史；主张已分为直接包含、直接推论和未直接包含的窄差异
- **窄稿候选 CONDITIONAL：** 正式稿必须把C03+C06作为同一贡献链并列出精确量词；独审关闭端点/原子/非零初态/有限完成性；新增网侧兼容性不能扩大为任意频率安全。这里的conditional不是建议无限检索，而是建议带上述明确收缩继续证明与写稿
- **宽新颖性 FAIL：** 首次完整记账、首次未知结束/非零初态、首次连续productive ramp、首次全局DP、首次最大桥、通用新凸化方法
- **工程资格不由本关判定：** 真实GPU节能、PCC波动/频率改善仍需独立测量及网模合同；文献不包含不能代替实验
- **能改变本判定的最小反证：** 合法取得的先例明确具有productive连续actual-power slew、同一EOS后真实return账本，并给出无损z≤R(M−x)或等价域及上述sharp凸性分类；出现时应逐式更新，而非靠改标题保留优先权

## 访问未知与证据保存

本次未声称穷尽控制/运筹/可靠性/专利文献。Hong等RTSS1998在P09/P10中被追溯为连续slew前史；本次只核到官方作者履历记录，没有用未经读取的原始全文作包含/非包含判定。Rao2006扩展终稿未读；1934 McShane原版此前有client限制，本次没有重试或换路。它们均不能被写成“不包含”；已读P08/P09足以否定对应宽创新，核心结果仍保持有限定向核查口径。

Bini机构PDF的web文本接口返回Internal Error，正常公开PDF在dot云浏览器成功显示并读到103、105页；这是公开正文读取，不是登录/付费/安全限制绕过。无作者联系、购买、登录、验证码、外来代码执行或新实验。

14:16 UTC工作环境重置，先前本地第三轮输入和初版专项笔记一度消失。本文件从本轮已读取的原文、保留的工具结果和工作对话重新写成；没有假称消失文件仍存在，没有编造输入哈希。随后在14:20 UTC由本任务从已交付Library包恢复W6和G1，逐字节SHA256与既有值一致并安全解包。输入哈希针对恢复后W6文件计算；总审REVIEW_ZH.md仍仅保留重置前阅读记录，不编造哈希。正文与矩阵存在性见QA_RESULT.json。
