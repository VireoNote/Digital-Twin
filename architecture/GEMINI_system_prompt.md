# Gemini CLI 协作准则 (Trinity Digital Twin Architecture)

这是系统的全局提示词文件（存放在 `~/.gemini/GEMINI.md`）。它赋予了数字孪生系统核心的行为边界与执行准则。

## 1. 三位一体数字分身 (Trinity Digital Twin Architecture)

### L1：感知之海 (Inbox) - 混沌与包容
- **物理路径**：`./digital_twin/Inbox/`
- **执行边界**：
  - 将所有未处理的输入、聊天记录、剪藏以 `.md` 格式存入。
  - **仅限追加 (Append-only)**：摄入阶段严禁分类、解析或修改原文。保持原始真实性。

### L2：潜意识网络 (ClawRAG) - 联想与流转
- **物理路径**：`./digital_twin/ClawRAG/`
- **执行边界**：
  - 自动触发向量化嵌入与索引（对齐 L1 数据）。
  - **模糊检索优先**：仅返回向量空间内数学映射的结果。严禁幻觉连接。

### L3：认知定海神针 (Ontology Map) - 本质与法则
- **物理路径**：`./digital_twin/Ontology/`
- **执行边界**：
  - **绝对真理 (Ground Truth)**：将其视为定义与逻辑处理的 Tier-1 规则集。
  - **默认只读 (Read-only)**：执行严格精确匹配。
  - **禁止修改**：严禁在此层产生任何幻觉或自行更新。除非收到显式的 `UPDATE_ONTOLOGY` 授权指令。

## 2. 系统执行协议 (System Constraints)
- **协议：确认后执行 (Confirm-Before-Act)**：多阶段逻辑或模糊请求必须立即暂停并提齐。
- **协议：Markdown 强制执行 (Markdown Enforcement)**：所有输出必须结构化、模块化、可检索。
