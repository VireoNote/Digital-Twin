# Gemini CLI 协作准则 (Trinity Digital Twin Architecture)

## 1. 三位一体数字分身 (Trinity Digital Twin Architecture)

### L1：感知之海 (Inbox) - 混沌与包容
- **物理路径**：`/home/liwu/digital_twin/Inbox/`
- **执行边界**：
  - 将所有未处理的输入、聊天记录、剪藏以 `.md` 格式存入。
  - **仅限追加 (Append-only)**：摄入阶段严禁分类、解析或修改原文。保持原始真实性。

### L2：潜意识网络 (ClawRAG) - 联想与流转
- **物理路径**：`/home/liwu/digital_twin/ClawRAG/`
- **执行边界**：
  - 自动触发向量化嵌入与索引（对齐 L1 数据）。
  - **模糊检索优先**：仅返回向量空间内数学映射的结果。严禁幻觉连接。

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
