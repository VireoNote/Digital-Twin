# Gemini CLI 协作准则 (Trading Agent Architecture)

## 1. 系统物理分层 (Trading Agent Architecture)

### L1: Raw Events (Inbox) - Append-Only
- **物理路径**：`/home/liwu/digital_twin/Inbox/`
- **执行边界**：
  - 将所有未处理的输入、聊天记录、API 原始数据以 `.md` 格式存入。
  - **仅限追加 (Append-only)**：摄入阶段严禁分类、解析或修改原文。保持原始真实性。

### L2: Data & Feature Pipelines - 避免特征共线性
RAG 无法处理时序与因果，因此 L2 被严格拆分为三大物理组件，以防止多维度重复计价：
1. **L2.1 Text Embeddings (文本向量)**：
   - **物理路径**：`/home/liwu/digital_twin/Semantic_Memory/`
   - **职责**：仅负责新闻、文本、研报的向量化召回。
2. **L2.2 Time-Series Features (时序特征库)**：
   - **物理路径**：`/home/liwu/digital_twin/Feature_Store/`
   - **职责**：管理 WALCL, RRP, OI, Velocity 等高频数值特征，保障口径一致性与时序对齐。
3. **L2.3 Causal Graph (因果事件图谱)**：
   - **物理路径**：`/home/liwu/digital_twin/Evidence_Graph/`
   - **职责**：把在新闻、市场、价格中具有相同底层驱动的信号合并，防止同一事件权重被放大。

### L2.5: Derived State (衍生状态寄存器)
- **物理路径**：`/home/liwu/digital_twin/State_Register/` (包含生成的快照与 Schema)
- **执行边界**：
  - **强类型状态 (Typed State)**：核心状态（Regime, P_30d, P_7d, P_24h）必须符合 `typed_state.json` 格式，携带 `decay_half_life` 与 `confidence`。
  - **状态转移自检 (Transition Rules)**：状态演化必须通过 `state_transition_rules.md` 验证（如 Regime 切换强制重置旧状态的 confidence）。

### L2.7: Policy (策略控制内核)
- **物理路径**：`/home/liwu/digital_twin/Policy_Kernel/`
- **执行边界**：
  - **Stage A (离散边界)**：执行硬规则拦截（状态过期截断、24h 极端风险降杠杆、Regime 切换期迟滞）。
  - **Stage B (连续解算)**：在边界内计算 `target_spot_beta` 与 `target_futures_hedge_ratio`。
  - 严禁将 L2.5 的状态直接连到执行 API，所有状态必须经由 Policy 转换为 `Target Intent`。

### L2.8: Execution (幂等执行内核)
- **物理路径**：`/home/liwu/digital_twin/Execution_Kernel/`
- **执行边界**：
  - **目标驱动**：废除 `Buy/Sell` 动作指令。基于 `Target Exposure - Effective Position` 差值触发动作。
  - **在途折算 (Effective Position)**：按 `CONFIRMED_OPEN`、`PENDING_CANCEL` 对在途订单进行概率折算，防止网络延迟造成的错单。
  - **意图感知撤单 (Intent-Aware Cancel)**：仅撤销与当前目标方向冲突、超载或价格偏离的挂单，禁止粗暴的 Cancel All。

### L3: Constraints (规范与约束注册表)
- **物理路径**：`/home/liwu/digital_twin/Ontology/` (包含 `tier3_spec.yaml`)
- **执行边界**：
  - **静态规则引擎**：对所有动态运行的 Agent 绝对只读。
  - **允许存储 (Whitelist)**：结构化声明、数学方法论算子、系统级红线约束（最大杠杆率、逻辑互斥条件）。
  - **严禁存储 (Blacklist)**：任何方向性观点（看涨/看跌）、对当前市场状态的具体判定。

## 2. 系统执行协议 (System Constraints)
- **协议：确认后执行 (Confirm-Before-Act)**：多阶段逻辑或模糊请求必须立即暂停并提齐。
- **协议：Markdown 强制执行 (Markdown Enforcement)**：所有输出必须结构化、模块化、可检索。
- **协议：命名与风格**：必须使用工程化语言，拒绝文学修辞、哲学隐喻（如 Soul, Trinity, Sea of Perception）。
