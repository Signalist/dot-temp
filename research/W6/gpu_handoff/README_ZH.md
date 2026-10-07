# W6 GPU 实验交接包

这是为以后拿到 GPU 准备的最小可执行工具包。当前没有 GPU：只执行 CPU 单元测试、合成端到端、静态检查；未执行 GPU、真实模型请求、功率控制或电气实验。SIMULATED 示例不是论文实测结果。

先读：
- docs/GPU_EXPERIMENT_CHECKLIST_ZH.md：硬件清单、GPU-only / GPU+DC / PCC 三层、识别→冻结确认→消融迁移与安全停机
- docs/DATA_CONTRACT_AND_ADAPTERS_ZH.md：单位/时钟/自然 EOS/删失/暖机/冷却/完整周期、适配器边界
- docs/SOURCE_LEDGER.md：本次核对的 NVIDIA/vLLM 官方文档与论文依据
- verification/STATUS.json：实际运行了哪些检查、哪些从未运行

## 1. 无 GPU 也可以直接运行

从本目录执行。采集适配器目标为 Linux/POSIX 主线程，本次仅在 Linux 测试；绝对请求超时依赖 setitimer/SIGALRM，其他系统不宣称兼容。Python 3.10+，CPU 核心只用标准库，不需要 pip 安装。

```sh
python3 -m unittest discover -s tests -v
python3 check_static.py
python3 verify_bundle.py
python3 -m w6kit demo /tmp/w6-simulated-demo-01
python3 -m w6kit validate /tmp/w6-simulated-demo-01/run_00 --purpose w6-dc
python3 -m w6kit analyze /tmp/w6-simulated-demo-01/run_00
python3 -m w6kit budget --alpha 0.05 --delta 0.05 --endpoints 1
```

目标目录必须不存在；工具不覆盖已有采集、冻结拟合或评估。demo 生成 8 个 SIMULATED run、按完整 session 冻结的 split、能量分解、诊断服务 fit 与独立角色 evaluation。8 个合成 run 仅测试软件流程，不满足物理 pilot 或统计样本预算。包内 examples/SIMULATED_DEMO 是本次实际生成的示例。

不带执行标志的采集预览不会调用 GPU、请求服务或改 cap：

```sh
python3 -m w6kit telemetry configs/telemetry.example.json /tmp/w6-raw-unused
python3 -m w6kit request configs/request.example.json /tmp/w6-events-unused.jsonl
python3 -m w6kit cap-session configs/cap_session.example.json /tmp/w6-cap-unused.jsonl
```

## 2. 将来在获准的 GPU 主机上

以下由操作者在自己的机器上选择执行。先编辑配置中的 REPLACE/OPERATOR 字段，确认独占、测量边界、时钟、模型服务与安全条件。不要原样使用 cap 的示例数值。

可选只读采集依赖为 NVIDIA 官方 nvidia-ml-py==13.590.48，模块名 pynvml。已有合适驱动提供 NVML shared library；工具不安装驱动/CUDA/engine/权重。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: -r requirements-gpu.txt
.venv/bin/python -m w6kit telemetry configs/telemetry.operator.json /tmp/w6-raw-run001 --execute
```

遥测按 duration_s 持续记录；请在独立终端启动，先覆盖 idle/warmup，再运行一条已审核请求。duration_s 只是采集上限，未覆盖返回/冷却就不能准入；不能用任意 120 s 证明恢复。第一次只做小任务与只读观察。

服务器必须由操作者用本地模型自行启动。本工具不启动服务、不下载模型，不要求 API key。客户端只允许本地 HTTP /v1/completions，拒绝代理与重定向。

```sh
.venv/bin/python -m w6kit request configs/request.operator.json /tmp/w6-events-run001.jsonl --execute
```

这只生成客户端可见事件；真正 device EOS 与 token 完成时间仍需适配。超时后服务端可能继续工作，必须用已验证的取消/队列检查流程恢复，不能立即启动下一任务。

## 3. 可选 cap API 试验（默认关闭）

只在机器管理者明确批准、设备独占且具备人工恢复手段时使用。配置 operator_reviewed/exclusive_device/no_other_workloads 必须全 true，UUID hash 必须与 inventory 相符。所有 cap 同时在设备支持范围、操作者范围且≤会话原始 cap。它不执行工作负载，也不产生 burn。

```sh
.venv/bin/python -m w6kit cap-session configs/cap_session.operator.json /tmp/w6-cap-run001.jsonl --execute-power-control
```

成功后仍必须检查 cap_restore=verified_readback。普通异常、SIGINT/SIGTERM 尝试 finally 恢复；断电、SIGKILL、驱动丢卡/卡死无软件恢复保证。温度检查不是安全联锁。权限不足就停止，不使用 sudo 或自动授权。

## 4. 整理、冻结和复算真实数据

按 schemas/ 与 DATA_CONTRACT 文档，将同次 raw telemetry、engine events、已标定 meter 数据整理为一个 run 目录。保留原件、软件版本、所有转换 spec 与 hash。原始遥测中的 baseline/null 不会被工具自动补成“实测”。

```sh
python3 -m w6kit import-meter raw_meter.csv configs/meter_import.operator.json imported_dc.jsonl
python3 -m w6kit freeze-split configs/registry.operator.json frozen_split.json
python3 -m w6kit validate runs/run_ident_001 --purpose descriptive
python3 -m w6kit validate runs/run_ident_001 --purpose w6-dc
python3 -m w6kit fit-service runs frozen_split.json frozen_service_model.json
python3 -m w6kit evaluate-service runs frozen_split.json frozen_service_model.json untouched_evaluation.json
```

先冻结 registry 与 hash，再采集 outcome；上述命令展示接口，不允许先看结果再伪称预注册。freeze-split 会拒绝模板的 declared_before_outcomes=false，需操作者完成真实预注册后更改并保存外部时间戳。

`w6-dc` 和 `pcc` 是声明性数据完整性 gate，不是安全/准确性认证；任何仪表证书、时钟误差、device EOS、物理 actuator 或 full-cycle 判据未建立，都应停止并报告缺口。现有公开语料不被本工具改名成 matched measured calibration/test。

## 5. 已交付与明确尚缺

已交付：只读 NVML logger、受限 localhost SSE client、engine event sink、DC/PCC CSV clock adapter、可选有界 cap API/恢复日志、严格准入器、完整周期积分、分组冻结/泄漏检查、诊断 service fit/冻结 evaluation、iid 预算计算、合成 fixtures 与 CPU 回归。

尚缺：实际硬件支持测试、每个 engine revision 的 device 完成 hook、物理仪表驱动/标定/接线、真实恢复或 burn actuator、真实服务包络、PCC 映射与网侧尾部认证。工具没有隐藏地声称这些已完成。
