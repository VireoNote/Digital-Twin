# Trading Agent Architecture 3.8

This repository hosts the source code and architectural philosophy of **Weather Station 3.8**, a highly autonomous, self-evolving automated agent and quantitative trading decision architecture built on the Gemini CLI.

This system completely abandons the traditional "multi-factor equal-weight stew" logic. Instead, it adopts a core philosophy centered on **"Frequency Isolation", "Bayesian Inference", and "Multi-Dimensional Dimensionality Reduction Strikes."**

## 🧠 Core Architecture: System Architecture

The system follows a strict physical hierarchy to ensure the underlying logic remains immutable, while upper-level beliefs can continuously evolve with data:

*   **[Tier 1] The Raw Events (L1)** - Chaos and Inclusion. It ingests all raw, unpolished information fragments (API scraped data, research clippings). **Boundary:** Append-only. No modification of raw truth.
*   **[Tier 2] The Data & Feature Pipelines (L2)** - Association, Alignment, and De-biasing. A monolithic RAG is fundamentally flawed for time-series and causality. Tier 2 is split into:
    *   **Tier 2.1 Text Embeddings**: Vector DB for text, news, and narrative retrieval.
    *   **Tier 2.2 Time-series Features**: Strictly manages time-series numerical features (RRP, OI, Velocity) to ensure temporal alignment and prevent LLM hallucination on numbers.
    *   **Tier 2.3 Event Ledger**: A typed event ledger using `canonical_event_name` and `overlap_group` to deduplicate and merge projections of the "same underlying event" across News, Polymarket, and Yields, preventing multi-counting in inference. Replaces graph-based paradigms with a flat relational schema.
*   **[Tier 2.5] The Derived State (L2.5)** - Deduction and Calibration. **[Where Evolution Happens]**. It explicitly rejects low-density natural language narratives (e.g., "Market nervous", "Macro bullish"). Instead, it acts as a high-density register holding a small set of mutable, mathematical state variables (e.g., `Regime=Loose_Fragile`, `P_30d=0.65`, `P_24h_Risk=0.8`). **Boundary:** These are probabilistic objects that are continuously overwritten or rolled back as new Evidence arrives via out-of-sample calibration.
*   **[Tier 2.7] The Policy Kernel (Hybrid Control Architecture)** - **[New in v3.6]**. Converts continuous cognitive probabilities into discrete target exposures. It operates a hybrid model:
*   **[Tier 2.8] The Execution Kernel (Idempotent Rebalance Cycle)** - **[New in v3.7]**. Replaces direct action commands (Buy/Sell) with a state-reconciliation engine.
    *   **Intent-Driven**: Operates strictly on `Target Exposure - Effective Position`.
    *   **In-flight Discounting**: Calculates `EffectivePosition` by discounting pending orders based on their state to prevent over-trading during network latency.
    *   **Intent-Aware Cancel**: Surgically cancels only stale or conflicting orders rather than a blind 'Cancel All', preserving API limits and orderbook priority.
    *   **Stage A (Discrete Power Boundaries)**: Enforces non-negotiable institutional rules (e.g., Validity Kill Switch, 24h Risk Damper, Regime Hysteresis). Has absolute veto power.
    *   **Stage B (Continuous Optimization)**: If Stage A permits, it calculates the optimal `target_spot_beta`, `target_futures_hedge_ratio`, and `max_gross_leverage` based on 30d/7d signals and friction costs.
*   **[Tier 3] The Constraints & Specifications (L3)** - The immutable global configuration and hard boundary layer. **Boundary:** Read-only for all operational agents. Tier 3 MUST ONLY store structural declarations (e.g., allowed state variables and their schemas), mathematical methodologies (e.g., specific Z-Score calculation logic), and strict system constraints (e.g., `max_gross_leverage`, validity decay rules). **It is strictly prohibited to store any directional market beliefs, current regime interpretations, or dynamic empirical thresholds in this tier.** Tier 3 operates as the static rule engine defining what is mathematically and logically permissible within the system.

