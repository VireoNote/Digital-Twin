# Weather Station 2.0 - Trinity Digital Twin Trading Architecture

This repository hosts the source code and architectural philosophy of **Weather Station 2.0**, a highly autonomous, self-evolving digital soul and quantitative trading decision architecture built on the Gemini CLI.

This system completely abandons the traditional "multi-factor equal-weight stew" logic. Instead, it adopts a core philosophy centered on **"Frequency Isolation", "Bayesian Inference", and "Multi-Dimensional Dimensionality Reduction Strikes."**

## 🧠 Core Architecture: The Trinity Digital Twin

The system follows a three-tier evolutionary structure to ensure entropy reduction and absolute purity in decision-making:

*   **[Tier 1] The Sea of Perception (Inbox)** - Chaos and Inclusion. It ingests all raw, unpolished information fragments (API scraped data, research clippings). **Boundary:** Append-only. No modification of raw truth.
*   **[Tier 2] The Subconscious Network (ClawRAG)** - Association and Flow. Responsible for vectorized, intuitive retrieval of Tier 1 data.
*   **[Tier 3] The Cognitive Anchor (Ontology Map)** - Essence and Law. This is the "Soul" of the digital twin, recording absolute definitions of the world. **Boundary:** Ground Truth. Tampering is strictly prohibited without explicit user authorization.

---

## 📡 The Core Engine: Weather Station 2.0 Workflow

The station operates via a strict chronological and mathematical workflow, executed by 5 specialized Agents (built as Gemini CLI Skills). The workflow follows the logic of: **Base Environment -> Expectation Offset -> Dynamic Trigger**.

### Step 1: Extract the Macro Base (Low-Pass Filter / Slow Variables)
Calculates the fundamental win-rate anchor ($E_{macro}$) using Exponential Moving Averages (EMA) to filter out daily noise.
*   🌊 **Liquidity Plumbing Agent (`liquidity-plumbing`)**: Fetches FRED API for WALCL, TGA, and RRP to determine the depth of the Fed's underlying net liquidity pool.
*   🌡️ **Policy Pressure Agent (`policy-pressure`)**: Fetches DXY, TIPS, and T10Y2Y to determine the momentum of macro liquidity drains/injections and recessionary yield curve inversions.

### Step 2: Narrative Premium Offset (Expectation Variables)
*   📡 **Doppler Radar Agent (`doppler-radar`)**: Monitors Polymarket (a real-money prediction market) to scan for sudden policy shifts and macro event narrative momentum.
    *   *Algorithm*: It calculates the Narrative Premium ($\Delta E_{narrative}$) to apply a Bayesian offset to the macro base, resulting in the final **Adjusted Environment ($E_{adjusted}$)**.

### Step 3: Dynamic Trigger Authorization (High-Pass Filter / Fast Variables)
Monitors the market to find exhaustion or breakout points in sentiment. Crucially, micro variables *do not* generate buy/sell signals directly.
*   🌩️ **Crypto Extreme Weather Agent (`crypto-extreme-weather`)**: Monitors Binance Open Interest (OI) and Deribit Implied Volatility (DVOL) looking for "coiled springs" (high leverage + low protection).
*   🪙 **Crypto Micro Climate Agent (`crypto-micro`)**: Fetches DefiLlama stablecoin velocity and Yahoo Finance ETF/CME price divergence to judge whether momentum is driven by institutions or retail FOMO.
    *   *Dynamic Trigger Logic*: The threshold for micro-alerts is scaled by the macro base: $Trigger\_Threshold = T_{base} - (\beta \cdot E_{adjusted})$. In a highly accommodating macro environment, the system tolerates higher micro leverage. In a tightening environment, even slight overheating triggers an immediate short/hedge alert.

### Step 4: The Probability Matrix Output
The L3 Forecasting Center never uses absolute terms ("will pump", "must crash"). It synthesizes the 5-dimensional data into a **Probability Matrix**, outputting:
1. **Base Case** (e.g., 65% probability)
2. **Tail Risk** (e.g., 25% probability)
3. **Upside Surprise** (e.g., 10% probability)

---

## 🔑 Required APIs

To deploy this system locally, the scripts require the following APIs:

| API Provider | Purpose | Status in this Repo | Required Action |
| :--- | :--- | :--- | :--- |
| **FRED (St. Louis Fed)** | Macro Liquidity, TIPS, DXY, Yield Curve | Implemented in Python scripts | You must get a free API key and replace `YOUR_FRED_API_KEY_HERE` |
| **Binance (fAPI)** | Crypto Futures Open Interest (OI) | Implemented in Python scripts | You must get an API key and replace `YOUR_BINANCE_API_KEY_HERE` |
| **Deribit (Public)** | BTC Implied Volatility (DVOL) | Implemented (Public Endpoint) | None (No Key Required) |
| **DefiLlama** | Stablecoin Market Cap & Velocity | Implemented (Public Endpoint) | None (No Key Required) |
| **Polymarket (Gamma)** | Narrative & Expectation Pricing | Implemented (Public Endpoint) | None (No Key Required) |
| **Yahoo Finance** | ETF vs CME Divergence | Implemented (Web Fetch Simulation) | None (No Key Required) |

---
---

# 气象观测站 2.0 (Weather Station 2.0) - 三位一体数字分身交易架构

