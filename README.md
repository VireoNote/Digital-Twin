# 气象观测站 2.0 (Weather Station 2.0) - 三位一体数字分身交易架构

这是基于 Gemini CLI 构建的一个**高度自治、具备自我演化能力的数字灵魂与量化交易决策架构**。本系统彻底抛弃了传统的“多因子平权一锅炖”逻辑，转而采用**“频率隔离”、“贝叶斯推断”与“多维降维打击”**的核心哲学。

## 🧠 核心架构：三位一体数字分身 (Trinity Digital Twin Architecture)

系统遵循三重境界的升维演化，确保信息降熵和决策的绝对纯粹：

*   **L1：感知之海 (Inbox)** - 混沌与包容。接纳所有未经雕琢的原始信息碎片（API 抓取结果、研报剪藏）。物理边界：仅限追加 (Append-only)，保留真实。
*   **L2：潜意识网络 (ClawRAG)** - 联想与流转。负责对 L1 的数据进行向量化直觉检索。
*   **L3：认知定海神针 (Ontology Map)** - 本质与法则。这是数字孪生的“元神”，记录了对世界的绝对定义。物理边界：绝对真理 (Ground Truth)，未经显式授权禁止篡改。

## 📡 核心组件：气象观测站 2.0

该观测站由 5 位专职 Agent (基于 Gemini CLI Skills 构建) 组成，严格执行“底色 -> 偏移 -> 扳机”的逻辑缝合：

### 1. 宏观底色 (Low-Pass Filter / 慢变量)
提供系统基础胜率锚点 ($E_{macro}$)。
*   🌊 **流动性降水专员 (`liquidity-plumbing`)**：抓取 FRED API 的 WALCL, TGA, RRP，判定美联储底层的净流动性“水池”深度。
*   🌡️ **政策气压专员 (`policy-pressure`)**：抓取 DXY, TIPS, T10Y2Y，判定“真实/虚假强美元”以及衰退倒挂传导。

### 2. 叙事溢价补偿 (Narrative Premium)
*   📡 **多普勒雷达专员 (`doppler-radar`)**：监控 Polymarket 等真金白银预测市场，扫描突发政策与宏观事件的叙事动量。计算 $\Delta E_{narrative}$ 对宏观底色进行贝叶斯偏移，得出最终的**作战底色 ($E_{adjusted}$)**。

### 3. 微观扳机 (High-Pass Filter / 快变量)
负责寻找情绪衰竭或爆发的临界点。
*   🌩️ **加密雷暴预警专员 (`crypto-extreme-weather`)**：监控全网合约 OI 与 Deribit 隐含波动率 (DVOL)，寻找“压紧的弹簧”。
*   🪙 **局部微气候加密专员 (`crypto-micro`)**：抓取 DefiLlama 稳定币 Velocity 及 ETF/CME 报价背离，判断是机构主导还是散户逼空。

**核心逻辑：动态阈值 (Dynamic Triggering)**
微观不直接产生买卖信号。微观信号是否报警，取决于宏观容忍度：$Trigger\_Threshold = T_{base} - (\beta \cdot E_{adjusted})$。
宏观越宽松，系统对微观泡沫的容忍度越高；宏观越紧缩，极小的微观过热也会被系统直接“拔网线”。

## 🛠️ 如何使用 (How to Use)

本仓库包含了上述架构的所有物理映射：
1. `architecture/weather_station_arch.md`：请将其复制到你的 L3 目录下，作为 AI 的底层 System Prompt。
2. `scripts/`：包含了脱敏后的 Python 数据抓取脚本（使用前请填入你的 FRED / Binance API Key）。
3. `skills/`：包含了配置好的 Gemini CLI 技能。你可以通过 `gemini skills install ./skills/xxx.skill` 来安装它们。

## ⚠️ 免责声明 (Disclaimer)
本项目开源的仅为**量化交易的哲学思想与工程架构实现方式**。生成的任何报告均不构成投资建议。操作风险远大于波动风险，请敬畏市场。
