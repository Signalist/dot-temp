# G6 研究路线交接（2026-10-07）

请从 [research/G6/README.md](research/G6/README.md) 开始。该目录中的状态、证据边界、复现步骤和后续代理提示是本路线的交接依据；先进入该目录，再按其说明执行。

## 保留的历史根目录说明

下面保留原仓库 README。根目录 ZIP 与报告属于此前 DOT-AIGRID 阶段交付；本路线的交接材料位于 research/G6/。

# dot-temp

DOT-AIGRID 阶段交付：修改后的代码、公开任务 GPU_ONLY 描述性研究及累计证据。

## 下载与解压

下载两个 Part ZIP，将它们解压到同一目录。两个包都是独立普通 ZIP，每个严格小于 20,000,000 字节；不要二进制拼接。合并后的内容与原完整包一致。`DOT-AIGRID_Code_and_Delivery_20261006_PARTS.json` 提供每包大小和 SHA256。

`REPORT_ZH.md` 是最新阶段报告，`AUDIT.json` 是数据审计，`DELIVERY_INDEX.json` 是原工作区交付索引。索引中的服务器绝对路径属于来源记录；下载后使用 ZIP 中的相对路径。

## 结果范围

本轮完成 12 个常驻会话、72 个主请求，全部自然 EOS；写作/代码输出的质量问题保留并明确报告。不声称质量匹配的节能改善。物理控制、DC/PCC 仍 BLOCKED，J_W6 为空，原 W6 全实验验证尚未完成。

修改后的代码、协议和数据在分包中。最新采集代码位于 `continuation_20261006_54`，调度位于55，分析与封装位于56。请先阅读合并后 `README_START_HERE_ZH.md`。当前 GPU_ONLY 结果使用 `GPU_ONLY_Fixed_Task_Estimation_v2.zip`。

不自动运行 GPU/物理控制脚本。离线复算按报告说明进行，需要相应 Python 依赖；模型权重、环境与缓存不包含在交付中。

