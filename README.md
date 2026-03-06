# Weather Station 3.2 - Trinity Digital Twin Trading Architecture

This repository hosts the source code and architectural philosophy of **Weather Station 3.2**, a highly autonomous, self-evolving digital soul and quantitative trading decision architecture built on the Gemini CLI.

This system completely abandons the traditional "multi-factor equal-weight stew" logic. Instead, it adopts a core philosophy centered on **"Frequency Isolation", "Bayesian Inference", and "Multi-Dimensional Dimensionality Reduction Strikes."**

## 🧠 Core Architecture: The Trinity Digital Twin

The system follows a strict physical hierarchy to ensure the underlying logic remains immutable, while upper-level beliefs can continuously evolve with data:

*   **[Tier 1] The Sea of Perception (Inbox)** - Chaos and Inclusion. It ingests all raw, unpolished information fragments (API scraped data, research clippings). **Boundary:** Append-only. No modification of raw truth.
*   **[Tier 2] The Subconscious Structure** - Association, Alignment, and De-biasing. A monolithic RAG is fundamentally flawed for time-series and causality. Tier 2 is split into:
    *   **Tier 2.1 Semantic Memory**: Vector DB for text, news, and narrative retrieval.
    *   **Tier 2.2 Feature Store**: Strictly manages time-series numerical features (RRP, OI, Velocity) to ensure temporal alignment and prevent LLM hallucination on numbers.
    *   **Tier 2.3 Evidence Graph**: Links different projections of the "same underlying event" (e.g., Fed cuts seen in News + Polymarket + Yields) into a single causal node, preventing catastrophic multi-counting in Bayesian inference.
*   **[Tier 2.5] The Belief Store** - Deduction and Calibration. **[Where Evolution Happens]**. Stores the system's directional conclusions and derived market states (e.g., "Macro is bullish", "Extreme panic"). **Boundary:** Beliefs are probabilistic objects. They must be continuously calibrated, overwritten, or rolled back as new Evidence arrives via Bayesian updates.
*   **[Tier 3] The Cognitive Anchor (Ontology Map)** - Essence and Law. This is the "Soul" of the digital twin. **Boundary:** Absolute Ground Truth. Tier 3 MUST ONLY store objective "Definitions", "Mathematical Methodologies" (e.g., Z-Score formulas), and "System Constraints". **It is strictly prohibited to hardcode any directional or emotional subjective conclusions (Beliefs) into Tier 3.** Tier 3 is the ruler; it does not record the length of what it measures.

---

## 📡 The Core Engine: Weather Station 3.2 Workflow

The station operates via a strict chronological and mathematical workflow, executed by 6 specialized Agents (built as Gemini CLI Skills). The workflow follows the logic of: **Base Environment -> Expectation Offset -> NLP Sentiment -> Dynamic Trigger**.

### Step 1: Extract the Macro Base (Low-Pass Filter / Slow Variables)
Calculates the fundamental win-rate anchor ($E_{macro}$) using Exponential Moving Averages (EMA) to filter out daily noise.
*   🌊 **Liquidity Plumbing Agent (`liquidity-plumbing`)**: Fetches FRED API for WALCL, TGA, and RRP to determine the depth of the Fed's underlying net liquidity pool.
*   🌡️ **Policy Pressure Agent (`policy-pressure`)**: Fetches DXY, TIPS, and T10Y2Y to determine the momentum of macro liquidity drains/injections and recessionary yield curve inversions.

### Step 2: Narrative Premium Offset (Expectation Variables)
*   📡 **Doppler Radar Agent (`doppler-radar`)**: Monitors Polymarket (a real-money prediction market) to scan for sudden policy shifts and macro event narrative momentum.

### Step 3: NLP Sentiment Alpha (Feels-like Temperature) [New in v3.2]
*   🌡️ **Feels-like Temperature Agent (`feels-like-temperature`)**: Fetches Web3 news streams via OpenNews MCP. It quantifies AI ratings and long/short signals into a continuous Alpha Factor `[-1, 1]`, acting as a final emotional reality-check against purely rational macro models.

