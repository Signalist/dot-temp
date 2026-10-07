# G3 源速度/静态分配/独立abc 增量包

此包不是独立全量包。请先恢复已保存的 **G3完整v2**，再将本包按相对路径展开到相同G3根目录。所有本包文件均为新增文件，不替换v2原文件。

基础包：`G3_GateA_with_extension_20261002.zip`，211,699,716 bytes，SHA256 `0d23d57e94eb17407570be7c7a336a703240e68232195af62e40e610c3c53ab5`。

主入口：`G3_PORT_AND_CURRENT_AUDIT_REPORT_ZH.md`；机器摘要：`G3_PORT_AND_CURRENT_AUDIT_SUMMARY.json`。原始失败、未观察到清除/恢复、微小越流、参考请求误差与配对参照差均保留。当前paper_ready=false。

`INCREMENT_PORT_CURRENT_MANIFEST.json` 将“本包新增文件及哈希”与“依赖基础v2的原文件及哈希”分开列出。两类不得混为恢复原件。`source_speed_ablation/verify_increment_dependencies.py` 可在叠加后只读核对。

本包仅有自行编写的源码、图表、实验结果、研究摘要及公开来源链接。没有下载的论文/厂家PDF原件，没有wheel、venv或第三方代码副本。使用NumPy/SciPy/Matplotlib等依赖仍遵循基础包的来源记录，二进制与安装环境不随包复制。独立abc为自行实现的公开方程复核，直接调用的原自行实现代码由基础v2提供。

包含已完成的DC拓扑适用性更正、解析源包络及文献/波形证据摘要；这些摘要中的未来开发实例均标记为尚未仿真。**不包含**下一动态电流guard提案及其来源文件，亦没有实现该guard。

重现注意：现有实验脚本使用固定结果目录。若另行复验，先复制到新的版本化工作目录，避免覆盖本包原始记录。读取和校验无需重跑。
