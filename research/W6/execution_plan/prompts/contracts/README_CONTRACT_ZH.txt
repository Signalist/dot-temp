W6 study级数据合同（w6-plan-1）

这是后续执行交付要求，不是已实现硬件接口，也不替换旧gpu_handoff/schemas的w6-1原始run合同。原始manifest/power/events/commands仍须按旧合同并经语义审计；新增run_audit连接实验ID、冻结、attempt与审查状态。

文件用途
- protocol.template.json：完整事前协议草稿；null必须由实际证据或操作者选择确定
- operator_scope.template.json：未经确认的权限清单，不是授权
- freeze_receipt.schema/template：冻结、真实确认与时间锚；哈希不是签名或独立时间证据
- run_audit.schema：所有尝试的状态/身份/来源/封存记录，失败与partial保留
- request_metrics.schema + header + field_dictionary：平面逐请求指标。不同electrical_boundary分行并保留主键；这些行不是新增独立样本
- run_metrics.schema + header：逐run/attempt统计；其字段suffix约定为_ns=ns、_s=s、_J=J、_bytes=byte；count字段为非负整数，类别/原因是字符串；完整已知字段见run_metrics_field_dictionary；实际新增扩展字段仍须补齐字典
- experiment_status.schema：ID逐项结果，PASS必须说明gate_level
- package_manifest.schema：每payload路径/字节/hash/标签/许可/part；manifest不自hash
- clock_transform.template：原sensor时间到host monotonic变换与实测误差依据
- claim_evidence.template、final_status.template：结果事实与主张边界；未知数为null，不先填零

JSON strict UTF-8，禁NaN/Infinity；CSV RFC4180、null用空字段表示、bool为true/false、整数字段不写小数。未来实现须有strict reader进行类型转换、枚举/单位校验及跨文件身份检查，不能依赖Excel猜类型。CSV空值为缺失，不是零；empty string不是有效非空ID。路径根相对POSIX，禁越界。

所有模板默认DRAFT/NOT_RUN/UNCONFIRMED。schema合规不等于物理真实性、统计有效、事前冻结或授权有效。用例必须包含预期拒绝样本：伪MEASURED、缺device EOS、无仪表却PCC、confirmation漏项、混run ID、clock reset、复写原件与缺冻结。

未知指标附missing_reasons或null_reasons_ref。时间端点必须同clock域或附可审计变换；如果只有host观察，不填true_eos。T_powercycle_s从request_start到power_return；T_matched_cycle_s到matched_state；网态尾部另报。J_W6只使用冻结c_W与dynamic功率周期，不替换成matched-state目标。

现有接口兼容性不得假定：旧validate_registry强制transfer_axis为device或model_family，且按整设备/模型族拒绝泄漏；没有workload/phase/context或none轴。无transfer研究可以保留真实的device/model_family轴并使用空transfer角色集合，明确不声称迁移；仅字面none轴需扩展。X01或X04等同设备workload/phase/context迁移须使用经过测试的版本化registry扩展/独立协议映射，不伪填新device/model_family标签。旧selected_folders只找root/run_*，evaluate-service要求registry内所有confirmation/ablation/transfer都存在；本计划的嵌套session/run/attempt raw树需实现安全索引/只读派生扁平视图或版本化path registry，核对每个run/attempt身份与hash。按阶段评估应显式冻结必需集合和依赖，不能默默忽略缺失run。所有扩展保留旧结构/泄漏/完整性门禁，新增角色冻结、父子hash链接、无transfer、workload-transfer及嵌套路径/一侧失败测试。

J_W6_J仅对应冻结的理论电气边界（通常GPU全rail DC动态功率），NVML/AC/PCC行填null并给原因；相似其他边界目标另名。run_metrics每行必须带electrical_boundary，边界多行不增加请求/run/独立样本数。矩阵logical输出路径与编号实际根目录用OUTPUT_PATH_MAP.csv/json逐项映射。

原evaluate不支持可选未使用预留slots：不使用链接适配器时，冻结实际全部执行集合；失败/缺失保留，不通过删除slot/过滤flat view伪造完整。

PCC接口补充：旧kit的power_W/baseline_W要求非负，含pcc_active，因此原接口只适合其非负输入语义；存在回送/有符号净PCC功率的设施须先明确正负方向并实现版本化且测试过的adapter/schema，不得abs、截零或删除门禁来冒充支持。旧meter import也未提供完整Q/V/I/f适配，须显式补齐。
