# G3 共用MPSC层六模型门增量

2026-10-02 UTC。入口：`GATE1_MPSC_MODEL_REPORT_ZH.md`。本包封存六个主模型条件、四个同条件5μs数值细化、全部原始轨迹/采样日志、代码和独立审计，不包含下一阶段P优先/径向提案或未执行结果。

## 结论

两条无故障有限窗取得数值物理准入，但均值服务约705.5kW/644.8kvar，未保持800/700请求。四故障均在DC上界停止前保持I<1pu，清除/恢复未观察。准确表述为“在已观察且DC域有效的前缀内未再出现旧过流”。不能将Q优先+该guard的失败推广到所有分配，也不能将有界观察升级为完整150ms故障安全。

`current_guard_qualified=false`、`paper_ready=false`。无联合DC/SoC不变集、严格外向舍入、开关硬件或100μs实时部署证据。固定冷启动SLSQP用时只代表本实现。

## 内容与来源

- `current_guard_gate1/results/`：六个主条件各JSON/NPZ/逐100μs完整jsonl.gz及启动记录；四个DC触边条件另存h5e-06，未覆盖10μs
- `common_guard.py`、`guarded_controller.py`、`run_models.py`：自行实现的已知tube-MPSC共用层、原Q优先采样适配与物理测试驱动
- `INDEPENDENT_INTERFACE_AUDIT.md`、`RUNNER_REVIEW.md`及audit_*：接口与十条产物独立只读复核
- `REFINEMENT_COMPARISON.json`与三张图：数值边界细化和实际响应；图在绘制后已逐张检查
- `IMPLEMENTATION_V1.json`保留中途记录时间及当时文档hash，最终交付文件hash以本包manifest为准；十次执行的guard/wrapper/runner代码hash完全相同

这是2026-10-02新获批并执行的模型诊断；初态/物理参数依赖既有重建后重跑的Gate A资料。未把历史摘要充作新原始轨迹。每步wall-clock字段和gzip元数据不要求重跑逐字节一致，物理/控制状态和指标可独立复核。

## 依赖与合并

本包是增量，不是独立全量包。按共同G3相对路径合并下列既有包与本包，不覆盖既有路径。manifest将新文件与前序依赖hash分列：

- 完整v2 `G3_GateA_with_extension_20261002.zip`，SHA256 `0d23d57e94eb17407570be7c7a336a703240e68232195af62e40e610c3c53ab5`
- 端口/静态电流审计增量 `G3_PORT_CURRENT_INCREMENT_20261002.zip`，SHA256 `8b783534e189f75952ec98d73f74925e304ce31924f147a38b17233e5c631a02`
- guard文献提案 `G3_DYNAMIC_CURRENT_GUARD_PROPOSAL_20261002.zip`，SHA256 `80fe75515f5cadbc2bb37f4f6b163afa72e7b09bd6329000765ca9c937f00712`
- 门0增量 `G3_GATE0_MPSC_INCREMENT_20261002.zip`，SHA256 `549d872d2dd6f64ab05bdddedb73abd2130eb4ae25f7520a20f08cdd4c072d2f`

不并入第三方代码、论文/厂家PDF原件、wheel、venv或用户设备资料。既有方法/公开来源链接保留于文献提案依赖中。

## 复核

从合并后的G3目录执行 `python current_guard_gate1/verify_gate1_package.py` 检查新文件及依赖hash。`audit_runner_checks.py`只读既有轨迹，不调用物理积分/新求解；其已保存结果覆盖六主+四细化。数值环境为Python3.12.14、NumPy2.3.5、SciPy1.17.0，运行时OPENBLAS/OMP线程均为1。

重算物理条件应在另建副本中进行；runner拒绝覆盖任何已有启动记录/结果。不要删除失败记录后把重试写成首次运行。健康长窗未重复5μs；四个短DC触边点按同一规则统一细化。
