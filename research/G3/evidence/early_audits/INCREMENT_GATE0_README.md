# G3 门0增量研究记录

日期：2026-10-02 UTC。此包只新增已完成的MPSC门0数学/实现审计与一次离线初态优化，另附尚未执行的六模型冻结清单。它不是独立全量G3包，也不是闭环guard通过报告。

## 先读

- `GATE0_MPSC_REPORT_ZH.md`：主要结论、结果分层及未闭合条件
- `GATE1_MPSC_SIX_MODELS_CHECKLIST_ZH.md`：下一步冻结条件、失败备份与保存方案，当前运行数0
- `current_guard_gate0/INDEPENDENT_MATH_REVIEW.md`：分时追加的独立审计；第八节记录当时尚未收到实现，第九、十节是后续最终实现/KKT审计
- `current_guard_gate0/GATE0_AUTHORITATIVE_STATUS.json`：机器可读主张边界
- `INCREMENT_GATE0_MANIFEST.json`：新增文件与既有依赖分别列出

## 依赖与合并

按共同G3相对路径依次放置完整v2、端口/静态限流增量、guard文献提案包及本包。当前包无同名覆盖项。准确依赖文件与SHA256见manifest，不需要重新复制整个历史轨迹。

1. 完整v2：`G3_GateA_with_extension_20261002.zip`，SHA256 `0d23d57e94eb17407570be7c7a336a703240e68232195af62e40e610c3c53ab5`
2. 端口/静态限流增量：`G3_PORT_CURRENT_INCREMENT_20261002.zip`，SHA256 `8b783534e189f75952ec98d73f74925e304ce31924f147a38b17233e5c631a02`
3. guard文献提案：`G3_DYNAMIC_CURRENT_GUARD_PROPOSAL_20261002.zip`，SHA256 `80fe75515f5cadbc2bb37f4f6b163afa72e7b09bd6329000765ca9c937f00712`

本包没有原始论文/厂家手册、第三方代码副本、wheel或venv。数学实现为自行编写；既有方法和公开来源链接在提案包中。源端口和参数适用性更正继续有效。

## 时间线与来源

- 既有物理轨迹是历史步骤从执行记录重建后重新运行的证据，来源标记未改动
- 门0冻结设计在本轮门0计算前保存；门0结果是新的离线计算，不是复用旧性能摘要，也没有新闭环轨迹
- 独立解析审计先行，02:29 UTC追加实现/计划审计，02:34 UTC追加KKT/终端尾部审计
- 02:43 UTC保存下一六模型冻结协议，状态仍为待闭环执行批准
- 本次仅重新绘图与打包，没有重跑初态优化或修改任何数值结果

## 复核方法

从合并后的G3目录运行 `python current_guard_gate0/verify_gate0_package.py`，检查本增量所有文件和依赖文件hash。该检查无外部网络、不会模拟物理轨迹。使用Python3.12.14、NumPy2.3.5、SciPy1.17.0的既有独立环境完成门0；重算需要这些运行依赖，绘图另用Matplotlib。依赖包不并入交付。

`diagnose_gate0.py`是门0结果生成脚本，只做两种合同各一次离线优化；`check_primal_witness.py`是只读原计划后验，`plot_gate0.py`绘制结果。重算会覆盖其本地输出且wall time会变化，若需复现请使用单独工作副本。`freeze_*`脚本保存冻结协议生成逻辑和当时字段，重新运行会更新时间戳，不能把新hash当成原冻结hash。

`current_guard_qualified=false`，`paper_ready=false`。本包图为解析外包与离线输入候选，不是模拟电流轨迹；理想实数证明、双精度结果、全装置认证三者严格区分。

后续时间边界：六模型执行范围于2026-10-02 02:53 UTC获批。冻结JSON及门0结果保留其原始待批准字段；本包没有随后闭环执行数据。后续结果应独立追加并保留本包hash，不能将此门0包称为六模型完成包。
