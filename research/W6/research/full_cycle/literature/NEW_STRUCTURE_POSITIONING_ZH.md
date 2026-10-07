# 新全周期结果的文献定位补充

更新：2026-10-04 05:56 UTC。本文件对照本轮`../theory/FULL_CYCLE_THEOREMS.md`，不重复证明，也不把未检索到先例写成首创。

## 1. 新结果应当如何与最近前史拉开距离

**优先候选是全周期双重支配与尾hazard凸性边界。** 既有PACE/Anselmi survival-cost模型没有恢复终端项，不能直接给出

`H′=G/R，J=H(z0)+∫SG(1+z′/R)`

所支持的无损recovery cone。原理层面，添加/消去exact differential和integration by parts是标准分析；真正需要论证并对照的是它如何使本模型的max-descent路径成本中性，从而允许无损限制`z≤R(M−x)`，再与critical cap一起恢复全局凸性。L06/L07的固定frame/离散mode转换费用并不具有同一恒等关系。

对幂服务，`κβ=(1+2β)/(1+β)`和`h(x)(M−x)≤κβ`的具体sharp convexity条件，在本轮核查来源中未找到精确先例。应清楚说明：这不是首次使用hazard；`h(M−x)`是相对于同支撑uniform hazard的无量纲比。理论文稿的尾部可行bump构造证明的是此统一阈值对约化profile类的sharpness；条件失败并不意味着每个具体分布都不可全局求解。

一般凹s下不应推广幂函数结论。文稿给的service-dependent κ可能小于1甚至趋零；uniform EOS对一般凹s不自动凸。原子EOS也需要另一个精确全局路径。

## 2. 最大桥公式有非常直接的标准前史

L09：Iosif Petrakis, *McShane-Whitney extensions in constructive analysis*, Logical Methods in Computer Science 16(1:18), 2020，[期刊页](https://lmcs.episciences.org/6105)，[原论文](https://lmcs.episciences.org/6105/pdf)。本轮直接读Definition 2.1、Theorem 2.3：给定集合A上的R-Lipschitz值g，

`g_upper(x)=inf_{a∈A}[g(a)+R d(x,a)]`

是最大同常数Lipschitz延拓，每个可行延拓f满足`f≤g_upper`。取A为两个区间端点，就得到两条cone的min；与常数critical cap取min保持Lipschitz。此数学论文明确追溯1934年的McShane–Whitney原理。1934 AMS原PDF本轮受client访问限制，未绕过；因此不声称直接核对过1934原版。

**应引用和保留的区别**：最大bridge的几何公式不是W6原创；L09也没有随机work、能耗、恢复或Bellman。W6具体贡献候选是：证明每个无EOS区间的原问题恰被该最大bridge代表，解析得到K，并把随机终端费用留在节点，使无限维问题精确约化为连续endpoint-state chain。这个“对本模型成立的精确降维”比“我们用了DP”具体得多。

L06（2007）的current speed、条件survival和动态规划是另一必须引用的前史；其discrete-mode time/energy penalty与W6真实slew中仍服务的模型不同。连续endpoint chain及box-lower/feasible-upper应定位为本模型可核验求解途径。Bellman原则、网格可行上界和乐观松弛下界都是通用工具，不能另列宽泛发明。

## 3. 可用于摘要/引言的保守措辞

“对一类具有连续实际功率slew、未知工作量以及EOS后完整回零成本的单任务模型，我们利用全周期reserve恒等式证明两个无损状态约束。对幂服务，这些约束导出一个sharp的尾hazard凸性保证；对有限原子结束分布，无EOS区间可精确消元为最大Lipschitz桥，得到带全局上下界的连续状态链。”

以上需要随正式定理一并说明：已知外生F、无阶段反馈、实际可控p、ramp内服务、恢复burn存在；高初态分支、模型的期望/硬deadline区别；数值box bounds使用普通浮点不是directed-rounding interval certificate。

不要写“首次随机size凸化”“首次非零初态恢复”“首次全局随机DP”“首次进度换元”“首次最大桥”。本轮没有进行穷尽控制/运筹/专利审查，也没有第三方正式新颖性确认。
