# W6 measurement feasibility audit

Audit date: 2026-10-04. Outcome: **NO currently admitted dataset closes the W6 deployment-measurement contract.** No service-law fit, new policy evaluation, physical experiment, or fresh statistical holdout is claimed.

## 结论

现有数据只能分别支持经验长度分布、同次运行的低频功率/聚合吞吐描述、以及功率遥测对DC参考仪的误差研究。没有一份已准入公开数据同时记录同一任务的功率命令、真实功率、逐步服务、自然EOS及其可见延迟、完整恢复、PCC功率与时钟误差。不同来源不能拼成一次实测。W6可继续写成条件理论与模型数值论文；实际GPU服务律、物理slew/burn能力和GPU→PCC映射不能被称为已标定。

## Scope and actual inspection

The earlier W6 status and report, A2/W5/A3/G5 source registers, and the final public-source catalog were read. Existing source bytes were reused rather than downloaded again. A self-authored read-only audit hashed 23 local inputs and completed before a workspace discontinuity at 14:16 UTC. It parsed both original NLR inference power logs (715,989 and 644,135 rows), both complete DaRUS CSVs (1,076,374 and 1,085,042 rows), the Azure conversation CSV, all eight compact SC24/PS3 power records, actual NLR JSON/JSONL metadata, and one representative SweetSpot trace from each of 13 model directories. The SweetSpot archive inventory contained 1,764 trace CSVs. The PS3 original header and 2,000-row prefix were also inspected.

These are direct field/timestamp audits, not empirical W6 calibrations. More rows, GPU channels, time windows, page segments, or copied files do not create independent experimental units. The historical data have already informed prior research; relabeling old test windows as a new independent test set would be invalid.

The source/new-output trees disappeared from the same cwd between tool calls at 14:16 UTC. This report preserves completed observations and separately records the replay limitation in results/WORKSPACE_DISCONTINUITY.json. It does not claim the missing raw files were restored or reverified afterward.

## Source-specific findings

### 1. Azure 2023 conversation inference trace

Actual fields: TIMESTAMP, ContextTokens, GeneratedTokens. There are 19,366 requests and 623 distinct observed output lengths, range 7–1000. No service timestamps, hardware identity, power, EOS reason, cap, or recovery fields exist. Its PMF is admissible as an explicitly exploratory, trace-driven length scenario, not a natural-EOS or prospective bounded-support guarantee. The README/CSV collection-date discrepancy already recorded by round three remains unresolved. Source: [official description](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2023.md), CC BY 4.0.

### 2. NLR 312 same-capture GPU power and service

The two original logs contain a timestamp, reading-time in ns, four GPU mW readings, and four temperatures. Finite has 715,989 rows with median positive interval 0.100095 s, maximum 0.142721 s; rate has 644,135 rows with median 0.100089 s, maximum 0.258216 s. These are polling intervals, not identified physical bandwidth.

The derived service files contain engine, prompt/generation tokens per second, running/waiting requests, KV-cache percentage and prefix-cache hit rate. Finite has 6,089 service rows, median gap 10 s and maximum 70 s. Rate has 6,044, median 10 s and maximum 50 s. The original finite benchmark JSONL has 1,024 aggregate result objects with latency percentiles, completed counts and throughput; it is not a per-request progress or completion log. Configuration files vary request rate, prompt count, length setting and seed, with no actual-power command schedule.

There are 1,026 finite and 200 rate segment records but only two continuous inference captures. The finite capture predates rate, and both were previously inspected. Year is inferred for the service logger; timezone, clock skew, logger-window boundaries and collection latency are unverified. Queue-zero and HTTP 200 are not proof of successful request EOS. Overlapping requests and back-to-back benchmark segments preclude treating every segment tail as an isolated recovery episode. Same-run descriptive power/throughput analysis is valid within these caveats; a causal single-task s(p), command response and EOS-delay law are not identified.