---

## 📡 The Core Engine: Data Pipeline Workflow

The station operates via a strict chronological and mathematical workflow, executed by 6 specialized Agents (built as Gemini CLI Skills). The workflow follows the logic of: **Base Environment -> Expectation Offset -> NLP Sentiment -> Dynamic Trigger**.

### Step 1: Extract the Macro Base (Low-Pass Filter / Slow Variables)
Calculates the fundamental win-rate anchor ($E_{macro}$) using Exponential Moving Averages (EMA) to filter out daily noise.
*   🌊 **Liquidity Plumbing Agent (`liquidity-plumbing`)**: Fetches FRED API for WALCL, TGA, and RRP to determine the depth of the Fed's underlying net liquidity pool.
*   🌡️ **Policy Pressure Agent (`policy-pressure`)**: Fetches DXY, TIPS, and T10Y2Y to determine the momentum of macro liquidity drains/injections and recessionary yield curve inversions.

### Step 2: Narrative Premium Offset (Expectation Variables)
*   📡 **Doppler Radar Agent (`doppler-radar`)**: Monitors Polymarket (a real-money prediction market) to scan for sudden policy shifts and macro event narrative momentum.

### Step 3: NLP Sentiment Alpha (Feels-like Temperature) [New in v3.4]
*   🌡️ **Feels-like Temperature Agent (`feels-like-temperature`)**: Fetches Web3 news streams via OpenNews MCP. It quantifies AI ratings and long/short signals into a continuous Alpha Factor `[-1, 1]`, acting as a final emotional reality-check against purely rational macro models.

### Step 4: Dynamic Trigger Authorization (High-Pass Filter / Fast Variables)
Monitors the market to find exhaustion or breakout points in sentiment. *Static thresholds have been completely deprecated in v3.0.*
*   🌩️ **Crypto Extreme Weather Agent (`crypto-extreme-weather`)**: Abandons absolute USD value thresholds. It now builds a Probability Model (Long Build-up vs Short Covering) by tracking **Coin-margined OI increment ($\Delta$OI)**, Price Direction, and Funding Rates. It uses **Z-Scores** over rolling windows to detect statistically significant institutional accumulation or liquidations.
*   🪙 **Crypto Micro Climate Agent (`crypto-micro`)**: Fetches DefiLlama data. It strictly rejects the illusion of total Stablecoin Market Cap, focusing instead on **Stablecoin Velocity (Daily DEX Volume / Market Cap)** to determine if the liquidity is actual purchasing power or just "dead water."

### Step 5: Critical Execution Path & Audit View
The system strictly separates the physical execution path from human-readable environmental interpretations. The "View Layer" is explicitly demoted to a pure logging/audit artifact and does NOT participate in the control loop.

**The Critical Execution Path:**
The system logic strictly flows via: `Features (L2) ➡️ Derived State (L2.5) ➡️ Policy Target Exposure (L2.7) ➡️ Idempotent Execution (L2.8)`.
1. **$P_{30d\_Tailwind}$ ➡️ Spot Base Exposure**: Dictates the core baseline direction.
2. **$P_{7d\_Continuation}$ ➡️ Mid-term Hedging**: Dictates the offensive/defensive tilt.
3. **$P_{24h\_Adverse\_Risk}$ ➡️ Risk Gate & Circuit Breaker**: The highest priority defense. Triggers L2.7 Risk Damper to force leverage cuts.

**The Audit View (Not in Critical Path):**
1. **Regime Synthesis**: Determines the current "Regime Tag" (e.g., `Loose Liquidity but Fragile`) for human auditing.
2. **Scenario Planning**: Outlines the Base Case and Tail Risks for logging purposes.

