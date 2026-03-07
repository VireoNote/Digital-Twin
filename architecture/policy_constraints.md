# L2.7 Policy Kernel Constraints (Stage A Boundaries)

这些是系统执行控制的**不可商量之红线 (Institutional Rules)**。它们在计算任何目标敞口之前具有绝对的否决权。

## 1. Validity Kill Switch (时效与健康截断)
- 若 L2.5 中的核心状态（如 `P_30d_Tailwind` 或 `Regime`）超过 `decay_half_life` 且未得到重验证，强制 `action_allowed = false`，禁止新增敞口。

## 2. Risk Damper (风险阻尼器)
- 当 `P_24h_Adverse_Risk > 0.8` 时，系统 `risk_gross_cap` 强制下调至当前仓位的 50%（或最大 0.5x），无视中长期看多信号的强度。
- 若处于高风险阻尼状态，只能进行减仓或增加 Hedge Ratio 的操作。

## 3. Regime Hysteresis (系统状态切换冷却)
- 当检测到 L2.5 `Regime` 发生跳变时，启动为期 24 小时的冷却窗（Cooling Window）。在此期间，除非触发强制止损，否则 `action_allowed = false`。

## 4. Minimum Action Threshold (最小动作阈值)
- 计算 Stage B 输出的 `target_net_exposure` 与当前实际敞口的差异。若差值绝对值 `< 5%`，且不处于极端风险状态，则判定为摩擦损耗大于收益，强制覆盖决定为 `HOLD`。
