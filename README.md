# Trading Agent Architecture 4.0
### Cognition / Validation / Constitution

---

## [English Version]

### 1. Architectural Philosophy
A constrained, multi-layer trading decision architecture where:
*   **LLM owns Cognition**: Explains the world, but cannot directly size risk.
*   **Data owns Validation**: Challenges cognition using numeric reality, but cannot invent narrative.
*   **Rules own Permission**: Constrains action rights via hard rules, but cannot reinterpret reality.

### 2. Design Thesis
This system is a **Constrained Cognitive Trading Architecture**. LLM-generated market hypotheses must survive numeric validation and constitutional permission checks before being allowed to influence portfolio exposure.

**Core Principles:**
*   **No Direct LLM-to-Execution**: LLMs are strictly forbidden from issuing physical execution instructions.
*   **Evidence Traceability**: Every high-level object must be traceable to raw EvidenceRecords.
*   **Competitive Hypotheses**: Every material thesis must face a real counter-hypothesis.
*   **Numerical Reality Overrides**: A coherent story without numeric support must be downgraded.
*   **Rules Override Everything**: No narrative quality or model confidence may bypass constitutional boundaries.

### 3. System Planes (Stage 0-6 Pipeline)
*   **[Stage 0] Constitution Plane**: Defines what the system is allowed to do (Hard limits, action-right rules).
*   **[Stage 1-2] Evidence Plane**: Stores raw evidence in append-only form (Source lineage, raw truth).
*   **[Stage 3] Cognition Plane**: Transforms evidence into structured understanding (`Hypothesis`, `ActionIntent`).
*   **[Stage 3] Validation Plane**: Challenges cognition using numeric and structural reality (`ValidationReport`).
*   **[Stage 4] Policy Compiler Plane**: Compiles cognition + validation + rules into a bounded `PolicyEnvelope`.
*   **[Stage 5] Execution Plane**: Safely transitions physical state to the desired bounded state (Reconciliation).
*   **[Stage 6] Governance Plane**: Evaluates reasoning quality and monitors drift (Shadow Metrics).

### 4. Shadow Heartbeat Metrics
We monitor the system's "Heartbeat" via 6 key metrics:
1.  **Split Court Frequency**: How often validators disagree.
2.  **Zero-Band Rate**: Frequency of total action freeze due to risks.
3.  **Tactical-Band Rate**: Frequency of restricted, low-exposure actions.
4.  **Hypothesis Thrash Rate**: Frequency of status flipping (e.g., Active <-> Challenged).
5.  **Envelope Supersede Rate**: Frequency of policy version relay.
6.  **New-vs-Old Divergence**: Comparison between 4.0 Shadow and Legacy Decision.

---

## [中文版]

### 1. 核心架构哲学：三权分立
这是一套受约束的多层交易决策架构，核心原则如下：
*   **LLM 拥有认知权 (Cognition)**：负责解释世界，生成假说，但严禁直接决定风险敞口尺寸。
*   **数据拥有校验权 (Validation)**：负责利用数值现实对认知进行质询，但严禁捏造叙事。
*   **规则拥有许可权 (Constitution)**：负责通过硬性红线约束行动权，但严禁重新定义现实。

### 2. 设计命题
本系统是一套**受约束的认知交易架构**。LLM 生成的市场假说必须在数值校验层和宪法许可检查中存活下来，才被允许转化为实际头寸。

**核心原则：**
*   **禁止认知直达执行**：LLM 严禁发布任何物理执行指令。
*   **证据可追溯性**：所有高层认知对象都必须可追溯至原始证据记录 (EvidenceRecords)。
*   **竞争性假说**：每一个核心论点都必须面对一个真实的对抗性反方假说。
*   **数值现实覆盖权**：没有数值支撑的连贯故事必须被降级或否决。
*   **规则至上**：任何模型信心或叙事质量都不得逾越宪法红线。

### 3. 系统维度 (Stage 0-6 流水线)
*   **[Stage 0] 宪法层 (Constitution Plane)**：权限法院。定义系统“准许”做什么（硬性红线、行动权准则）。
*   **[Stage 1-2] 证据层 (Evidence Plane)**：原始感知。以仅限追加的方式存储原始证据（保留来源溯源与原始真相）。
*   **[Stage 3] 认知层 (Cognition Plane)**：解释权。将证据转化为结构化的市场理解（假说、行动意图）。
*   **[Stage 3] 校验层 (Validation Plane)**：质询权。利用数值现实质询认知输出（产出校验报告）。
*   **[Stage 4] 政策编译层 (Policy Compiler)**：行动包络。将认知、校验与宪法编译成受限的 `PolicyEnvelope`。
*   **[Stage 5] 执行层 (Execution Plane)**：无状态对齐。安全地将物理仓位过渡到目标受限状态（在途折算）。
*   **[Stage 6] 治理层 (Governance Plane)**：影子审计。评估推理质量并监控随时间产生的漂移。

### 4. 影子审计：六大“心跳”指标
我们通过影子编译器实时监控 4.0 的系统健康度：
1.  **分裂法庭频率 (Split Court Frequency)**：多路校验器意见分歧的频率。
2.  **零带宽率 (Zero-Band Rate)**：因风险导致行动完全冻结的频率。
3.  **战术区间率 (Tactical-Band Rate)**：受限、轻仓试探性行动的频率。
4.  **假说震荡率 (Hypothesis Thrash Rate)**：假说状态频繁翻转（如 Active <-> Challenged）的频率。
5.  **包络覆写率 (Envelope Supersede Rate)**：政策版本接力/覆写发生的频率。
6.  **新旧分歧率 (New-vs-Old Divergence)**：4.0 影子系统与旧决策体系的结论差异率。

---

## ⚠️ Disclaimer (免责声明)
The core idea of 4.0 is not that language models should trade. The core idea is that: **language models should interpret, data should challenge, and rules should decide what interpretation is allowed to touch risk.**
4.0 的核心思想不是让语言模型去交易，而是：**语言模型负责解释，数据负责质询，规则负责决定哪种解释可以碰触风险。**
本项目生成的任何内容均不构成投资建议。
