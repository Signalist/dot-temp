# API 与科学来源核验（2026-10-04）

本目录代码为本次新写，没有下载、执行或复制第三方实现。网络浏览仅用于核对公开文档。

1. NVIDIA 当前 NVML Device Queries：
   https://docs.nvidia.com/deploy/nvml-api/latest/api/group__nvmlDeviceQueries.html
   支持只读功率、能量、温度、时钟、配置/执行 cap 与设备 UUID 查询；功率 API 输出 mW，累计能量输出 mJ。`nvmlDeviceGetPowerUsage` 在 Ampere（GA100 除外）或更新 GPU 返回约 1 秒平均；GA100 和较旧架构的接口描述为瞬时读数，也不等于已校准的无限带宽传感器。代码明确保留查询前后 host 时间，物理采样时刻未知，不能把 20 Hz 轮询写成 20 Hz 真实传感器带宽。
2. NVIDIA 当前 NVML Device Commands：
   https://docs.nvidia.com/deploy/nvml-api/latest/api/group__nvmlDeviceCommands.html
   `nvmlDeviceSetPowerManagementLimit` 受设备支持、有效范围和权限约束。本工具先读取原 cap、设备约束与 UUID，执行限于操作者范围且不超过原 cap；写回后读取配置值；`finally` 尝试恢复原值。拒绝权限错误，不提权、不更改驱动/持久化设置。API 成功不是物理功率跟踪成功。
3. NVIDIA 官方 Python binding 发布页：
   https://pypi.org/project/nvidia-ml-py/13.590.48/
   选择固定已发布版本 13.590.48；不是声称它是最新版。发布主体 NVIDIA，模块名 `pynvml`，发行包名 `nvidia-ml-py`。本次未安装、未在真实 GPU 上测试该 binding。公开 wheel SHA256：fd43d30ee9cd0b7940f5f9f9220b68d42722975e3992b6c21d14144c48760e43。
4. vLLM 官方 `CompletionOutput` / `RequestOutput` 文档：
   https://docs.vllm.ai/en/stable/api/vllm/outputs/
   `token_ids`、`finished`、`finish_reason`、`stop_reason` 的语义用于设计 engine 适配说明。稳定站点内容会更新，操作者必须保存实际部署的 vLLM 版本/commit 文档；本工具不安装 vLLM。`stop` 可来自停止规则，客户端拿到输出不是真实 device EOS。
5. vLLM 官方 completion serving：
   https://docs.vllm.ai/en/latest/api/vllm/entrypoints/openai/completion/serving/
   客户端适配器只处理 localhost `/v1/completions` SSE 格式；记录返回 chunk 与 finish_reason，保持 device EOS 为空，不将文本 chunk 计为 token。实际服务器是否支持 stream_options/include_usage 必须先小样本验收；不兼容即停止并修改适配器，不伪造字段。

## 本地研究依据

`../measurement/MEASUREMENT_FEASIBILITY_REPORT.md`：已准入语料没有完整命令/实际功率/服务/EOS/恢复/PCC 同步链，不能制造实测校准集。

`../measurement/protocol/MINIMAL_MEASUREMENT_PROTOCOL.md`：本套件沿用识别→冻结确认→消融/迁移、30 个聚类 pilot plateau 的最小设计和 iid 确认预算前提。

`../theory_grid/theory/GRID_MEMORY_THEOREMS.md`：p 是实际动态功率；真实 post-EOS burn/return 属于假设；成本为动态能量加 c×power-cycle 时长。PCC 与 grid tail 另需证据，0.05 Hz 仅研究预算。

`../recovery/W6_Round3_Portable_Evidence_20261004/round3_w6_20261004/README.md`：Azure 长度只提供探索分布；功率控制/服务律/瞬时 EOS/burn 仍为模型假设。

这些相对路径相对于 gpu_handoff 目录；完整研究 ZIP 包含相应目录。本工具自己的 CPU demo 不读取这些论文结果，不将它们当硬件样本。