Source: [NLR catalog](https://data.nlr.gov/submissions/312), [dataset-specific notice](https://data.nlr.gov/node/312/license). Preserve the complete DOE/NLR/ALLIANCE notice; do not replace it with an assumed CC-BY license. The associated publication explicitly scales measured component profiles through whole-facility simulation; those outputs are not measured PCC trajectories. [Primary paper](https://arxiv.org/html/2604.07345)

### 3. SweetSpot

The actual trace schema is Timestamp (ms), gpu_power, gpu_clock. The archive contains 1,764 trace CSVs across 13 models; 13 representative records were read. Twelve inspected representatives had 500 ms spacing; one Llama-3.2-1B record had 200 ms spacing. Documentation describes 100–500 ms polling. Aggregate CSVs supply input/output length settings, batch, requests, throughput, latency and energy. No command time series, per-token progress, stop reason, event visibility, calibrated idle-return state, or PCC channel is supplied in those inspected schemas.

Changing context/batch/model changes both work and power. It is not an intervention on actual power under a fixed service condition. Prescribed output-length settings are not natural EOS. Original W1/W3 exposure includes 299 analyzed records and broader archive QC; remaining members are not automatically pristine holdout data. Source: [Zenodo 18714476](https://zenodo.org/records/18714476), CC BY 4.0 as declared by metadata and README; a separately named LICENSE file was absent in the archive.

### 4. SC24 GPU Power Benchmark

Seven previously used paired records expose reference_t/reference_W and GPU timestamps/power arrays. Median reference spacing is approximately 0.205216 ms; GPU polling is approximately 7–13 ms in the inspected records. These pairs can interrogate telemetry filtering and measurement-domain discrepancies. The PMD boundary omits 3.3 V, original tick/voltage conventions need to remain explicit, and timestamp alignment lacks a certified physical error bound. Workload transitions in a power benchmark are not a synchronized EOS/actuator/service experiment. There is no PCC measurement. Source: [author repository](https://github.com/JimZeyuYang/GPU_Power_Benchmark), commit ab12c0606775e38872501de8a5cf57ca0e863fa1, MIT.

### 5. PowerSensor3

AD4000 raw fields include marker, host time, dt_micro, device_timestamp, three rail current/voltage/power triplets and power_total. The inspected device-clock prefix mostly advances by 50 raw units; the complete compact host-time median spacing is approximately 46.0 microseconds and NVML polling approximately 60 ms. Host timestamp spacing is not itself sensor sample rate or certified synchronization. Three-rail DC reference supports measurement comparisons but supplies no W6 progress/EOS/control/PCC chain. A3 also reused a W7700 paired capture; it is another previously exposed sensor-comparison record, not a new W6 deployment. Source: [author v1.0.0 data](https://github.com/nlesc-recruit/powersensor3-results/tree/v1.0.0), [DOI](https://doi.org/10.5281/zenodo.15037451), Apache-2.0.

### 6. DaRUS 3044

Actual fields: sensor; time[ms]; power[W]; run; status. NVIDIA CSV has 1,076,374 rows and AMD has 1,085,042. Rail-channel median positive spacing is 5 ms within run/page groups; NVIDIA NVML is 6 ms and AMD ADL positive gaps are 17–24 ms, with duplicate/nonincreasing entries. Time resets by page, so concatenating status transitions into a single monotonic capture would be wrong. Four run labels per file and 60 page/run groups are not verified independent acquisition sessions. Logged page-navigation/showing state is not quantitative service progress. No command, natural EOS, or PCC fields are present. Named external rails are DC; an AC instrument named in dataset metadata does not establish an AC channel in these selected logs. Source: [DaRUS 3044 V1](https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-3044), CC BY 4.0.

### 7. G5 and final catalog

G5 explicitly reports zero new hardware/workload samples, an ideal averaged unity-power-factor interface, and finite network simulations. Its cumulative-energy/power fidelity framework can be imported as a conditional error contract; its simulations cannot identify the actual GPU-to-PCC map, sensor bandwidth, terminal thermal state, or facility-specific frequency limits. The final catalog also identifies these missing physical layers; this audit confirms that boundary rather than upgrading simulation to measurement.

## New public alternatives actually checked

1. **WattGPU:** repository tree pinned at 4e010359c167ac8c65b55aabd1aafbf765ae5d91 and a 65,536-byte prefix of data/watt_counts_subset.csv inspected. Its schema contains model/GPU, rate, aggregate duration/energy, mean/min/max/std power and per-request length/latency lists. It lacks a power timeline, command timeline, natural stop reasons and recovery/PCC. Useful for descriptive cross-model/GPU aggregates, not W6 dynamic calibration. Apache-2.0 LICENSE was read. [Repository](https://github.com/maufadel/wattgpu)
2. **TokenPowerBench:** repository tree pinned at 9a50272213885bd9bba8427e34ebdf345c2204fe and one published JSON result inspected. The result is run-aggregate power/energy/throughput. It has no raw timestamped samples or finish reasons and includes zero CPU/DRAM/total-power fields; zeros must not be interpreted as measured zero consumption. Current source code can retain samples, but that does not retroactively establish published old measurements. README says MIT; no separate LICENSE appeared in the inspected tree, so redistribution licensing remains unresolved. No downloaded code was executed. [Repository](https://github.com/chenxuniu/TokenPowerBench)
3. **ML.ENERGY v3:** public card describes H100/B200, request metrics and power timelines, but files require login and contact-information sharing. No login, acceptance, raw/API file request or bypass attempted. Even authorized access would need a fresh field/intervention/recovery audit before admission. Apache-2.0 is declared on the card. [Official access instructions](https://ml.energy/data/), [dataset card](https://huggingface.co/datasets/ml-energy/benchmark-v3)
4. **GPU Power Super-Resolution:** public Zenodo record advertises PS3, NVML, vLLM and phase markers but explicitly restricts files. No restricted file endpoints were requested. Metadata is promising for a measurement subproblem; W6 sufficiency remains unknown. [Zenodo 21058153](https://zenodo.org/records/21058153)
5. **Argonne Data Center Flexibility Dataset:** the current official project page describes planned H100/B200 control sweeps and QoS recording; it offers no release used here. A future plan is not obtained data. [Official project](https://www.jlse.anl.gov/projects/benchmarking/data-center-flexibility-dataset)
6. **High-resolution AI training dataset:** its paper describes component telemetry, 20 ms node polling and no accessible CPU power in virtualized node measurements. The AGC frequency case study is simulated. It does not provide the stated W6 inference/EOS/control/PCC chain; paper-only scope audit, not raw-data admission. [Primary publication](https://www.nature.com/articles/s41597-026-07496-6), [data DOI](https://doi.org/10.6084/m9.figshare.31654879)
7. **IPDPS26-LLM-Energy:** public tree 860267c519bed17373c3b0926c42676a652d05fd was inspected. It contains benchmark/monitoring code and workload input files, but no measurement CSV/JSON trace release was found in that tree. Software capability alone is not an experiment. [Repository](https://github.com/SPEAR-UIC/IPDPS26-LLM-Energy)

The search is a dated, bounded audit of these sources, not a proof that no suitable dataset exists anywhere.

## Identifiability, not just file availability

- A power cap u is an actuator command, not observed actual dynamic power p. Observational covariation of throughput and p under changing requests/context/temperature does not identify a causal single-valued service s(p). Even under a fixed law, finitely many aggregate integrals leave unobserved functional degrees of freedom without explicit restrictions.
- Without stop reason and maximum-token/cancellation metadata, the observed length distribution is compatible with multiple natural completion distributions and censoring processes.
- Without synchronized true EOS, scheduler visibility and actuator effect times, delay can be assigned arbitrarily within hidden intervals. Aggregate server statistics cannot bound it at token/control timescales.
- Without a post-EOS trajectory and a declared restored state, two physical systems can share every observed execution sample and have different recovery duration/energy. A subsequent job's power is not the previous job's recovery.
- With no simultaneous PCC output, arbitrarily different transfer kernels g are compatible with the same GPU trace. A PUE multiplier or unmatched facility trace does not identify g.
- Finite sampled values do not upper-bound continuous slew: between-sample spikes can preserve the same samples. A hard slew claim requires independently justified bandwidth/regularity plus sensor/clock error, or a device guarantee tested within its conditions. Polling faster does not identify the internal sensor filter.

## What can be validated now

Admissible now: reproduce Azure PMF and synthetic EOS stress; audit recorded-domain sensor discrepancies and timestamp pathologies; test parser/metric invariants; run theoretical and explicitly model-based grid/error-budget experiments; compare fixed assumptions with known failures. Existing observational NLR/SweetSpot data may falsify an overbroad universal service model, but cannot certify a controlled scalar service law.

Not admissible now: measured W6 energy savings; measured p-slew realizability; calibrated natural-EOS latency or physical burn; measured full-cycle terminal recovery; measured GPU-to-PCC map; deterministic hardware/grid safety; a fresh empirical calibration/test result. See protocol/MINIMAL_MEASUREMENT_PROTOCOL.md and protocol/VALIDATION_BUDGET.json for the smallest next acquisition and its stopping criteria.

## Decision

The matched-data gate is closed. **Do not fit or manufacture a calibration/test split from the present corpus.** A prospective split rule is supplied, but it contains no admitted measurement records. Before any later fitting or large evaluation, a newly obtained candidate must pass the channel/time/boundary/provenance gate, its independent acquisition units must be frozen, and the parent must receive the sufficiency finding.
