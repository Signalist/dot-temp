# G3 可复核研究证据包

此包是小型可再生证据核心，不是全部原始轨迹镜像。中文研究档案Word和PDF另附。

## 阅读顺序
1. LATEST_EVIDENCE_INDEX.json给出本次交付入口；FINAL_SCIENTIFIC_STATUS.json是保持不变的核心与V2阶段状态，新补同输入对照见recovery_phase3_workload_match/PHASE3_INDEX.json。
2. reports/G3_RESEARCH_REPORT_ZH.md 是核心理论长稿；theory/EXACT_PORT_CONTRACT_THEORY.md 是完整证明。
3. recovery_phase2/REPORT_V1A.md 保留14通过、4失败；V2/REPORT_V2.md及对应独立审计说明34/34通过的有限合同。
4. recovery_phase3_workload_match/REPORT_PHASE3.md及独立审计补充逐时相同算力输入L对照；34行均为已见配置的追溯检查，不新增盲测。
5. V2及补对照只验证100 kW削减、600 kvar服务主见证，未验证808 kvar容量边界。

## 合同边界
核心100 J是0–0.2 s平均模型指定晚段P上限的额外净余量，要求精确服务和终态。V2的100 J是0.2–0.7 s相对匹配健康PWM轨迹的恢复成本，分别检查带符号绝对值、正向和绝对电量，采用服务/状态容差，并继续观察至0.9 s。两者不等价。标准PI恢复没有原创算法主张；没有硬件/GPU因果验证。

## 内容完整性
保留688个科学源码、输入、协议、证明、结果汇总、审计与图文件。另有1027个原始数值轨迹文件，合计2,125,009,460字节，在OMITTED_RAW_TRACE_INDEX.csv逐项列出字节数和原始SHA256。全部源文件校验通过，原件未改。缓存、可再编译程序和执行日志不作为公开材料。

部分文本仅作执行位置或描述性溯源用语规范化；数学表达和数值结果未改。PUBLIC_FILE_MANIFEST.json同时保存原始与公开副本哈希。历史SCIENCE_MANIFEST及执行冻结中的哈希仍标识原始字节；公开副本完整性请用PUBLIC_FILE_MANIFEST，不应把文字规范化造成的哈希变化误称科学变化。

## 可移植复现
使用requirements.txt中的Python依赖；核心脚本的具体用法见原README.md。恢复V2在其目录执行：

    g++ -O3 -std=c++17 recovery.cpp -o recovery
    python run_campaign.py warmup
    python run_campaign.py nominal
    python run_campaign.py regression
    python run_campaign.py confirmation
    # 返回证据包根目录后，对重建轨迹使用原科学assess函数
    python PUBLIC_REPRODUCE.py summarize V2

先在证据包根目录运行python PUBLIC_REPRODUCE.py verify校验副本。恢复V1A在recovery_phase2目录使用warmup、nominal、holdout阶段，然后在根目录运行python PUBLIC_REPRODUCE.py summarize V1A。运行会重建CSV/NPZ轨迹，耗时与磁盘需求高于阅读本包。审计的历史原件哈希检查按原始冻结字节定义；公开副本先用PUBLIC_FILE_MANIFEST检查，重新运行时应在独立工作副本中保存新输出，不覆盖历史结果。

数值残差和微小终态差是模拟器诊断，不是物理测量精度。新确认配置、回归配置、双步长细化和配对健康支路在统计中严格区分。

公开复现包装器只复用原summarize.py中的数值assess函数，结果另存REPRODUCED_PUBLIC_SUMMARY，不覆盖冻结汇总。原summarize.py主入口还会读取省略的全历史原始文件做哈希检查，因此不能直接作为这个小包的入口；这里明确分离数值复算与历史归档哈希认证。没有跳过或伪造完整原始归档通过结论。

## 追加逐时相同算力输入对照

旧S−F对照的服务期逐时计算输入不同，尽管0–0.2 s计算总电能均为130 kJ。新L分支逐时采用与S完全相同的d(t)，按声明模型铜损补偿跟随负荷，Q=0、u前馈=0。S−L只表示相对于这个明确可行策略的增量，不是全球最优无服务机会成本。

原17配置×2步长的34条S−L追溯比较全部通过，不新增盲测数。名义细步长全过程S−L有符号增量约69.002737 J，正向电量14.248771 kJ、绝对电量28.428539 kJ；不能只报净量。恢复0.2–0.7 s最坏绝对电量为0.524038 J；100 J只限该恢复窗。

先完成上面的V2 warmup/nominal/regression/confirmation原始轨迹重建；phase3会读取这些S/F轨迹和已有检查点，并验证两个原S的重放。然后进入recovery_phase3_workload_match目录运行：

    g++ -O3 -std=c++17 rectifier_load_match.cpp -o rectifier_load_match
    python run_phase3.py

返回证据包根目录，运行：

    python PUBLIC_REPRODUCE.py summarize PHASE3

此入口复用原evaluate_phase3.py中的workload_definition()和assess()，另存重算结果。该原文件的main()还会检查1457份历史保全哈希；在省略原始轨迹的小包中不直接执行这个完整归档检查，也不伪造“旧归档全部相同”的结论。编译器和平台差异可能影响字节级结果，源证据中的逐位重放声明只指冻结环境中的检查。全部限制与612行独立账本见本阶段audit目录。
