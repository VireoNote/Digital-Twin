# L2.5 State Transition Rules (Probabilistic Logic Invariants)

这些规则定义了 L2.5 内部不同 Typed State 发生变更时的强制级联反应。系统必须在每次更新 State Register 前执行此“写入前自检 (Pre-commit Validation)”。

## 1. 级联失效规则 (Cascade Invalidation)
- **T1 - Regime 切换**: 当 `Regime` 的 `value` 发生变更时，当前存在的 `P_30d_Tailwind` 和 `P_7d_Continuation` 的 `confidence` 必须强制乘以 0.1（或归零）。这意味着在旧 Regime 下训练的先验概率在新的底层规则下失效，强制系统基于新 Regime 重新计算中长期概率。
- **T2 - 置信度衰减 (Decay)**: 如果当前时间减去 `as_of` 大于 `decay_half_life`，系统的读取器在提取该状态时，必须动态将其 `confidence` 减半。当 `confidence < 0.3` 时，该状态被视为“失效 (Invalid)”。

## 2. 跨时域一致性守卫 (Cross-Horizon Consistency)
认知层允许长短期看法不一致，但这必须是有逻辑支撑的（即“反弹”而不是“趋势反转”）。
- **T3 - 嵌套约束**: `P_24h_Adverse_Risk` 的爆发，如果是孤立的（不带有流动性恶化的 Evidence），不能单独去修改 `P_30d_Tailwind`。
- **T4 - 矛盾审查**: 如果 `P_30d_Tailwind > 0.6` (看多) 且 `P_7d_Continuation < 0.3` (看空回调)，必须在更新 `P_7d` 的时候，在 `derived_from_evidence_ids` 中明确引用“超买/资金费率过高”的微观结构证据，**不允许无解释的冲突**。

## 3. 证据溯源红线 (Lineage Requirement)
- **T5 - 无证据不更新**: 任何 `confidence` 大于 0.5 的状态更新，其 `derived_from_evidence_ids` 数组不能为空，且必须指向 L2.3 Evidence Graph 中时间戳在 `effective_from` 之前的合法节点。
