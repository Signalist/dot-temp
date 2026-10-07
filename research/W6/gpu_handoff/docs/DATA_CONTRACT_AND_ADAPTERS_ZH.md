# 数据契约与适配器说明

## 文件与字段

一个完整 acquisition/run 目录包含 manifest.json、power.jsonl、events.jsonl、commands.jsonl。所有数据行必须携带 acquisition_id、run_id、clock_id、evidence；不可跨任务拼接。session_id 表示独立采集/初始化组，不能把窗口当 session。`SIMULATED` 标签保留到所有输出；一个自报标签或 hash 不能证明数据真实。

- 时间：非负整数 ns，同一 boot 的 host monotonic 域；墙钟只作来源锚点。跨机器/设备需独立校准 `host_ns = slope × device_timestamp × time_scale_to_ns + offset_ns`，记录同步前/后 marker、offset/drift/latency 上界。不允许用“相关性最大”对齐后宣称无延迟
- 功率：W；绝对功率 power_W 与 idle baseline_W 独立；动态 p=power_W−baseline_W，不截零。能量 J；NVML mW/mJ 分别乘 0.001。不要将 configured_cap_W/enforced_cap_W 减 baseline 后替代 p
- 功率行：t_ns、arrival_ns、channel、power_W、baseline_W、status。NVML 原始日志还保留 query_begin_ns、arrival_ns、sensor_time_ns=null、energy_J、cap、温度、时钟及逐字段错误。轮询间隔不等于设备内部采样时间
- channel metadata：named electrical boundary、source、rail_coverage、all_required_rails、calibration_id、filter_description、bandwidth_Hz、calibration_error_W、filter_error_W、baseline_error_W、clock_transform_id。未知写 null，不能填 0；物理声明 gate 会拒绝未知
- manifest：硬件/模型/engine/hash、model_family、phase/context/batch stratum、concurrency=1、max_tokens、request_id、baseline_method、clock_error_ns、max_gap_ns、initial_state、analysis window 与审计 ID
- 命令：issue_ns、return_ns、requested/configured/enforced cap、status、physical_effect_ns。物理效果不知道时保持 null；API 回执时刻不是设备实际响应时刻。事件型原始 cap 日志保留，分析使用 cap_return 回执
- 事件：idle_before、warmup_start/end、request_start、progress、eos_visible、power_return、terminal_state、capture_end。phase 时间严格有序，完整功率通道覆盖从 idle 到 capture_end，不只覆盖执行段
- progress：唯一递增时间、同 request_id、累计 completed_tokens、work_source、phase/context/batch、clock。文本 chunk 不是 token。即使 token 计数准确，token 成本也随 context/phase 变化
- EOS：finish_reason、stop_class、max_tokens、censored、true_eos_ns、true_eos_source。自然 EOS 要核验 EOS token 与停止规则；length/cancel/error/timeout/unknown/stop_rule 保留 censoring；自然长度分布拟合另需有根据的删失模型，本套件不把删失长度当自然 EOS
- full cycle：power_return 是声明的实际动态功率返回判据；terminal_state 需含 criterion_id、restored、持续 hold_ns 和 initial_state 对应的状态分类。原始温度/clock/队列等验收证据另存审计文件。自动比对字段相等不证明物理状态相等