**Engineering Pillars:**
*   **Regime Gate**: Models are *Regime-aware*. A separate module (e.g., HMM) acts purely as a "Regime Classifier" (e.g., `Loose Liquidity`, `Panic`), routing samples or altering conditional mappings rather than issuing direct trade signals.
*   **Empirical Bayes Shrinkage**: Bayes is demoted from a global framework to a robust tool for sparse statistics. It uses Beta-Binomial shrinkage to prevent overconfidence in rare buckets (e.g., historically rare combinations of high funding and low volume).
*   **Collinearity Control**: Evidence overlap is managed at the feature level via `overlap_groups`, aggregation, or monotonic constraints, NOT by hacking posterior probabilities.

---

## 🔑 Required APIs

To deploy this system locally, the scripts require the following APIs:

| API Provider | Purpose | Status in this Repo | Required Action |
| :--- | :--- | :--- | :--- |
| **FRED (St. Louis Fed)** | Macro Liquidity, TIPS, DXY, Yield Curve | Implemented in Python scripts | You must get a free API key |
| **Binance (fAPI)** | Crypto Futures Open Interest (OI) | Implemented in Python scripts | You must get an API key |
| **Deribit (Public)** | BTC Implied Volatility (DVOL) | Implemented (Public Endpoint) | None (No Key Required) |
| **DefiLlama** | Stablecoin Market Cap & DEX Volume | Implemented (Public Endpoint) | None (No Key Required) |
| **Polymarket (Gamma API)**| Macro Narrative Pricing | Implemented (Public Endpoint) | None (No Key Required) |
| **OpenNews MCP** | NLP Sentiment AI Analysis | Implemented via `feels-like-temperature` | You must get a 6551.io API Token |
| **Bitget MCP Server** | Physical Trade Execution | Integrated via `bitget-mcp-server` | Configure API Key/Secret/Passphrase in Gemini CLI MCP |

---
---

# 气象观测站 3.8 (Weather Station 3.8) - 三位一体数字分身交易架构

这是基于 Gemini CLI 构建的一个**高度自治、具备自我演化能力的数字灵魂与量化交易决策架构**。本系统彻底抛弃了传统的“多因子平权一锅炖”逻辑，转而采用**“频率隔离”、“贝叶斯推断”与“多维降维打击”**的核心哲学。

## 🧠 核心架构：三位一体数字分身 (Trinity Digital Twin Architecture)

系统遵循严密的物理层级隔离，确保底层逻辑不可篡改，而上层信念可以随数据持续演化：

*   **L1：感知之海 (Inbox)** - 混沌与包容。接纳所有未经雕琢的原始信息碎片。**物理边界**：仅限追加 (Append-only)，保留真实。
*   **L2：结构化潜意识 (Subconscious Structure)** - 联想、对齐与消偏。废除单一 RAG 的黑盒（RAG 无法处理时序与因果），将其拆分为三层物理组件：
    *   **L2.1 语义记忆 (Semantic Memory)**：向量库，仅负责新闻、文本、研报的向量化召回与模糊联想。
    *   **L2.2 时序特征库 (Feature Store)**：专门管理 WALCL, RRP, OI, Velocity 等高频数值特征。保障口径一致性与时序对齐，拒绝文本化污染。
    *   **L2.3 事件归并表 (Event Ledger)**：强类型事件账本。消除多重共线性（Multi-collinearity）。通过 `canonical_event_name` 和 `overlap_group` 把“同一件事”在新闻、Polymarket、价格中的多个投影去重归并，防止在后验推断中被多次重复加分。不支持也不需要复杂的图计算。
