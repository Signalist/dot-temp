# G4 可辨识性研究：核心证据包

先打开 `index.html`：离线可读，适合手机。完整中文研究报告位于 `outputs/round2_g4_identifiability_20261003/report/G4_RESEARCH_REPORT_ZH.md`。

## 一句话结论

这是一组数学证明和合成模型证据。较强候选是：在声明的有损缓冲、独立任务排列、输出范围及恢复约束下，无限时域通用隐藏需要 B ≥ 2Q + W∞，最低 2Q 可达到。它不是一般来源识别时限；高原创性和优先权尚未确立。

同一完整 PCC 轨迹下仍可保留不同任务历史。匹配站点、时刻、误差和延迟的 1 bit SOC 查询，可改变声明模型内的安全服务决策；拥有相同信息的常规稳健可行性基线也能作出相同决策。没有证明现实硬件成本优势、AI 标签推断或新定位器性能优势。

## 包内包含什么

- 冻结的本轮 G4 科学集合 114 个文件全部保留：理论、声明协议、代码、原始结果数组、精确有理数证书、独立审计、保留失败、研究报告和图
- 原始科学集合清单 1 个，保留其原文件哈希用于溯源
- 此次 G4 电网迁移重跑所需的 11 个较早输入全部附带，约 159 KB；另附上游许可证
- 22 篇原始来源的 URL、具体阅读深度和重合性审计；不转载论文全文
- 发布副本的原始→公开 SHA-256 对照、遗漏原因、移植验证记录和逐次日志

本包不包含另行交付的 Word/PDF 研究正文；图件的 PDF 版本是本轮冻结证据的一部分，予以保留。

## 推荐阅读顺序

1. `outputs/round2_g4_identifiability_20261003/FINAL_SCIENTIFIC_STATUS.json`：结论与未建立事项
2. `outputs/round2_g4_identifiability_20261003/report/G4_RESEARCH_REPORT_ZH.md`：完整研究报告
3. `outputs/round2_g4_identifiability_20261003/report/HYPOTHESIS_ASSUMPTION_LEDGER.md`：假设、边界与主张账本
4. `outputs/round2_g4_identifiability_20261003/theory/LOSS_TOLERANCE_TASK_ORDER_THEOREMS.md`：主体定理
5. `outputs/round2_g4_identifiability_20261003/theory/SERVICE_DECISION_CERTIFICATE_ADDENDUM.md`：服务决策证书
6. `outputs/round2_g4_identifiability_20261003/literature/CONTINUOUS_TOLERANCE_DAG_ADDENDUM.md`：扩展新颖性审计

## 可重跑范围：两层必须区分

### A. 核心数学、SOC 与服务证明

代码、参数、结果与见证全部在本包内。无需更早实验目录、ANDES 或网络数据下载；仍需本机有 Python 和 NumPy/SciPy/SymPy。图件重绘另需 Matplotlib。

### B. 本轮 G4 电网迁移分析

它依赖更早生成的 11 个锁定输入，本包已将这 11 个文件按原相对目录 `outputs/round2_20261003/grid_transfer/` 一并提供。清单与 SHA-256 见 `EXTERNAL_GRID_INPUTS.json`，当前迁移分析可离线重跑，不需安装 ANDES。

本包不承诺从零重建较早的完整 ANDES 资格验证、原始基准工作簿或所有历史实验。附带的早期资格说明可能引用本包外的历史实验；这些引用只是来源背景，不表示所引全部文件随包提供。原始模型版本、上游地址和文件哈希见该目录的 `PROVENANCE_LOCK.json`。

### 最短操作

解压后保持 `outputs/` 下的相对目录不变，在包根目录执行：

```bash
python reproduce.py --verify-only
python reproduce.py
```

第一条核对公开文件哈希。第二条将证据复制到新建的 `rerun_workspace/`，执行 17 项核心生产/审计命令，不覆盖原证据。

若同时重跑本轮电网迁移和三张图：

```bash
python reproduce.py --include-grid --figures
```

完整模式执行 21 项命令。输出目录已存在时程序会停止；可用 `--destination rerun_workspace_2` 选择新目录。`requirements.txt` 列出此次核验的版本，未捆绑 Python 环境或依赖安装包。

原始 `README.md` 保留逐条命令，供手动复核。手动执行原始脚本会在其所在副本写入结果，因此也应先复制一份后运行。

## 此次移植验证结果

在单独临时副本中，15 项生产脚本、4 项独立审计、2 项图件生成，共 21/21 项退出码为 0。本轮所有 JSON/NPZ 输出与冻结副本字节相同，唯一差异为电网 `results.json` 的生成时间；排除该时间元数据后数值一致（比较容差 rtol=1e-10，atol=1e-12）。114 个冻结科学原件无修改；11 个电网依赖的原件、公开副本、重跑后副本全部匹配锁定哈希。

详情见 `PORTABLE_VERIFICATION.json`。这是交付移植核验，不是新增科学结果。独立审计是同一研究包内的独立实现检查，不是外部同行评审。绘图执行通过；不同机器的字体、PDF 元数据和浮点库可能造成字节差异。

## 原件、公开副本与遗漏

`PUBLIC_PACKAGE_MANIFEST.json` 对每个科学来源文件记录原相对路径、原始 SHA-256、公开路径、公开 SHA-256 和具体转换。114 个科学文件中仅有 3 个发布副本发生非科学变更：README 的入口/范围说明，以及两段绘图脚本的临时缓存路径可移植化。未修改数值、数组、算法、实验协议或结论。

原始嵌套清单记录的是冻结原件哈希，可能与这 3 个公开副本的哈希不同；请用包根目录的公开清单和 `SHA256SUMS.txt` 校验本包。哈希不能循环自校验：公开清单本身的哈希在 SHA256SUMS.txt，SHA256SUMS.txt 及整个 ZIP 的完整性由包外 ZIP 的 SHA-256 保证。

57 个科学历史/来源文件仅作哈希索引：21 份论文 PDF/文本副本，以及 36 个早期 G4 历史归档/展开文件。原因和原始哈希见 `SCIENTIFIC_OMISSIONS.json`。这不是删去本轮失败；本轮失败 ODE 代码和失败输出仍完整保留在 `validation/retained_failures/`。

私有协作、传输凭据/签名地址、交付工具和环境缓存不在包内。已有科学文件未变更的原始统计口径见 `validation/SCIENTIFIC_INPUT_INTEGRITY.json`：该记录是大小与时间戳核对，不应表述为对全部旧文件做了内容哈希核验；此次另对 114 个本轮冻结文件及 11 个输入作了内容哈希核验。

## 文献与使用边界

22 项来源保留原 URL、作者、标题、年份、实际查看程度和重合性说明。部分来源只检查了摘要、书目记录或索引片段；没有把这些项目宣称为全部已下载全文。原审计未找到完全相同的组合前例，但未完成穷尽检索或确立优先权。

论文全文不随包再分发；请通过原 URL 按原站许可获取。电网输入附 `ANDES_LICENSE_GPL3.txt` 和来源说明。没有随包分发整个运行环境。

这些结果不是实测 AI–PCC–PMU 联合数据，不是电网运行保护保证，也不是完整开关/电流圆约束下的 PCS 硬件验证。服务证书采用声明的标量一阶执行器模型和未经传感器实测标定的研究误差界。
