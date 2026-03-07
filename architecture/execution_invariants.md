# L2.8 Execution Invariants (The Idempotent Kernel)

这些规则定义了系统如何将 `Target Intent` 转化为物理的交易所请求，确保在任何网络故障或状态延迟下，交易执行具备绝对的**幂等性 (Idempotency)** 和**原子归属性 (Atomic Reconciliation)**。

## 1. Effective Position 计算定律
严禁将未确认状态粗暴加总。所有目标差异 (`Diff`) 必须基于 `EffectivePosition`，公式如下：
`EffectivePosition = Settled_Position + Executable_Inflight_Effect`

**在途折算系数 (In-flight Discounting)**:
- **`CONFIRMED_OPEN` (交易所已确认挂单)**: 计为 1.0x。
- **`SUBMITTED_PENDING` (系统已发出，未收到 OrderID)**: 计为 0.5x ~ 0.8x（基于历史网络成功率折算，通常视为中可信）。
- **`PARTIALLY_FILLED` (部分成交)**: 已成交部分移入 `Settled`，剩余未成交部分作为 `CONFIRMED_OPEN` 计入 `Inflight`。
- **`PENDING_CANCEL` (正在撤销中)**: 计为 0.0x（视为该敞口已不存在，避免因撤单延迟导致系统重复下达替代单）。

## 2. 意图感知撤单 (Intent-Aware Cancel)
废除无脑的 `Cancel All`。只有当现存挂单与当前的 `Target Intent` 发生逻辑冲突时才执行撤单：
- **冲突分类**：
  1. **方向不一致 (Wrong Side)**：Target 需要减仓，但存在未成交的买单。
  2. **意图超载 (Over-sizing)**：现存挂单加上 `Settled_Position` 超过了当前的 `Target_Net_Exposure`。
  3. **价格脱离区间 (Price Out-of-bounds)**：限价单价格偏离当前 Orderbook 超过允许范围（不再服务于当前 Diff）。
- 符合上述任何一条的订单标记为 `Stale` 并加入撤单队列；其他订单保留。

## 3. 重平衡循环的原子性与溯源 (Atomic Rebalance & Lineage Tracing)
- **强类型因果信封 (Causal Envelope)**：L2.8 接收的 Target Intent 必须是一个包含 `decision_id` 及其 `lineage` (state_version, constraint_version, market_snapshot_id) 的信封对象。
- **ClientOid 挂载强制要求**：每次执行循环下达的所有的物理 `Cancel` 和 `Place` 操作，**必须将 `decision_id` 注入到交易所的 `clientOid` (或作为前缀/后缀)**。
- 只有这样，当发生异常或回测对账时，我们才能从交易所的订单历史上直接反查出：这笔订单是在哪个特征窗口下、基于哪个版本的认知状态、被哪版风控规则放行的。