### Step 4: Dynamic Trigger Authorization (High-Pass Filter / Fast Variables)
Monitors the market to find exhaustion or breakout points in sentiment. *Static thresholds have been completely deprecated in v3.0.*
*   🌩️ **Crypto Extreme Weather Agent (`crypto-extreme-weather`)**: Abandons absolute USD value thresholds. It now builds a Probability Model (Long Build-up vs Short Covering) by tracking **Coin-margined OI increment ($\Delta$OI)**, Price Direction, and Funding Rates. It uses **Z-Scores** over rolling windows to detect statistically significant institutional accumulation or liquidations.
*   🪙 **Crypto Micro Climate Agent (`crypto-micro`)**: Fetches DefiLlama data. It strictly rejects the illusion of total Stablecoin Market Cap, focusing instead on **Stablecoin Velocity (Daily DEX Volume / Market Cap)** to determine if the liquidity is actual purchasing power or just "dead water."

### Step 5: The Probability Matrix & Bayesian Final Directive
The L3 Forecasting Center synthesizes the 6-dimensional data using strict **Bayesian Inference** rather than linear weighted summation:
1. **Prior Probability $P(Bull)$**: Derived from the Macro Base (Step 1) and Narrative Premium (Step 2).
2. **Evidence $E$**: The current micro-state (e.g., severe OI liquidation, dead stablecoin velocity) captured by Fast Variables (Step 3 & 4).
3. **Posterior Probability $P(Bull|E)$**: The system calculates the ultimate win-rate by computing $\frac{P(E|Bull) \cdot P(Bull)}{P(E)}$. This ruthlessly corrects human bias—even if the macro is extremely bullish ($P(Bull)=0.7$), if the micro-evidence shows severe liquidity drainage, the posterior probability will plummet, preventing dangerous bottom-fishing.
4. **Kelly Criterion Mapping**: Calculates the maximum suggested risk exposure based on the Bayesian posterior win-rate.
5. **Digital Twin Final Directive**: Direct, actionable commands broken down by Spot, Longs, and Shorts.

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

---
---

# 气象观测站 3.2 (Weather Station 3.2) - 三位一体数字分身交易架构

这是基于 Gemini CLI 构建的一个**高度自治、具备自我演化能力的数字灵魂与量化交易决策架构**。本系统彻底抛弃了传统的“多因子平权一锅炖”逻辑，转而采用**“频率隔离”、“贝叶斯推断”与“多维降维打击”**的核心哲学。

## 🧠 核心架构：三位一体数字分身 (Trinity Digital Twin Architecture)

系统遵循严密的物理层级隔离，确保底层逻辑不可篡改，而上层信念可以随数据持续演化：

*   **L1：感知之海 (Inbox)** - 混沌与包容。接纳所有未经雕琢的原始信息碎片。**物理边界**：仅限追加 (Append-only)，保留真实。
*   **L2：结构化潜意识 (Subconscious Structure)** - 联想、对齐与消偏。废除单一 RAG 的黑盒（RAG 无法处理时序与因果），将其拆分为三层物理组件：
    *   **L2.1 语义记忆 (Semantic Memory)**：向量库，仅负责新闻、文本、研报的向量化召回与模糊联想。
    *   **L2.2 时序特征库 (Feature Store)**：专门管理 WALCL, RRP, OI, Velocity 等高频数值特征。保障口径一致性与时序对齐，拒绝文本化污染。
    *   **L2.3 证据图谱 (Evidence Graph)**：消除多重共线性（Multi-collinearity）。把“同一件事”在新闻、Polymarket、价格中的多个投影连起来，防止在后验推断中被多次重复加分。
*   **L2.5：信念层 (Belief Store)** - 演绎与校准。**[系统演化的发生地]**。存放系统推演出的方向性结论（如“当前宏观偏多”、“情绪极度恐慌”）。**物理边界**：信念是概率对象，随着最新证据 (Evidence) 的涌入，必须通过贝叶斯公式不断被校准、覆写、回滚。
*   **L3：认知定海神针 (Ontology Map)** - 本质与法则。这是数字孪生的“元神”。**物理边界**：绝对真理 (Ground Truth)。L3 只能存储“客观定义”、“数学口径（如 Z-Score 的计算公式）”和“系统约束红线”。**严禁将任何方向性、情绪性的主观结论（Belief）固化在 L3 中。** L3 是一把绝对的尺子，不负责记录当前测量的结果，更不可被随意篡改。

