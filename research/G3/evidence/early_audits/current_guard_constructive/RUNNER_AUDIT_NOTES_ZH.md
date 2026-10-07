# 四条件构造性基线 runner：透明变更与静态检查

状态：仅实现与静态/导入/纯计分测试通过。此工作未实例化 CommonGuard，未调用 guard 求解器，未执行物理轨迹。物理启动留给单独接口审阅后的显式单条件执行。

## 审计材料

- `run_constructive.py`：新 driver，旧 `current_guard_gate1/run_models.py` 完整拷贝后显式适配；没有运行期 monkeypatch
- `RUNNER_DIFF_FROM_GATE1.patch`：完整统一 diff
- `RUNNER_STATIC_AUDIT.json`：源 SHA256、AST 不变清单及已执行纯测试
- `test_runner_static.py`：可重现纯测试；临时合成数据只写临时子目录，结束自动清除，没有真实结果 claim

最终 runner SHA256：`e9bceab631ec7f26c9639aa3a2887ddf21f8cefdd63390c76fbeb1d3d30563c5`

## 有意修改范围

1. `load_design`：冻结四条件提案及原 Gate1→Gate0→物理协议/checkpoint 链；固定共同 guard 和原 allocator 源 SHA256；仅 P0-fast、R0-fast、P50-fast、R50-fast，2 ms、50 MW/s；恢复原 .6 s 完整 checkpoint
2. `check_run_admission`：保持单条件/禁止覆盖/条件性5μs细化机制；先两个健康记录，再依各自健康物理/guard admission 决定对应故障是否可执行；失败 P 不阻止通过的 R，反之亦然
3. `reference_comparison`：健康同 allocator 无guard参考不存在，明确 `NOT_AVAILABLE`，绝对服务请求偏差为主；故障必须配对自身 P0 或 R0，检查 allocator、端口、runner/wrapper/guard/allocator/checkpoint hash、trace hash、全归一化初始状态
4. `run`：导入新 wrapper，直接从封存 Gate1 路径导入 CommonGuard；初始化后设置 `guard.nominal_allocator`；名义 controller 计分改成同 allocator；结果记录实际源路径/hash及allocator标签
5. `update_roster`：改为四行及自身 allocator 的健康 admission
6. 新增 `healthy_case_id`、`read_healthy_reference`、`external_q_guard_controls`：原 Q+guard C0-fast/C50-fast只作外部已知对照，明确不是同allocator参考、不得用于恢复评分
7. CLI仅允许四个冻结case，输出只进入新 `current_guard_constructive/results`；导入禁止旧目录bytecode写入

## AST 保持不变的范围

- 完整 gzip 轨迹执行和逐采样日志代码块：仅把同 allocator 名义采样调用还原成旧调用后，AST 与封存 Gate1 完全相同
- 因此原 DOP853、10μs/条件性5μs、rtol/atol、100μs时钟、故障精确分段、硬阈值/接触根、异常完整回滚检查、queue/AW检查、逐步fullstate/plan/timing日志均未改
- `service`、`inventory`、`energy_necessary_condition`、`recovery_score`、`TimingSummary`、`flattened_scalars` 以及序列化辅助函数 AST 完全相同
- `run` 内 `fun`、`level`、`margins`、`measure`、`row_margins` 完全相同
- STATE_NAMES、COLS、CI、CONTROL_COLS、INTERVAL_COLS、NORMALIZED_NAMES、HARD_NAMES 完全相同

## 已执行检查

- 四case冻结协议/源hash、端口参数、原始完整checkpoint读取及case拒绝逻辑
- 健康 `NOT_AVAILABLE` 参考语义，绝对P/Q积分与零时长处理
- 临时合成fixture下自身健康配对、hash/provenance防错、完整初态校验与零匹配差值计分
- 两健康在先、各自失败故障拒绝、另一个通过allocator可独立准入
- 禁止覆盖、未指示5μs细化拒绝
- 原Q+guard外部对照标签明确，不用于恢复
- 新模块导入无CommonGuard加载，更无求解/传播

复查命令（仅静态测试，不调用physical run）：

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python current_guard_constructive/test_runner_static.py

此脚本预期尚无真实 `results` 目录，仅用于物理启动前审计。它不会重写runner、wrapper或任何旧Gate1文件。

## 边界

本次通过不是物理安全通过、健康服务透明度通过、故障恢复通过、联合DC/SoC证书或100μs实时实现通过。原固定阈值、guard冷启动/求解/独立primal验证/备份逻辑完全由封存common_guard继续提供。
