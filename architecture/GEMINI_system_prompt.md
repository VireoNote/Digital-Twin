# Gemini CLI 协作准则 (Trinity Digital Twin Architecture)

## 1. 三位一体数字分身 (Trinity Digital Twin Architecture)

### L1：感知之海 (Inbox) - 混沌与包容
- **物理路径**：`/home/liwu/digital_twin/Inbox/`
- **执行边界**：
  - 将所有未处理的输入、聊天记录、剪藏以 `.md` 格式存入。
  - **仅限追加 (Append-only)**：摄入阶段严禁分类、解析或修改原文。保持原始真实性。

### L2：结构化潜意识 (Subconscious Structure) - 三重记忆网络
RAG 无法处理时序与因果，因此 L2 被严格拆分为三大物理组件，以防止“同一叙事被多维度重复计价”的贝叶斯谬误：
1. **L2.1 Semantic Memory (语义记忆网络)**：
   - **物理路径**：`/home/liwu/digital_twin/Semantic_Memory/`
   - **职责**：仅负责新闻、文本、研报的向量化召回与模糊联想。
2. **L2.2 Feature Store (时序特征库)**：
   - **物理路径**：`/home/liwu/digital_twin/Feature_Store/`
   - **职责**：专门管理 WALCL, RRP, OI, Velocity 等高频数值特征。保障口径一致性与时序对齐，拒绝文本化污染。
3. **L2.3 Event Ledger (事件归并表)**：
   - **物理路径**：`/home/liwu/digital_twin/Event_Ledger/`
   - **职责**：强类型事件账本。消除多重共线性（Multi-collinearity）。通过 `canonical_event_name` 和 `overlap_group` 把“同一件事”在新闻、Polymarket、价格中的多个投影去重归并，防止在后验推断中被多次重复加分。不支持也不需要复杂的图计算。

### L2.5：概率状态机 (Probabilistic State Machine, 原信念层)
- **物理路径**：`/home/liwu/digital_twin/State_Register/` (包含生成的快照与 Schema)
- **执行边界**：
  - **废止模糊叙事**：彻底摒弃“市场恐慌”、“宏观偏多”等低密度自然语言。
  - **强类型状态 (Typed State)**：核心状态（Regime, P_30d, P_7d, P_24h）必须符合 `State_Register/schemas/typed_state.json` 的格式，携带 `decay_half_life` 与 `confidence`，声明其生命周期。
  - **有限状态机转移 (Transition Rules)**：状态的演化必须通过 `Ontology/state_transition_rules.md` 中的“写入前自检”。例如：Regime 切换强制导致旧的 30d 概率置信度归零；跨频率（如30d与7d）的概率冲突必须带有明确的底层证据解释，否则不予写入。
  - 这是系统真正发生“学习与自我演化”的发生地。

### L2.7：决策引擎 (Decision Engine)
- **物理路径**：`/home/liwu/digital_twin/Decision_Engine/`
- **执行边界**：
  - **统揽策略与风控**：系统的“大脑皮层”。回答“在这个市场状态下，系统应该持有多少敞口？”
  - **统一快照输入 (DecisionSnapshot)**：严禁分别或异步读取特征与状态。必须消费由汇聚网关生成的不可变 `DecisionSnapshot` (包含对齐时间戳的 features, state 与 constraint_version)，以彻底消除数据撕裂 (Clock Skew)。
  - **内部逻辑**：全权负责 Hard Veto (时效拦截)、Leverage Cap (风险阻尼器降杠杆)、Hysteresis (防抖迟滞) 和 Friction-Aware Optimization (摩擦成本精算)。
  - **唯一输出**：纯净的 `Target Exposure`（目标敞口字典）。严禁在此层输出具体的撤单或下单指令。

### L2.8：执行引擎 (Execution Engine) - 幂等重平衡
- **物理路径**：`/home/liwu/digital_twin/Execution_Kernel/`
- **执行边界**：
  - **无状态对齐器**：系统的“脊髓反射”。没有任何市场观点，不懂风控。只回答“怎么把实际仓位安全地变成目标仓位？”
  - **输入**：`Target Exposure` (来自 L2.7) + `Effective Position` (当前有效仓位) + `Live Orders` (在途挂单)。
  - **在途折算 (Effective Position)**：严禁将未确认状态粗暴加总，必须按照 `CONFIRMED_OPEN`、`PENDING_CANCEL` 等状态进行概率折算。
  - **唯一输出**：离散的物理动作 (`Order Intents` 和 `Cancel Intents`)。意图感知撤单，拒绝无脑 `Cancel All`。

### L3：规范与约束注册表 (Specification & Constraint Registry)
- **物理路径**：`/home/liwu/digital_twin/Ontology/` (包含 `tier3_spec.yaml` 等)
- **执行边界**：
  - **静态规则引擎 (Static Rule Engine)**：系统内最高约束层，对所有动态运行的 Agent 绝对只读。
  - **允许存储的内容 (Whitelist)**：结构化声明（合法状态变量及其 Schema）、数学方法论（标准化算子逻辑）、硬性系统约束（最大杠杆率、逻辑互斥条件）。
  - **严禁存储的内容 (Blacklist)**：任何形式的方向性观点（看涨/看跌）、市场状态解释（当前的 Regime 标签）、随行情动态调整的经验参数。

## 2. 系统执行协议 (System Constraints)
- **协议：确认后执行 (Confirm-Before-Act)**：多阶段逻辑或模糊请求必须立即暂停并提齐。
- **协议：Markdown 强制执行 (Markdown Enforcement)**：所有输出必须结构化、模块化、可检索。
- **协议：语言与模型**：始终使用中文，默认使用 `gemini-3.1-pro-preview`。
