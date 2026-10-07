# W6：公开实测证据能支持什么

核查日期：2026-10-04。零硬件session，零外来代码执行。后续取得一份719KB官方Azure长度CSV，已计算经验PMF；没有功率数据下载或硬件验证。其余是可用性审查。

## D01 NLR H100生成式工作负载power profiles，2026

[数据主页](https://data.nlr.gov/submissions/312)，[OEDI记录](https://data.openei.org/submissions/8651)，[一手论文](https://arxiv.org/html/2604.07345)。数据页公开列出5/10 Hz功率曲线、raw与aggregated格式、workload metadata；论文§2.2与§3.4–3.5讨论H100、vLLM离线/在线推理。进一步核查发现官网仅列1021.3MB的dataset.zip，没有小型单独metadata/length文件。未下载整包，实际文件字段和EOS标记仍未核实。OEDI镜像链接CC BY 4.0，但[原站许可](https://data.nlr.gov/node/312/license)为NLR自有notice，含保留notice、署名及indemnity条款，不能假定两者等价。

可支持：真实功率起落、空闲基线、不同负载时序与重复run的量级。**不能据此支持**：连续可控实际p、定值slew R、功率到服务的单值递增凹函数。已读实验主要改变workload/request rate，并非对同一任务进行完整实际功率干预扫描。数据还含由模型生成的whole-facility曲线，不能称它们为设施实测。0.1/0.2秒采样也不足以验证更快瞬态的硬slew保证。

## D02 Microsoft Azure LLM inference trace 2024

[官方说明](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md)，[官方许可](https://github.com/Azure/AzurePublicDataset/blob/master/LICENSE)。采集日期为2024-05-10至19；公开schema含TIMESTAMP、ContextTokens、GeneratedTokens，数据许可CC-BY。关联HPCA 2025 DynamoLLM。

可支持：用实际GeneratedTokens建立明确数据集上的经验F、按context/服务类型分组，并做分布漂移压力测试。**不能支持**：输出中止原因是自然EOS还是长度上限、token逐步时间、实际p或EOS后ramp。官方说明还指出benchmark replay强制生成对应长度，因此replay的固定输出长度不能叫“运行时未知EOS实测”。令tokens=W是建模近似，单token工作成本随context/phase变化需另说明。

## D02b 本轮已取得：Azure 2023 conversation文件

[官方说明](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2023.md)链接的完整小型CSV已无需登录下载：719,188字节、19,366条、623种GeneratedTokens，均值211.126、中位数129、p90=424、p99=601，经验support为7–1000。本地data_candidate/含未改动CSV、完整CC-BY4.0许可、SHA256、可重放处理脚本与完整PMF。

**不能忽略的数据边界**：README称2023-11-11采集，CSV时间是2023-11-16 18:15至19:14，未擅自调和。仅能把长度PMF用作trace-driven synthetic W；没有EOS原因、逐token work/power或恢复数据。样本最大1000不是未来请求硬上界。

## D03 ML.ENERGY Benchmark v3

[官方toolkit说明](https://ml.energy/data/)，[作者数据卡](https://huggingface.co/datasets/ml-energy/benchmark-v3)。公开文档列出H100/B200、per-request output lengths、ITL和power timelines；schema含avg_power_watts与output_throughput_tokens_per_sec，数据卡许可为Apache-2.0。

**访问状态**：数据文件要求登录并同意分享联系信息。未登录、未同意、未下载、未试图走raw/API路径绕过gate。若后续得到合规访问，它更适合对齐服务与power的统计剖面；但跨batch/config测得的曲线仍不能不经控制设计就当成对p的因果服务函数，也不能保证continuous-slew actuator模型。

## D04 NVIDIA官方执行边界

[当前nvidia-smi文档](https://docs.nvidia.com/deploy/nvidia-smi/index.html)，[NVML smoothing API](https://docs.nvidia.com/deploy/nvml-api/latest/api/group__nvmlPowerSmoothing.html)。本轮重新确认文档区分实际draw、requested/enforced ceiling，以及power-smoothing的TMP floor、ramp up/down和hysteresis字段。

可支持：这些设置/读数是不同对象。**不能从接口存在推出**“p(t)可任意命令且被硬约束|p_dot|≤R”或“s(p)已校准”。应固定GPU/firmware、功率测量边界、控制开关及sampling语义，分别验证服务吞吐与恢复动态。

## 次级候选未采用为定量依据

Ma等2026预印本[The Illusion of Power Capping in LLM Decode](https://arxiv.org/html/2605.11999)直接区分静态cap与actual draw，并披露50ms NVML采样及短prefill替代估计。它的摘要/引言同时使用137–300 W范围和最低280 W cap却作广泛“never”表述，不能未经配置级数据审查引用为普遍定量结论。本轮只记录为可读候选，没有重用其测量值或宣称所有decode都不受cap影响。

TokenPowerBench[原稿](https://arxiv.org/html/2512.03024)讨论prefill/decode的phase归因；本轮未验证到可直接取用的原始EOS/ramp数据，故不把其宣传的功能当作已获得的数据证据。

## 最小可发表验证合同

1. 同一硬件、模型、phase、context/batch条件下，记录功率命令、实际draw、服务进度及起止标记
2. 用独立重复run检验s(p)单值性、单调性、凹性，报告失配而非强行拟合
3. 恢复收费必须有EOS后功率/idle直到声明终态，且时间同步精度足够
4. token长度来自公共trace时，只称trace-driven synthetic EOS；若没有结束原因，不能称natural EOS
5. 公开数据、合成模型和真实设备结果分列，不把两种不同设备/服务的数据拼成一条实测曲线
