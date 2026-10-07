# W6 实验设计文件索引

本目录是 2026年10月5日的规划交付，没有新运行科学实验或硬件任务。

- DESIGN_REPORT_ZH.md：路线选择、既有负结果、raw capture、最小 pilot、功效/统计、QoS、消融/迁移、证据门槛和打包说明
- EXPERIMENT_MATRIX_ZH.md：38 项实验逐项中文操作设计
- EXPERIMENT_MATRIX.json / EXPERIMENT_MATRIX.csv：同一矩阵，含 ID、优先级、tier、当前状态、依赖、输入、设计/预算、输出、指标、gate、失败转向、实现状态
- ROUTE_PLAN.json：5 条机器可读路线及依赖覆盖、条件扩展和最终终态汇总门槛
- CHECKPOINT_A_E_MAP.json：原 A–E 检查点保持原含义，与资源 tier 分开
- OUTPUT_PATH_MAP.json / .csv：127 个逻辑输出到 prompts 编号目录的规范路径映射
- IMPLEMENTATION_LEDGER.json：16 个组件，严格区分已有 CPU 测试、硬件未测、仅接口与缺实现
- SOURCE_LEDGER.json：17 个实际阅读的本地旧来源及 SHA256；不宣称本次科学复算
- COVERAGE_AUDIT.json：32 个方法学/工程覆盖维度与实验 ID，不是 empirical gate pass
- CSV_FORMAT.json：CSV 嵌套字段以单元内 JSON 编码，数组/对象须二次解析
- PLAN_QA.json：矩阵一致性、依赖无环、源文件存在性检查
- MANIFEST_SHA256.json：本目录交付文件完整性

重建顺序为 build_design.py → finalize_design_routes.py → build_audits.py，之后重新封存 MANIFEST_SHA256.json。三个脚本只生成/校验规划文件；不会执行采集、科学求解或 GPU。源路径以当前仓库根为基准；完整既有项目应从两个原交付 ZIP 合并后使用，不能把本目录当成已经实现的 GPU runner。