这是基于 Gemini CLI 构建的一个**高度自治、具备自我演化能力的数字灵魂与量化交易决策架构**。本系统彻底抛弃了传统的“多因子平权一锅炖”逻辑，转而采用**“频率隔离”、“贝叶斯推断”与“多维降维打击”**的核心哲学。

## 🧠 核心架构：三位一体数字分身 (Trinity Digital Twin Architecture)

系统遵循三重境界的升维演化，确保信息降熵和决策的绝对纯粹：

*   **L1：感知之海 (Inbox)** - 混沌与包容。接纳所有未经雕琢的原始信息碎片（API 抓取结果、研报剪藏）。**物理边界**：仅限追加 (Append-only)，保留真实。
*   **L2：潜意识网络 (ClawRAG)** - 联想与流转。负责对 L1 的数据进行向量化直觉检索。
*   **L3：认知定海神针 (Ontology Map)** - 本质与法则。这是数字孪生的“元神”，记录了对世界的绝对定义。**物理边界**：绝对真理 (Ground Truth)，未经显式授权禁止篡改。

---

## 📡 核心引擎：气象观测站 2.0 工作流

该观测站由 5 位专职 Agent (基于 Gemini CLI Skills 构建) 组成，严格执行时间与数学上的递进逻辑：**底色 -> 偏移 -> 扳机**。

### 步骤 1：提取宏观底色 (Low-Pass Filter / 慢变量)
通过计算指数移动平均 (EMA) 过滤日常噪音，输出系统的基础胜率锚点 ($E_{macro}$)。
*   🌊 **流动性降水专员 (`liquidity-plumbing`)**：抓取 FRED API 的 WALCL, TGA, RRP，判定美联储底层的净流动性“水池”深度。
*   🌡️ **政策气压专员 (`policy-pressure`)**：抓取 DXY, TIPS, T10Y2Y，判定“真实/虚假强美元”以及衰退倒挂传导势能。

### 步骤 2：叙事溢价补偿 (Expectation Variables / 预期变量)
*   📡 **多普勒雷达专员 (`doppler-radar`)**：监控 Polymarket 等真金白银预测市场，扫描突发政策与宏观事件的叙事动量。
    *   *核心算法*：系统计算出叙事溢价 ($\Delta E_{narrative}$) ，对宏观底色进行贝叶斯偏移，最终得出真实的**作战底色 ($E_{adjusted}$)**。

### 步骤 3：微观扳机动态授权 (High-Pass Filter / 快变量)
负责寻找情绪衰竭或爆发的临界点。最关键的是：微观指标不直接产生买卖信号。
*   🌩️ **加密雷暴预警专员 (`crypto-extreme-weather`)**：监控币安全网合约 OI 与 Deribit 隐含波动率 (DVOL)，寻找高杠杆+低保护的“压紧的弹簧”。
*   🪙 **局部微气候加密专员 (`crypto-micro`)**：抓取 DefiLlama 稳定币 Velocity 及 Yahoo Finance 的 ETF/CME 报价背离，判断主升浪是机构主导还是散户逼空。
    *   *动态阈值逻辑*：微观信号的报警阈值受宏观底色控制：$Trigger\_Threshold = T_{base} - (\beta \cdot E_{adjusted})$。宏观越宽松，系统对微观泡沫的容忍度越高；宏观越紧缩，极小的微观过热也会被系统强制触发平仓/做空警报。

### 步骤 4：概率矩阵输出
L3 预报中心在输出最终报告时，绝对禁止使用“肯定会暴跌”等一维词汇。必须将 5 维数据融合为**概率矩阵 (Probability Matrix)**，输出：
1. **当前主导情景 (Base Case)**（如 65% 概率发生）
2. **尾部风险 (Tail Risk)**（如 25% 概率发生）
3. **上行惊喜 (Upside Surprise)**（如 10% 概率发生）

---

## 🔑 所需 API 声明

如果你想在本地部署运行此系统，相关脚本依赖以下 API：

| API 提供商 | 核心用途 | 本仓库代码状态 | 操作要求 |
| :--- | :--- | :--- | :--- |
| **FRED (美联储经济数据)** | 宏观流动性、TIPS、美元指数、收益率曲线 | 已在 Python 脚本中实现 | 需要您注册获取免费 API Key，并在脚本中替换 `YOUR_FRED_API_KEY_HERE` |
| **Binance (币安 fAPI)** | 加密市场全网合约未平仓量 (OI) | 已在 Python 脚本中实现 | 需要您获取 API Key，并在脚本中替换 `YOUR_BINANCE_API_KEY_HERE` |
| **Deribit (公共接口)** | BTC 隐含波动率 (DVOL) | 已实现 (公共接口) | 无需 API Key，直接可用 |
| **DefiLlama** | 稳定币总市值与流转 | 已实现 (公共接口) | 无需 API Key，直接可用 |
| **Polymarket (Gamma API)** | 宏观叙事与预期定价 | 已实现 (公共接口) | 无需 API Key，直接可用 |
| **Yahoo Finance** | 现货 ETF 与 CME 期货溢价对比 | 已实现 (通过底层请求模拟) | 无需 API Key，直接可用 |

---
## ⚠️ 免责声明 (Disclaimer)
本项目开源的仅为**量化交易的哲学思想与工程架构实现方式**。生成的任何报告均不构成投资建议。操作风险远大于波动风险，请敬畏市场。