schemas/*.schema.json 是结构说明；跨文件身份、顺序、coverage、split 和服务窗口检查以 w6kit/core.py 为执行规范。声明性检查不替代仪器证书、同步实验或工程安全审查。

## 三个已实现适配层

### 1. 只读 NVML

`telemetry` 仅调用查询；缺失 API/字段保留 null 和异常类型，不用零替代。输出 telemetry.jsonl、inventory.json。它有意不生成“已经标定”的 manifest，不估造 baseline、不伪造 recovery/EOS。操作者需将同次记录连同 engine/meter 事件整理成上述格式。

单独的 NVML 累积能量可作交叉核对，但必须先验证计数器重置、单位、采样时域与测量边界；当前通用 analysis 只对明确时间边界内功率做分段线性积分，未把 NVML counter 当无误差基准。

### 2. localhost SSE 工作负载客户端

`request` 向操作者已启动的本地 /v1/completions 提交一个文本请求，max_tokens≤4096，绝对时限≤600 s。关闭代理和重定向；不发远程请求、不用 credentials、不保存 prompt/生成内容。请求体只在该本地端点使用；日志保留 input_sha256 与字节数。Linux 主线程以绝对 timer 防慢速持续流；非 Unix 或已有 timer 则拒绝。

已实现字段：request_start、chunk_received、eos_visible、request_transport_end/server usage、request_error。`finish_reason=stop` 一律仅判 stop_rule/censored，true_eos_ns=null；即使 server usage 给出 total tokens，也没有逐 token 时间。这个适配器本身不能通过完整 W6 DC gate。

传输失败/超时不保证服务端请求已取消。工具不擅自调用引擎管理或 kill 服务；操作者检查队列并通过已验证的 request cancel hook 清理，完成返回记录后才能继续。服务器支持 request ID/cancellation 的方式需与实际版本核对。

### 3. engine 与仪器的显式接入点

`EventSink.emit` 可以被操作者的 engine 插桩调用。`record_engine_progress` 用累计 token_ids 长度记录 host engine-output 可见事件；它不声称 CUDA/device 完成。因此这些 host-output 事件单独不能通过 w6-dc 的 device-aligned progress gate；后者还要求 timestamp_source=device_completion_aligned 与 progress_timing_audit_id。每请求一个 writer 文件，避免进程写入竞争；多个源先各自验证单调，再按已校准 clock 转换合并，保留原件/hash。不要全局排序来掩盖 clock reset。

vLLM：在固定 revision 的 async 输出回调读 RequestOutput.request_id、outputs[0].token_ids、finished、finish_reason、stop_reason。实际 output kind 必须是 cumulative（delta 输出要显式累加且查重），n=1；finished 只是引擎层观察。需要 device 完成时，在最后 useful kernel/token 的实际执行路径增加同步/事件 instrumentation，并说明 stream 语义、timestamp→host 转换、开销与误差。逐 token 同步可能改变性能，需 A/B 评估插桩扰动。工具没有伪造通用 device EOS hook。

DC/PCC 仪器：导出 CSV 为 sensor_timestamp,arrival_monotonic_ns,power,status，通过 `import-meter` 和操作者提供的校准 spec 映射。每个物理 channel 单独文件，拒绝 reset/重复时间。仪表驱动、rail 合计、反混叠和 marker 采集依仪器而定，本工具不自动安装。保存原始 source timestamp/CSV/hash，转换不创造标定证据。

## 分析、切分与拒绝规则

`analyze` 对完整窗口分段线性积分，分别报告 gross/dynamic cycle、productive/recovery、whole-capture 与 cooldown 能量。输出采样差分最大斜率只作描述，不推断连续硬上界。未知 true EOS 时服务/恢复分量为 null，不用客户端接收时间顶替。

冻结 registry 的每 run analysis_protocol 绑定 stratum、model/engine revision、stop 配置、max_tokens 与相对 request_start 的 service_window_offsets_ns。相对窗口可在采集之前冻结；使用冻结规则 first_progress_at_or_after_offset，在指定 offset 之后选择第一个真实 progress event，且延迟不得超过冻结 endpoint_lag_max_ns。实际事件时间和计数用于积分/速率，避免要求硬件恰好在某 ns 出 token。过短任务、缺端点或不覆盖窗口就失败，不能事后换窗口“拯救”。真实自然 EOS pilot 可能因此不适合此简单拟合；应在新 protocol 中预先定义更合适的 interval/censoring 方法。

`fit-service` 只打开 identification/calibration outcome 文件；`evaluate-service` 打开 registry 所列 confirmation/ablation/transfer，全体必需 run 不能默默缺失。人为剔除坏 run 必须记录预先冻结规则与 attrition；当前最小实现遇到缺失就停止，不自动插补。按 transfer_axis 排除跨角色的完整设备或模型族。

OLS 只是区间平均服务与实际平均 DC 动态功率的诊断关系。均值下的非线性偏差、输入随机性、传感器滤波、热历史、内生性、pointwise service 误差都没有被这个简单 fit 解决。max residual 不是未来 supremum 保证；不要用它自动给 W6 安全 guard 发证。已提供凹性/单调性经验反例检测，没有强制凹化。
