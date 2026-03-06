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

### L2.5：信念层 (Belief Store) - 演绎与校准
- **物理路径**：`/home/liwu/digital_twin/Beliefs/` (包含生成的研报与状态快照)
- **执行边界**：
  - **概率对象**：存储所有关于市场状态的“方向判断”、“情绪定性”（如“真实强美元”、“宏观偏多”、“极度恐慌”）。
  - **可篡改与演化**：信念是可版本化、可回滚、可随贝叶斯后验不断校准的概率对象。这是系统真正发生“学习与自我演化”的发生地。

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