*   **L2.5：状态寄存器 (State Register, 原信念层)** - 演绎与校准。**[系统演化的发生地]**。彻底摒弃“市场恐慌”、“宏观向好”等低密度、易重复的自然语言叙事。它是一个高密度的变量寄存器，仅保存少量、可更新、直接影响决策的核心数学状态（如 `Regime=Loose_Fragile`, `P_30d_Tailwind=0.65`, `P_24h_Risk=0.8`）。**物理边界**：这些状态是概率对象，随着最新观测证据的涌入，必须不断被严格覆盖、校准或回滚。
*   **L2.7：策略内核 (Policy Kernel)** - **[v3.6 新增：混合控制架构]**。作为信念层与执行层之间的隔离转换器，解决“连续认知概率”与“离散执行动作”的映射问题。
*   **L2.8：执行内核 (Execution Kernel)** - **[v3.7 新增：幂等重平衡]**。彻底废除“买入/卖出”动作指令，转向“状态对齐 (State Reconciliation)”。
    *   **在途折算 (Effective Position)**：严禁将未确认状态粗暴加总，根据订单生命周期（已提交、已挂单、撤销中）进行概率折算，防止网络延迟导致的反向或重复发单。
    *   **意图感知撤单 (Intent-Aware Cancel)**：废除粗暴的批量撤单，仅外科手术式撤销与当前目标方向相反、尺寸超载或价格偏离的冲突订单。
    *   **Stage A (离散权力边界)**：执行不可商量的制度红线（如状态过期截断、24h 高风险强制降杠杆、Regime 切换迟滞窗）。一票否决。
    *   **Stage B (连续数值解算)**：在边界内，综合 30d/7d/24h 概率与摩擦成本，计算最优的 `target_spot_beta` 与 `target_futures_hedge_ratio`。
*   **L3：规范与约束注册表 (Specification & Constraint Registry)** - 不可变的全局配置与强边界层。**物理边界**：对所有动态运行的 Agent 绝对只读。L3 必须且只能存储结构化声明（如合法的状态变量及 Schema）、数学方法论（如特定 Z-Score 计算逻辑）以及硬性系统约束（如 `max_gross_leverage`、状态衰减规则）。**严禁在此层存储任何方向性市场观点、当前 Regime 状态解释或动态经验阈值。** L3 作为静态规则引擎，定义系统内什么是数学和逻辑上被允许的。

---

## 📡 核心引擎：气象观测站 3.8 工作流

该观测站由 6 位专职 Agent (基于 Gemini CLI Skills 构建) 组成，严格执行时间与数学上的递进逻辑：**底色 -> 偏移 -> 情绪 -> 扳机**。

### 步骤 1：提取宏观底色 (Low-Pass Filter / 慢变量)
通过计算指数移动平均 (EMA) 过滤日常噪音，输出系统的基础胜率锚点 ($E_{macro}$)。
*   🌊 **流动性降水专员 (`liquidity-plumbing`)**：抓取 FRED API 的 WALCL, TGA, RRP，判定美联储底层的净流动性“水池”深度。
*   🌡️ **政策气压专员 (`policy-pressure`)**：抓取 DXY, TIPS, T10Y2Y，判定“真实/虚假强美元”以及衰退倒挂传导势能。

### 步骤 2：叙事溢价补偿 (Expectation Variables / 预期变量)
*   📡 **多普勒雷达专员 (`doppler-radar`)**：利用 Polymarket `/events` 接口，监控交易量超百万美金的突发宏观事件，提取高能叙事溢价。

### 步骤 3：情绪偏移 (Sentiment Alpha / 体感变量) [v3.4 新增]
*   🌡️ **体感温度专员 (`feels-like-temperature`)**：基于 OpenNews MCP 抓取全网资讯并量化 AI 评级与多空信号，转化为连续的 Alpha 因子 ([-1, 1])。作为对纯理性宏观模型的感性校验，防止忽略极端的 FOMO 或恐慌踩踏。

### 步骤 4：微观扳机动态授权 (High-Pass Filter / 快变量)
**[v3.0 重大升级]：彻底废除静态绝对值阈值。**
*   🌩️ **加密雷暴预警专员 (`crypto-extreme-weather`)**：摒弃 U 本位假象。严格使用 **币本位 OI 增量 + 价格方向 + 资金费率** 构建多空行为概率模型（精准区分“多头建仓”与“空头回补”）。利用 1H/4H 的百分比及 14天 **Z-Score** 捕捉具备统计学意义的主力异动。
*   🪙 **局部微气候加密专员 (`crypto-micro`)**：摒弃稳定币总市值的刻舟求剑，专注于测算真实的 **日换手流速 (Velocity = DEX Volume / Market Cap)**。结合流速 Z-Score 判断目前场内资金是“死水沉淀”还是“健康活跃”。

