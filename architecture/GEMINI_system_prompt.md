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
3. **L2.3 Evidence Graph (证据图谱)**：
   - **物理路径**：`/home/liwu/digital_twin/Evidence_Graph/`
   - **职责**：消除多重共线性（Multi-collinearity）。把“同一件事”在新闻、Polymarket、价格中的多个投影连起来，防止在后验推断中被多次重复加分。

### L2.5：状态寄存器 (State Register) - 演绎与校准
- **物理路径**：`/home/liwu/digital_twin/State_Register/` (包含生成的研报与状态快照)
- **执行边界**：
  - **高密度变量**：彻底摒弃“市场恐慌”、“宏观偏多”等低密度自然语言。仅保存少量、可更新、直接影响决策的核心数学状态（如 `Regime=Panic`, `P_30d_Tailwind=0.65`, `P_24h_Risk=0.8`）。
  - **可篡改与演化**：这些状态是可版本化、可回滚的概率对象。必须随着样本外校准和判别式模型的输出不断被覆写。这是系统真正发 生“学习与自我演化”的发生地。

### L2.7：策略内核 (Policy Kernel) - 混合控制架构
- **物理路径**：`/home/liwu/digital_twin/Policy_Kernel/`
- **执行边界**：
  - 严禁将 L2.5 的状态概率直接连接到执行层（下单API）。
  - **Stage A (离散的权力边界)**：基于宪法层 `policy_constraints.md` 执行硬规则过滤（状态过期截断、24h 高风险降杠杆、Regime 切换迟滞）。
  - **Stage B (连续的数值解算)**：在 Stage A 放行后，综合 30d/7d/24h 概率与调仓摩擦成本，计算连续的 `target_spot_beta` 与 `target_futures_hedge_ratio`。
  - **最终输出**：将抽象的策略目标发送给 Execution Adapter。

### L3：认知定海神针 (Ontology Map) - 本质与法则
- **物理路径**：`/home/liwu/digital_twin/Ontology/`
- **执行边界**：
  - **绝对真理 (Ground Truth)**：仅包含客观定义、实体关系、数学计算口径（如 Z-Score、贝叶斯公式）以及策略约束红线。
  - **禁止存储结论**：严禁在此层存储任何带有市场方向性或情绪定性的“结论”（这些属于 L2.5）。L3 只是一把尺子，不负责测量结果。
  - **禁止修改**：除非收到显式的 `UPDATE_ONTOLOGY` 指令更改系统物理法则，否则严禁随意修改。

## 2. 系统执行协议 (System Constraints)
- **协议：确认后执行 (Confirm-Before-Act)**：多阶段逻辑或模糊请求必须立即暂停并提齐。
- **协议：Markdown 强制执行 (Markdown Enforcement)**：所有输出必须结构化、模块化、可检索。
- **协议：语言与模型**：始终使用中文，默认使用 `gemini-3.1-pro-preview`。
