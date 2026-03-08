# Trading Agent Architecture 4.0
### Cognition / Validation / Constitution (三位一体交易认知架构)

A constrained, multi-layer trading decision architecture where LLM owns **cognition**, data owns **validation**, and rules own **permission**.
这是一套受约束的多层交易决策架构：LLM 掌握**认知**，数据掌握**校验**，规则掌握**许可**。

---

## 1. Why 4.0 Exists (为什么存在 4.0)

Version 3.x established strong separation between layers, but suffered from LLM overreaching. 4.0 resolves this by introducing a strict **Separation of Powers**:
3.x 版本虽建立了层级隔离，但仍存在 LLM 权力过度扩张的问题。4.0 通过引入严格的**“三权分立”**来解决：

*   **Cognition Plane (认知层)**: Explains the world, but cannot directly size risk. (解释世界，但不能直接决定风险敞口)
*   **Validation Plane (校验层)**: Challenges cognition using numeric reality, but cannot invent narrative. (用数值现实质询认知，但不能虚构叙事)
*   **Constitution Plane (宪法层)**: Constrains action rights via hard rules, but cannot reinterpret reality. (通过硬性规则约束行动权，但不能重新定义现实)

---

## 2. Design Thesis (设计命题)

This system is a **Constrained Cognitive Trading Architecture** (受约束的认知交易架构). LLM-generated market hypotheses must survive numeric validation and constitutional permission checks before influencing exposure.
LLM 生成的市场假说必须在数值校验和宪法许可检查中存活下来，才被允许影响头寸。

### Core Principles (核心原则)
*   **No Direct LLM-to-Execution (禁止认知直达执行)**: LLMs must never issue physical execution instructions. (LLM 严禁发布物理执行指令)
*   **Competitive Hypotheses (竞争性假说)**: Every material thesis must face a real counter-hypothesis. (每一个核心论点都必须面对一个真实的对抗假说)
*   **Numerical Reality Overrides (数值现实覆盖权)**: A coherent story without numeric support must be downgraded. (没有数值支撑的连贯故事必须被降级)
*   **Rules Override Everything (规则至上)**: No model confidence may bypass constitutional boundaries. (任何模型信心都不得逾越宪法红线)

---

## 3. System Planes (系统维度 / Stage 0-6 流水线)

### [Stage 0] Constitution Plane (宪法层 - 权限法院)
*   **Role**: Defines what the system is allowed to do. (定义系统“准许”做什么)
*   **Logic**: Hard limits, conditional caps, and action-right rules. (硬性红线、条件限额与行动权准则)
*   **Location**: `/digital_twin/00_Constraints/`

### [Stage 1-2] Evidence Plane (证据层 - 原始感知)
*   **Role**: Stores raw evidence in append-only form. (以仅限追加的方式存储原始证据)
*   **Logic**: Preserves observed time, source lineage, and raw truth. (保留观测时间、来源溯源与原始真相)
*   **Location**: `/digital_twin/01_Ingest/` & `/digital_twin/02_Features/`

### [Stage 3] Cognition Plane (认知层 - 解释权)
*   **Role**: Transforms evidence into structured market understanding. (将证据转化为结构化的市场理解)
*   **Outputs**: `Hypothesis`, `CounterHypothesis`, `ActionIntent`.
*   **Location**: `/digital_twin/03_State/` (Cognition sub-dir)

### [Stage 3] Validation Plane (校验层 - 质询权)
*   **Role**: Challenges cognitive outputs using numeric and structural reality. (利用数值和结构化现实质询认知输出)
*   **Logic**: Emit `ValidationReport` with support/contradiction scores. (产出带有支持/矛盾分数的校验报告)
*   **Location**: `/digital_twin/03_State/` (Validation sub-dir)

### [Stage 4] Policy Compiler Plane (政策编译层 - 行动包络)
*   **Role**: Compiles cognition + validation + constitution into a bounded `PolicyEnvelope`. (将认知、校验与宪法编译成受限的行动包络)
*   **Logic**: Converts narrative conviction into allowed exposure bands (e.g., `[0.0, 0.15]`). (将叙事信心转化为被允许的敞口区间)
*   **Location**: `/digital_twin/04_Decision/`

### [Stage 5] Execution Plane (执行层 - 无状态对齐)
*   **Role**: Safely transitions from current physical state to the desired bounded state. (安全地将物理仓位过渡到目标受限状态)
*   **Logic**: Reconciliation, in-flight discounting, and idempotent execution. (仓位对齐、在途折算与幂等执行)
*   **Location**: `/digital_twin/05_Execution/`

### [Stage 6] Governance & Evaluation Plane (治理与评估层 - 影子审计)
*   **Role**: Evaluates reasoning quality and monitors drift over time. (评估推理质量并监控随时间产生的漂移)
*   **Logic**: Shadow runs, split-court frequency analysis, and model calibration. (影子运行、分裂法庭频率分析与模型校准)
*   **Location**: `/digital_twin/06_Governance/`

---

## 📊 Shadow Metrics (影子审计指标)

We monitor the "Heartbeat" of 4.0 via 6 key metrics in our **Shadow Compiler**:
我们通过影子编译器监控 4.0 的“心跳”指标：

1.  **Split Court Frequency (分裂法庭频率)**: How often validators disagree. (多路校验器意见分歧的频率)
2.  **Zero-Band Rate (零带宽率)**: Frequency of total action freeze due to risks. (因风险导致行动完全冻结的频率)
3.  **Tactical-Band Rate (战术区间率)**: Frequency of restricted, low-exposure actions. (受限、轻仓行动的频率)
4.  **Hypothesis Thrash Rate (假说震荡率)**: Frequent status flipping (e.g., Active <-> Challenged). (假说状态频繁翻转的频率)
5.  **Envelope Supersede Rate (包络覆写率)**: Frequency of version relay in policies. (政策版本接力/覆写的频率)
6.  **New-vs-Old Divergence (新旧分歧率)**: Comparison between 4.0 Shadow and Legacy Decision. (4.0 影子系统与旧决策体系的分歧对比)

---

## 🔑 Required APIs (所需 API)

| API Provider | Purpose (用途) |
| :--- | :--- |
| **FRED** | Macro Yields (TIPS, DXY, Curve) (宏观收益率) |
| **Binance / Bitget** | Derivatives OI & Market Data (衍生品与市场数据) |
| **DefiLlama** | Stablecoin Velocity (稳定币流速) |
| **OpenNews MCP** | Sentiment Alpha Factor (情绪因子) |
| **Gemini API** | Cognitive Reasoning (Hypothesis generation) (认知推理) |

---

## ⚠️ Disclaimer (免责声明)
The core idea of 4.0 is not that language models should trade. The core idea is that: **language models should interpret, data should challenge, and rules should decide what interpretation is allowed to touch risk.**
4.0 的核心思想不是让语言模型去交易，而是：**语言模型负责解释，数据负责质询，规则负责决定哪种解释可以碰触风险。**
本项目生成的任何内容均不构成投资建议。
