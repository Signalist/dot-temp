# G3 构造性标准基线与收束增量

2026-10-02 UTC。主入口 `G3_CONSTRUCTIVE_AND_CLOSURE_REPORT_ZH.md`；四轴结论与假设更新位于 `protocol/next_constructive/`。

## 已完成与有界结论

P0-fast、R0-fast、P50-fast、R50-fast四条冻结条件全部完成并通过独立全记录审计。标准P优先/径向加同一已有MPSC，均给出覆盖150ms跌落、清除与之后2s的有限完整数值物理见证。这是合成装置参考轨道的工程正结果，不是新算法优越、800/700联合服务全交付、实机认证或算力负荷特异性。

原恢复评分保持未通过。健康参照本身的末150ms也持续guard介入，因此该观测目标与“退出全部限制”的严格合同不适配；轨道贴回不等于通过该合同，也不等于电池库存再平衡。不得事后改评分，或将其写成任何控制都不能恢复。

建议本轮G3以paper_ready=false有界收束，不再追加策略/幅频/相位网格。少数尚未建立的后续科学命题在假设账本中列明证据门槛，不是自动待执行事项。

## 本包内容

- 自行编写的新标准分配wrapper/driver、与已封存driver的diff、静态测试
- 四条完整JSON/NPZ/逐100μs采样gzip；每条21,501样本，共86,004样本/优化计划；原始记录不删减
- 独立接口、全产物、事件、能量、Ω/保留节点管与恢复审计及各自manifest
- 恢复合同兼容性只读核查、三张已检查的结果图、代码轻量包更新建议
- 结果前四条件协议、旧时点假设账本及草案、结果后定稿矩阵/收束建议/机器更新JSON

协议中“待批准、执行数0”是创建时点的冻结文本；后来批准与实际执行分别记录于EXECUTION_SCOPE.json、结果/启动记录及定稿文件。旧六行账本快照保留，后四行另写更新，没有回填历史证据。当前四条没有hard/near标志，未重复5μs长轨迹。

## 增量依赖

本包不是独立全量包。按共同G3相对路径与以下旧包合并；新文件和精确前序依赖hash分列在INCREMENT_CONSTRUCTIVE_MANIFEST.json。

1. G3_GateA_with_extension_20261002.zip；SHA256 0d23d57e94eb17407570be7c7a336a703240e68232195af62e40e610c3c53ab5
2. G3_PORT_CURRENT_INCREMENT_20261002.zip；SHA256 8b783534e189f75952ec98d73f74925e304ce31924f147a38b17233e5c631a02
3. G3_DYNAMIC_CURRENT_GUARD_PROPOSAL_20261002.zip；SHA256 80fe75515f5cadbc2bb37f4f6b163afa72e7b09bd6329000765ca9c937f00712
4. G3_GATE0_MPSC_INCREMENT_20261002.zip；SHA256 549d872d2dd6f64ab05bdddedb73abd2130eb4ae25f7520a20f08cdd4c072d2f
5. G3_GATE1_MPSC_SIX_MODELS_INCREMENT_20261002.zip；SHA256 06cbba5897d99651261866bbd82c8e8ad25e8aaa560f05615086e7eed181ac5b

共同guard直接复用旧Gate1源码，未复制一个改动版隐藏于新目录。旧source/parameter/checkpoint/协议/归档均未修改。无论文或厂商PDF原件、第三方源码副本、wheel、venv或用户设备文件。

## 复核及轻量更新

合并后运行 `python current_guard_constructive/verify_package.py` 检查新文件与前序依赖；独立audit_*入口仅重算已有记录，不调用新物理积分/优化。重跑模型需单独副本，runner拒绝覆盖任何已有证据。环境为Python3.12.14、NumPy2.3.5、SciPy1.17.0，OPENBLAS/OMP均单线程。

另提供CODE_LIGHT_ADDITIONS增量，剔除4份NPZ与4份jsonl.gz，但保留代码、审计、摘要、图表和明确的原始数据索引。建议将其并入既有“代码与审计报告”资料库文件并保持同一身份/版本保护；已有三份四条件协议字节未变，只保留一份，不向ZIP写重复同名成员。轻量包本身不能替代完整原始证据。