---

## 📡 核心引擎：气象观测站 3.2 工作流

该观测站由 6 位专职 Agent (基于 Gemini CLI Skills 构建) 组成，严格执行时间与数学上的递进逻辑：**底色 -> 偏移 -> 情绪 -> 扳机**。

### 步骤 1：提取宏观底色 (Low-Pass Filter / 慢变量)
通过计算指数移动平均 (EMA) 过滤日常噪音，输出系统的基础胜率锚点 ($E_{macro}$)。
*   🌊 **流动性降水专员 (`liquidity-plumbing`)**：抓取 FRED API 的 WALCL, TGA, RRP，判定美联储底层的净流动性“水池”深度。
*   🌡️ **政策气压专员 (`policy-pressure`)**：抓取 DXY, TIPS, T10Y2Y，判定“真实/虚假强美元”以及衰退倒挂传导势能。

### 步骤 2：叙事溢价补偿 (Expectation Variables / 预期变量)
*   📡 **多普勒雷达专员 (`doppler-radar`)**：利用 Polymarket `/events` 接口，监控交易量超百万美金的突发宏观事件，提取高能叙事溢价。

### 步骤 3：情绪偏移 (Sentiment Alpha / 体感变量) [v3.2 新增]
*   🌡️ **体感温度专员 (`feels-like-temperature`)**：基于 OpenNews MCP 抓取全网资讯并量化 AI 评级与多空信号，转化为连续的 Alpha 因子 ([-1, 1])。作为对纯理性宏观模型的感性校验，防止忽略极端的 FOMO 或恐慌踩踏。

### 步骤 4：微观扳机动态授权 (High-Pass Filter / 快变量)
**[v3.0 重大升级]：彻底废除静态绝对值阈值。**
*   🌩️ **加密雷暴预警专员 (`crypto-extreme-weather`)**：摒弃 U 本位假象。严格使用 **币本位 OI 增量 + 价格方向 + 资金费率** 构建多空行为概率模型（精准区分“多头建仓”与“空头回补”）。利用 1H/4H 的百分比及 14天 **Z-Score** 捕捉具备统计学意义的主力异动。
*   🪙 **局部微气候加密专员 (`crypto-micro`)**：摒弃稳定币总市值的刻舟求剑，专注于测算真实的 **日换手流速 (Velocity = DEX Volume / Market Cap)**。结合流速 Z-Score 判断目前场内资金是“死水沉淀”还是“健康活跃”。

### 步骤 5：贝叶斯后验矩阵与终极指令
L3 预报中心彻底摒弃线性加权求和，必须通过**贝叶斯公式**完成 6 维数据的降维打击：
1. **先验概率 $P(Bull)$**：由宏观底色（慢变量）与叙事溢价（预期变量）得出基础多头胜率。
2. **观测证据 $E$**：由体感温度专员和雷暴预警专员抓取到的最新微观异动（如：剧烈的多头踩踏、流速枯竭等）。
3. **后验概率 $P(Bull|E)$**：计算 $\frac{P(E|Bull) \cdot P(Bull)}{P(E)}$。利用此公式对抗人性偏见——即使宏观再好 ($P(Bull)=0.7$)，只要微观出现了极其恶劣的流动性断裂，贝叶斯公式也会冷酷地将最终胜率暴降，压制抄底冲动。
4. **凯利公式仓位映射 (Kelly Criterion)**：根据贝叶斯后验胜率，计算出严谨的最高头寸风险敞口。
5. **数字分身终极操作建议**：向现货、多头、空头三种仓位下达干脆的交易动作指令。

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

---
## ⚠️ 免责声明 (Disclaimer)
本项目开源的仅为**量化交易的哲学思想与工程架构实现方式**。生成的任何报告均不构成投资建议。操作风险远大于波动风险，请敬畏市场。