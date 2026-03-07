---
name: nlp-sentiment
description: 交易架构3.0 - NLP情绪因子提取器。基于 OpenNews MCP 抓取并量化社交媒体与新闻情绪，将其转化为连续的 Alpha 因子。用于在预测模型中补齐基本面和情绪面的量化感知。
---

# NLP情绪因子提取器 (Feels-like Temperature Specialist)

本技能属于“交易架构 3.0”的**感知层与同化层**，作为 NLP 与情绪分析的核心模块。
专员通过抓取 `opennews-mcp` (AI评级 >= 0 的资讯)，量化其 `score` 与 `signal` (long/short)，将情绪转化为连续的连续 Alpha 因子 ([-1, 1])。

## 工作流与执行指令 (Execution)

当你在推演过程中，或用户要求“感知当前市场情绪”、“抓取项目基本面”或“计算情绪 Alpha”时，调用此技能：

1. **执行抓取并生成报告**：
   运行本地 Python 脚本。你可以选择性传入一个查询词（例如 "BTC"、"ETF" 等），如果不传则抓取全网最新。
   ```bash
   python3 /home/liwu/digital_twin/Skills/nlp-sentiment/scripts/fetch_sentiment.py [可选: "查询词"]
   ```
2. **分析结果**：
   脚本会自动生成 Alpha 因子，并将完整的研报存入 `L1 原始事件层`（`/home/liwu/digital_twin/Inbox/`）。你可以在输出中直接读取 Alpha 因子的数值与最近驱动事件。
3. **输出融合研判**：
   将计算出的 `Alpha Factor` 作为情绪偏移项，辅助 L3 认知中心修正最终的综合胜率。如果 Alpha 极度偏离 0，说明市场处于极度 Fomo 或恐慌。
