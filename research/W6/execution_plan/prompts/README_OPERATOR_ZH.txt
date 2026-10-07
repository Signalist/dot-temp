W6 Codex 提示词包：操作者使用说明
2026-10-05。这里交付的是后续实验计划和提示词，不包含新硬件结果，不保证现有GPU/仪表条件满足W6合同。

最省事的用法
1. 在打算执行实验的Codex环境中放入原始两份ZIP和本计划包：
   W6_CPU_GPU_Handoff_01_Main.zip
   W6_CPU_GPU_Handoff_02_NetworkData.zip
   两份是普通ZIP，共用根目录。不要cat拼接；由Codex先检查hash/路径/CRC，再合并解压到新目录。
2. 打开 00_MASTER_PROMPT_ZH.txt，把全文一次复制给Codex。无需把8段逐条拼接，也无需先自行填全部未知硬件参数。Codex应先盘点并集中询问具体权限/缺口。
3. 只有中途换会话、需要重启某一阶段或单独复核时，使用01至08阶段提示词。让新会话可以读取master与已有工作目录；必须先校验freeze/checkpoint，不能把阶段提示词当成跳过前置gate的捷径。

需要你准备或确认
- 能在目标Codex环境本地读取的两ZIP，原始hash在master内；工作目录、剩余磁盘和CPU/GPU时间预算
- GPU/模型本地文件或已有本地服务、具体engine版本；缺少模型/driver不会自动下载或安装
- 管理者允许的具体设备、独占与动作；若要写cap，明确可用范围、会话时长、温度/冷却、人工急停和恢复。所有数值由设备/操作者决定，示例不是安全标准
- 若目标是DC/PCC主张，相应合格人员安装/标定/同步的仪表和设施批准；只有GPU仍能做范围更窄的有用工作
- prompt/生成文本/token IDs是否允许记录与共享。默认仅hash/ID/长度，秘密永不记日志；公开语料保留来源与许可

先读懂这个缺口
原gpu_handoff已具备只读NVML、受限localhost客户端、event sink、meter CSV导入、可选有界cap操作与CPU测试。它没有完整的真实W6控制器、通用device EOS hook、物理burn或DC/PCC标定。master要求Codex明确实现、测试这些适配器；任何缺项必须BLOCKED，不能仅填字段“让validator通过”。

三个硬件层级
GPU_ONLY：GPU读数/host可见服务描述，不能宣布外部DC或网侧效果
GPU_DC：经标定全rail DC + 经验证的进度/EOS/actuator/恢复，才能研究对应物理W6合同
PCC：额外真实设施边界与同步电气/背景/初态/尾部证据，才能做网侧实测
没有高层资源，就缩小主张并交付低层结果；模拟并不补齐硬件层级。

阶段顺序
01 输入与资源盘点 → 02 实现桥/预检 → 03 pilot/标定/预算 → 04 冻结 → 05 主确认 → 06 必要消融/迁移/PCC → 07 主张审计 → 08 复算打包
I06默认起步30 episodes＝3独立session×5实际可达功率区域×2重复，独立cluster只有3；确认N必须依据pilot/MDE/QoS/不确定度/预算事前确定。“所有必要实验”指覆盖所有必要科学问题，不意味着机械跑所有设备×模型×长度×功率×温度组合。

哪些情况要停
- GPU不可用、独占/权限不明、取消后仍有请求、时钟reset/漏rail/标定漂移、设备异常/恢复失败
- actual p不可达、实际EOS不明、服务律/恢复/burn合同不成立
- 新确认结果看过后要改调参/排除规则。应先保留旧结果，建立amendment与新确认样本
失败、不显著或反例都是有效结果；不要要求Codex一直重跑到得到正收益。

你最后应收到什么
- README、主结论/效应与CI/质量/QoS/边界、实验与run状态矩阵、主张→证据表
- per-request/per-run typed CSV和JSONL、原始时间/功率/事件/命令、全部失败和尝试、校准/协议/软件硬件hash
- 图的SVG/PDF/PNG、figure_data、生成脚本；原始数据不可变，派生结果可重算
- 默认离线无GPU的一命令CPU复算，以及独立的GPU重放入口和硬件/权限gate
- review/code/raw若干普通ZIP，每份严格小于18,000,000 bytes；共同根、PARTS/manifest/hash、在新目录合并验证的报告
- 模型权重/驱动/缓存/凭证不在包中。若raw因隐私/许可不能共享，必须说明可复算范围和缺失依赖

contracts目录
包含结构化字段/单位合同和未填值模板。模板里的null/UNCONFIRMED/NOT_RUN是刻意的，不能当已完成授权/标定/数据证明。schema仅做结构校验；跨文件身份、时间、物理真实性、冻结时间和仪器证据必须另做语义审计。原kit的w6-1数据schema仍保留；新增study级schema是外层审计合同，不应降低原门禁。

本次交付的验收范围
只检查提示词/计划的一致性、结构化模板可读性、文件/包装完整性。未来Codex实现的reproduce_cpu.py、replay_gpu.py及硬件结果目前不存在或未运行；这些是任务输出要求，不能从本计划包的QA通过推出它们已通过。

详细实验矩阵与设计说明：从本目录分别打开 ../experiment_design/EXPERIMENT_MATRIX.json、../experiment_design/EXPERIMENT_MATRIX.csv、../experiment_design/DESIGN_REPORT_ZH.md。O01严格机器证书与O02额外独立复现为可选增强，不应为了“全跑”无限扩展主任务。
