# G4 有界收束和隐藏状态前置门

先读GATE_C_REPORT_ZH.md，再读G4_HYPOTHESIS_LEDGER_ZH.md。建议本轮G4收束为paper_ready=false；保留条件信息/测量价值，不声称整个真实问题不可行。

## 本门完成

9个容量/频率例、200周期连续守恒轨迹；只有3种归一化储能轨道。9/45预定窗口源类不同，最终窗口全同类；1bit能量阈值与1bit直接PCC阈值同样足够解除二元有限窗口歧义。周期收缩和能量差预算排除本控制族内持续非零初态分离。

11项测试和独立数学审查通过；数值贴边失败、未奏效的容差修复及最终相位分段修复全部记录。硬截断理想模型只作解析对照，主见证的能量和功率连续。

## 复现

进入G4/GateC目录：

1. python run_gate_c.py
2. python -m unittest -v test_gate_c.py
3. MPLCONFIGDIR=.cache/g4_mpl XDG_CACHE_HOME=.cache/g4_cache python analyze_gate_c.py

numpy/scipy/pandas/matplotlib来自现有环境。主脚本为独立可运行文件，无商业仿真器或外部数据依赖。

## 文件和完整轨迹

核心包包含报告、假设账本、文献/独立审查、代码、全部汇总/逐周期CSV、测试、图像与哈希。完整9条最终轨迹和1条原始数值问题审计轨迹分装到RAW分包；解压到同一位置即可。若仅取得核心包，也可运行脚本重生成全部最终轨迹。

每条最终NPZ保留全部160001个采样时刻，含time_s、energy_MWs、load_MW、charge_MW、discharge_MW、PCC_MW、PMU_Hz、PMU_swapped_Hz、energy_balance_residual_MWs。两列对应低/高初能量站；交换世界使用相应列交换，网侧另保存了独立求解结果。没有删减晚期数据或只提供最有利窗口。

RAW_TRACES_INDEX.json列出文件、单位、哈希及所属分包。archived_pre_domain_refinement是数值审计材料，不是额外科学样本。

G4 Gate A/B的既有包独立保留，本增量不重打包其全部大数据。所有门均未声称公共IEEE/未知频率/真实AI-PCC联合验证已经完成。
