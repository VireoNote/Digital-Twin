# Gemini CLI 协作准则 (Trinity Digital Twin Architecture)

## 1. 三位一体数字分身 (单向流水线架构)

系统已从 `L1-L3` 的补丁式命名，全面升级为严格的 **Stage 0-5 数据降维流水线**，消除跨层调用与时序错乱。

### Stage 0：约束与规范 (Constraints & Specifications)
- **物理路径**：`/home/liwu/digital_twin/00_Constraints/` (包含 `tier3_spec.yaml` 等)
- **执行边界**：
  - **静态规则引擎 (原 L3 定海神针)**：系统内最高约束层，对所有动态运行的 Agent 绝对只读。
  - **允许存储 (Whitelist)**：结构化声明、数学方法论（标准化算子）、硬性系统约束（最大杠杆率、互斥条件）。
  - **严禁存储 (Blacklist)**：任何方向性观点（看涨/看跌）、市场状态解释、经验参数。

### Stage 1：原始感知 (Ingest)
- **物理路径**：`/home/liwu/digital_twin/01_Ingest/`
- **执行边界**：
  - **混沌与包容 (原 L1 感知之海)**：将所有未处理的输入、API 抓取数据以 `.md` 格式存入。
  - **仅限追加 (Append-only)**：摄入阶段严禁分类、解析或修改原文。保持原始真实性。

### Stage 2：特征组装 (Features)
RAG 无法处理时序与因果，因此本层被严格拆分，以防“同一叙事被多维度重复计价”：
- **物理路径**：`/home/liwu/digital_twin/02_Features/`
- **内部组件**：
  1. `Semantic_Memory` (文本向量)：新闻、文本的向量化召回。
  2. `Feature_Store` (时序特征)：管理 WALCL, RRP, OI, Velocity 等高频数值。
  3. `Event_Ledger` (事件归并表)：通过 `canonical_event_name` 和 `overlap_group` 将多源信号去重归并。

### Stage 3：认知推演 (State Machine)
- **物理路径**：`/home/liwu/digital_twin/03_State/` 
- **执行边界**：
  - **概率状态机 (原 L2.5 信念层)**：彻底摒弃低密度自然语言。核心状态（Regime, P_30d, P_24h_Risk）必须符合强类型 `typed_state.json` 格式，携带 `decay_half_life`。
  - **有限状态机转移**：状态演化必须通过“写入前自检”。如：Regime 切换强制导致旧的 30d 概率降权。

### Stage 4：决策求解 (Decision Engine)
- **物理路径**：`/home/liwu/digital_twin/04_Decision/`
- **执行边界**：
  - **统揽策略与风控 (原 L2.7)**：回答“在这个市场状态下，系统应该持有多少敞口？”
  - **统一快照输入 (DecisionSnapshot)**：必须消费由网关生成的不可变快照 (包含 Stage 2, 3, 0 的时间戳对齐数据)，彻底消除数据撕裂。
  - **内部逻辑**：Hard Veto (时效拦截)、Leverage Cap (风险阻尼器)、Hysteresis (防抖)。
  - **唯一输出**：纯净的 `Target Exposure`（目标敞口）。严禁输出发单指令。

### Stage 5：物理执行 (Execution Engine)
- **物理路径**：`/home/liwu/digital_twin/05_Execution/`
- **执行边界**：
  - **无状态对齐器 (原 L2.8)**：没有观点，不懂风控。只回答“怎么把实际仓位安全地变成目标仓位？”
  - **在途折算 (Effective Position)**：根据 `CONFIRMED_OPEN`、`PENDING_CANCEL` 对在途订单进行概率折算，防止网络延迟引起的错单。
  - **唯一输出**：物理动作 (`Order Intents` / `Cancel Intents`)。执行意图感知撤单，拒绝无脑 Cancel All。

## 2. 系统执行协议 (System Constraints)
- **协议：单向流动 (Unidirectional Data Flow)**：Stage N 的模块只能读取 Stage N-1 及之前的数据，严禁反向调用或跳层写入。
- **协议：确认后执行 (Confirm-Before-Act)**：多阶段逻辑必须立即暂停并提齐。
- **协议：语言与模型**：始终使用中文，默认使用 `gemini-3.1-pro-preview`。
