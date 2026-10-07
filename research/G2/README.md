# G2 正等能共享工作时钟的表示阶与核相消边界

**处置：窄数学分类后备；不是 paper-ready，不能升级为实网工程复杂度结论。** 科学结论以 2026-10-04 第三轮研究档案和六行目录为准；本交接的代码复核日期为 2026-10-07。本目录应放在目标分支的 `research/G2/`。

## 精确研究问题

在正工作能耗函数、共享工作时钟和固定端点工作/速度/加速度下，端口功率满足 `p_j(t)=e_j(theta(t))*theta_dot(t)`。单位工作能耗被假定不随速度改变。时钟完成后继续名义输入，电气状态不能重置。问题是：把 jerk 限为至多 m 次跳变的分段常数后，完整未来绝对峰值最优值损失是什么阶？工作函数正则性、核相消和真实网络核如何改变这个结论？m 是表示预算，不是任意算法运行时间。

固定主定理合同为 T=1、theta(0)=0、theta(1)=1、v(0)=v(1)=1、a(0)=a(1)=0、|j|<=1/4、|a|<=1、0.9<=v<=1.1；后续theta=t。整个jerk可行类的速度/加速度界都非活跃。匹配下界使用 h1(s)=s^3 exp(-s)、h2=-h1 和零共同电气初态；工作族的Fourier次数N+2随预算增长。

## 最新可保留结论

- 有限 jerk 要采用连续分段线性加速度，不能沿用有跳变的加速度弧。固定非活跃速度/加速度约束下，合成四阶滤波核与无统一带宽上限的正等能工作族给出最坏 `Theta(m^-3)`
- 加统一工作函数斜率界，仍允许带宽增长时得到 `Theta(m^-4)`。固定有限 Fourier 截止 K 的完整非线性尖锐阶仍开放
- 有限 jerk、同号衰减核类的服务完成后峰值，只需比较两条通用候选时钟；不适用于服务中的全峰值，也未证明实际电网属于该容易类
- Goodman–Lee perfect-spline/Hermite 与 Scarinci–Veliov 矩恢复已覆盖核心压缩工具。相同信息自由结点 L1 支撑基线达到相应连续线性化目标，不能主张优于成熟求解器
- m=100 的保守证书差仅约 `1.34e-28` 归一化输出单位；充分渐近阈值 `N0=1,734,133`。测试 `N<=128` 不是进入该正下界区间的证据

## 必须保留的负面结果与证据等级

Kundur 51 状态矩阵的八个原始频率核均有非零 `CB`，约 `2.63e-5` 至 `1.79e-3`；新下界所需零初导数条件不成立。在固定采样网格上各导数观察到 62–64 次变号，简单同号核充分条件也不成立。结果既没有把 Kundur 证明成困难类，也没有把它证明成两候选容易类。

相消实例 N=8/32 中统一非线性 Taylor 余项超过线性化优化增益。固定网格与自由结点的差异不等于一般算法下界；独立端口时钟、去掉端点矩分别改变信息和工作合同。核失配、观测滤波、固定绝对误差下非消失工程量级、活跃 jerk 约束及实际 DVFS/PCC 校准均未闭合。数值恒等式检查不是向外舍入证明或硬件验证。

## 直接阅读与执行入口

- 论述及 claim ledger：`evidence/snapshot/outputs/round3_g2_20261004/report/`
- 精确定理、量词和常数：同目录下 `theory_worker/FINITE_JERK_AND_BANDWIDTH_THEOREMS.md`、`COHERENT_KERNEL_EXACT_BOUNDARY.md`
- 独立怀疑性审查与失败修正：`audit/SKEPTICAL_THEORY_AUDIT.md`、`protocol/DEVIATIONS_AND_POSTHOC.md`、`audit/matched_support_qa_attempt1.log`
- 强基线及真实核否定筛选：`experiments/` 中完整脚本和 JSON/NPZ
- 下一轮实验与停机标准：`NEXT_STEPS.md`；接手提示：`AGENT_START.md`
- 环境和完整命令：`REPRODUCE.md`；版权边界、下载和校验：`provenance/README.md`

从仓库根运行：

```sh
cd research/G2
python verify.py
OPENBLAS_NUM_THREADS=1 python replay.py --mode full --work-dir ../../g2_replay_work
```

复放会复制科学证据到新的工作目录；拒绝覆盖已存在目录。参考环境 Python 3.12.14、NumPy 2.3.5、SciPy 1.17.0、SymPy 1.14.0、mpmath 1.3.0。本次已新执行全部八阶段并比较归档结果；细节见 `validation/HANDOFF_QA.json`。这不是新安装依赖测试、上游矩阵独立再生或第二轮完整仿真。

`MANIFEST.json` 是本交接唯一当前完整性清单。历史报告中的 hash/验证成功仅属于原科学快照，不能用于认证删减后的全部历史工作区。四个第二轮数学参考保留，原 896 文件历史检查没有重新执行。未分配新的代码许可证；上游 ANDES 通告单独保留。