### 步骤 5：核心控制链路与审计视图
系统明确将“关键交易路径”与“人类可读的环境解释”进行物理隔离。**“观点层 (View Layer)”被彻底降级为纯粹的日志与审计输出，不参与任何实际的控制闭环**。

**核心控制链路 (The Critical Execution Path)：**
交易决策严格遵循单向物理链路：`特征 (L2) ➡️ 衍生状态 (L2.5) ➡️ 策略目标敞口 (L2.7) ➡️ 幂等执行 (L2.8)`。
1. **战略底仓 ($P_{30d\_Tailwind}$)**：决定核心现货的基准暴露方向与最大风险预算。
2. **中期倾斜 ($P_{7d\_Continuation}$)**：决定波段仓位的攻防倾斜与衍生品对冲比例。
3. **风险闸门 ($P_{24h\_Adverse\_Risk}$)**：最高优先级防守。高风险时直接触发 L2.7 阻尼器，强制收缩杠杆。

**审计视图 (The Audit View - 不参与执行)：**
1. **Regime 状态定调**：生成用于人类复盘审计的绝对“天气标签”（如：宽裕但极度脆弱）。
2. **情景沙盘推演**：概述基准情景与尾部风险，仅作为运行日志写入。

**三大工程支柱：**
*   **Regime Gate (环境门卫)**：HMM 等状态机退居幕后，只提供“天气标签”，让主模型成为 *Regime-aware*，在不同天气下采用不同的条件概率映射，而不直接发号施令。
*   **经验贝叶斯收缩 (Empirical Bayes Shrinkage)**：贝叶斯从“全局推导口号”退回到“局部稀疏统计工具”。使用 Beta-Binomial 收缩防止系统在遭遇历史罕见切片（Rare Bucket）时过度自信。
*   **特征层共线性管制 (Collinearity Control)**：废除在后验层硬相乘的逻辑。通过 `overlap_group` 打标，在特征进入模型前执行分组聚合或限额，显著降低冗余证据对同一叙事的重复放大。

---

## 🔑 所需 API 声明

如果你想在本地部署运行此系统，相关脚本依赖以下 API：

| API 提供商 | 核心用途 | 本仓库代码状态 | 操作要求 |
| :--- | :--- | :--- | :--- |
| **FRED (美联储经济数据)** | 宏观流动性、TIPS、美元指数、收益率曲线 | 已在 Python 脚本中实现 | 需要获取免费 API Key |
| **Binance (币安 fAPI)** | 加密市场全网合约未平仓量 (OI) 等 | 已在 Python 脚本中实现 | 需要获取 API Key |
| **Deribit (公共接口)** | BTC 隐含波动率 (DVOL) | 已实现 (公共接口) | 无需 API Key |
| **DefiLlama** | 稳定币总市值与 DEX 真实交易量 | 已实现 (公共接口) | 无需 API Key |
| **Polymarket (Gamma API)** | 宏观叙事与预期定价 | 已实现 (公共接口) | 无需 API Key |
| **OpenNews MCP** | NLP 情绪 Alpha 提取 | 已通过 `fetch_sentiment.py` 实现 | 需要配置 `OPENNEWS_TOKEN` |
| **Bitget MCP Server** | 物理级自动化交易执行 | 已通过 `bitget-mcp-server` 接入 | 需要在 Gemini CLI 中配置 API Key/Secret/Passphrase |

---
## ⚠️ 免责声明 (Disclaimer)
本项目开源的仅为**量化交易的哲学思想与工程架构实现方式**。生成的任何报告均不构成投资建议。操作风险远大于波动风险，请敬畏市场。