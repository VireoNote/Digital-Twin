import json
import uuid
import re
from datetime import datetime, timezone, timedelta
from typing import List, Tuple, Dict, Any

from schemas.v4_core import (
    EvidenceRecord, Hypothesis, CounterHypothesis, ActionIntent,
    ValidationReport, PolicyEnvelope, ExposureBand, DecayProfile,
    EnvelopeStatus, HypothesisStatus
)
from lifecycle_runner import LifecycleRunner

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

# =====================================================================
# 1. VALIDATORS (交叉质询法庭)
# =====================================================================

def crypto_micro_validator(intent_bias: str, evidence_content: str) -> Dict[str, Any]:
    """
    微观流动性审查：重点关注资金流速是否支持意图。
    """
    velocity_match = re.search(r'\(Velocity\)\*\*:\s*([\d\.]+)%', evidence_content)
    if velocity_match:
        velocity = float(velocity_match.group(1))
        missing = False
    else:
        velocity = 0.0
        missing = True

    support = 0.5
    contradiction = 0.0
    conflict = False

    if intent_bias == "long":
        if velocity < 5.0:
            support = 0.2
            contradiction = 0.8
            conflict = True
        else:
            support = 0.8
            contradiction = 0.1
    elif intent_bias == "short":
        if velocity < 5.0:
            support = 0.8
            contradiction = 0.1
        else:
            support = 0.2
            contradiction = 0.8
            conflict = True
    else:
        support = 0.5
        contradiction = 0.1

    return {
        "family": "liquidity_conversion",
        "support": support,
        "contradiction": contradiction,
        "conflict": conflict,
        "missing": missing,
        "notes": f"Velocity={velocity}% vs Intent={intent_bias.upper()}"
    }

def policy_pressure_validator(intent_bias: str, evidence_content: str) -> Dict[str, Any]:
    """
    宏观压力审查：重点关注 TIPS 实际利率是否偏紧。
    """
    tips_match = re.search(r'TIPS 收益率\*\*:\s*([\d\.]+)%', evidence_content)
    if tips_match:
        tips = float(tips_match.group(1))
        missing = False
    else:
        tips = 2.0 # fallback default to tight
        missing = True

    is_tight = tips >= 1.5

    support = 0.5
    contradiction = 0.0
    conflict = False

    if intent_bias == "long":
        if is_tight:
            support = 0.3
            contradiction = 0.7
            conflict = True
        else:
            support = 0.8
            contradiction = 0.1
    elif intent_bias == "short":
        if is_tight:
            support = 0.8
            contradiction = 0.1
        else:
            support = 0.3
            contradiction = 0.7
            conflict = True
    else:
        support = 0.5
        contradiction = 0.1

    return {
        "family": "macro_structure",
        "support": support,
        "contradiction": contradiction,
        "conflict": conflict,
        "missing": missing,
        "notes": f"TIPS={tips}% (Tight={is_tight}) vs Intent={intent_bias.upper()}"
    }

def crypto_weather_validator(intent_bias: str, evidence_content: str) -> Dict[str, Any]:
    """
    衍生品法官：识别博弈结构（OI, Funding, Squeeze）。
    重点提供 Tactical Release 理由。
    """
    # 提取关键指标
    price_change_match = re.search(r'当前价格 \(BTC\): .*?\(24H:\s*([+-]?[\d\.]+)\%\)', evidence_content)
    funding_match = re.search(r'资金费率 \(Funding Rate\):\s*([+-]?[\d\.]+)%', evidence_content)
    oi_1h_match = re.search(r'OI 1H 变化率\:\s*([+-]?[\d\.]+)%', evidence_content)
    behavior_match = re.search(r'当前资金面状态\*\*: .*? ([\w\s-]+) \(', evidence_content)

    price_change = float(price_change_match.group(1)) if price_change_match else 0.0
    funding = float(funding_match.group(1)) if funding_match else 0.0
    oi_1h = float(oi_1h_match.group(1)) if oi_1h_match else 0.0
    behavior_raw = behavior_match.group(1).strip() if behavior_match else "Unknown"

    support = 0.5
    contradiction = 0.1
    tactical_release = False
    notes = [f"Behavior: {behavior_raw}, Funding: {funding}%"]

    # 1. 识别 Short Covering (空头回补 - 价格涨, OI减)
    if price_change > 0 and oi_1h < -0.5:
        notes.append("Detected potential Short Covering (空头认亏平仓)")
        if intent_bias == "long":
            support = 0.75
            tactical_release = True
            
    # 2. 识别空头衰竭 (Exhaustion - 费率极负且跌不动)
    if funding < -0.01 and abs(price_change) < 1.0:
        notes.append("Detected Short Exhaustion (空头衰竭/费率深负)")
        if intent_bias == "long":
            support = 0.8
            tactical_release = True

    # 3. 对抗性识别：Long Build-up vs Intent
    if "Long Build-up" in behavior_raw:
        if intent_bias == "long": support = 0.85
        if intent_bias == "short": contradiction = 0.8

    return {
        "family": "derivatives_structure",
        "support": support,
        "contradiction": contradiction,
        "tactical_release": tactical_release,
        "notes": " | ".join(notes)
    }

def spot_confirmation_validator(intent_bias: str, evidence_content: str) -> Dict[str, Any]:
    """
    现货确认法官：盯住 ETF 资金流向与现货溢价。
    """
    # 提取 IBIT 交易量
    etf_vol_match = re.search(r'贝莱德现货 ETF \(IBIT\): .*?单日交易量:\s*([\d,]+)\)', evidence_content)
    # 提取是否提及“狂热”或“申购”
    inflow_hint = "ETF 大量申购" in evidence_content or "现货支撑" in evidence_content

    etf_vol = int(etf_vol_match.group(1).replace(",", "")) if etf_vol_match else 0
    
    support = 0.5
    contradiction = 0.1
    offensive_alpha = False
    notes = [f"IBIT Vol: {etf_vol}"]

    if intent_bias == "long":
        # 1. 如果 ETF 交易量巨大（假设 > 20M）或有流入暗示
        if etf_vol > 20000000 or inflow_hint:
            notes.append("Strong ETF demand detected (现货买盘确认)")
            support = 0.85
            offensive_alpha = True
    
    if intent_bias == "short":
        if inflow_hint:
            notes.append("Counter-trend Spot buy detected")
            contradiction = 0.7

    return {
        "family": "spot_confirmation",
        "support": support,
        "contradiction": contradiction,
        "offensive_alpha": offensive_alpha,
        "notes": " | ".join(notes)
    }

def run_multi_court_validation(hyp: Hypothesis, intent: ActionIntent, evidences: List[EvidenceRecord]) -> ValidationReport:
    """
    Validation Engine v4.2: 汇总四路法庭证词 (Micro, Macro, Derivatives, Spot)
    """
    micro_ev = next(e for e in evidences if e.source == "crypto_micro")
    macro_ev = next(e for e in evidences if e.source == "policy_pressure")
    weather_ev = next(e for e in evidences if e.source == "crypto_weather")
    
    micro_res = crypto_micro_validator(intent.primary_bias, micro_ev.raw_payload["content"])
    macro_res = policy_pressure_validator(intent.primary_bias, macro_ev.raw_payload["content"])
    weather_res = crypto_weather_validator(intent.primary_bias, weather_ev.raw_payload["content"])
    spot_res = spot_confirmation_validator(intent.primary_bias, micro_ev.raw_payload["content"]) # 复用 micro 里的 ETF 数据

    # 聚合打分
    # 权重重新分配：三权分立的进攻性增强版
    overall_support = (macro_res["support"] * 0.3) + \
                      (micro_res["support"] * 0.3) + \
                      (weather_res["support"] * 0.2) + \
                      (spot_res["support"] * 0.2)
                      
    overall_contradiction = max(micro_res["contradiction"], macro_res["contradiction"], spot_res["contradiction"])
    
    any_conflict = micro_res["conflict"] or macro_res["conflict"]
    any_missing = micro_res["missing"] or macro_res["missing"]
    
    validator_notes = [
        f"[Micro]: {micro_res['notes']}", 
        f"[Macro]: {macro_res['notes']}", 
        f"[Deriv]: {weather_res['notes']}",
        f"[Spot]: {spot_res['notes']}"
    ]
    
    if weather_res["tactical_release"]:
        validator_notes.append(">> TACTICAL RELEASE GRANTED by Derivatives Judge")
    if spot_res["offensive_alpha"]:
        validator_notes.append(">> OFFENSIVE ALPHA confirmed by Spot Judge")

    return ValidationReport(
        validation_id=generate_id("val"),
        hypothesis_id=hyp.hypothesis_id,
        intent_id=intent.intent_id,
        validator_family_scores={
            "macro_structure": macro_res["support"],
            "liquidity_conversion": micro_res["support"],
            "derivatives_structure": weather_res["support"],
            "spot_confirmation": spot_res["support"]
        },
        support_score=overall_support,
        contradiction_score=overall_contradiction,
        alignment_score=overall_support - overall_contradiction,
        freshness_score=0.9,
        redundancy_score=0.1,
        calibration_class="historically_robust",
        validator_notes=validator_notes,
        veto_flags={
            "stale_critical_data": False,
            "semantic_numeric_conflict": any_conflict,
            "missing_core_confirmation": any_missing,
            "excessive_echo_risk": False,
            "historical_low_repeatability": False
        },
        generated_at=datetime.now(timezone.utc),
        valid_until=datetime.now(timezone.utc) + timedelta(hours=4)
    )

# =====================================================================
# 2. POLICY COMPILER (处理现货溢价带来的灵活性)
# =====================================================================

def compile_policy_envelope(hyp: Hypothesis, intent: ActionIntent, val: ValidationReport) -> PolicyEnvelope:
    """
    处理 4 种多法庭结果。
    """
    scores = val.validator_family_scores
    macro_support = scores["macro_structure"] > 0.5
    micro_support = scores["liquidity_conversion"] > 0.5
    deriv_tactical = scores["derivatives_structure"] > 0.7
    spot_support = scores["spot_confirmation"] > 0.7

    notes = []
    
    # 场景 1：双主法官反对，但现货+衍生品强力支持 (现货驱动的战术解冻)
    if not macro_support and not micro_support and (deriv_tactical or spot_support):
        allowed_dir = intent.primary_bias
        # 如果两位进攻法官都支持，给稍大一点的战术空间
        upper = 0.15 if (deriv_tactical and spot_support) else 0.10
        target_band = ExposureBand(lower=0.0, upper=upper)
        aggression = "low"
        c_mode = "tactical_only"
        notes.append("Compiler Rule: DUAL REJECT but SPOT/DERIV OFFENSIVE PUSH")
        
    # 场景 2：真正的双反对 (全票否决)
    elif not macro_support and not micro_support:
        allowed_dir = "neutral"
        target_band = ExposureBand(lower=0.0, upper=0.0)
        aggression = "low"
        c_mode = "frozen"
        notes.append("Compiler Rule: DUAL REJECT -> Vetoed/Frozen")
        
    # 场景 3：分裂法庭 (正常逻辑)
    elif macro_support != micro_support:
        allowed_dir = intent.primary_bias
        limit = 0.25 if spot_support else 0.15
        target_band = ExposureBand(lower=0.0, upper=limit) 
        aggression = "low"
        c_mode = "tactical_only"
        notes.append(f"Compiler Rule: SPLIT COURT -> Scaled Down (Spot {'Strong' if spot_support else 'Weak'})")
        
    # 场景 4：放行
    else:
        allowed_dir = intent.primary_bias
        # 即使放行，也要看现货脸色
        upper_cap = 0.6 if spot_support else 0.4
        target_band = ExposureBand(lower=0.2, upper=upper_cap)
        aggression = intent.aggression
        c_mode = "structural_allowed"
        notes.append("Compiler Rule: DUAL SUPPORT -> Admitted")

    return PolicyEnvelope(
        envelope_id=generate_id("env"),
        hypothesis_id=hyp.hypothesis_id,
        intent_id=intent.intent_id,
        validation_id=val.validation_id,
        constitution_decision_id="const_dummy",
        allowed_direction=allowed_dir,
        max_exposure=target_band.upper,
        min_exposure=target_band.lower,
        target_exposure_band=target_band,
        compiler_mode=c_mode,
        aggression_cap=aggression,
        decay_profile=DecayProfile(mode="fast", ttl_seconds=14400),
        invalidation_triggers=[],
        execution_urgency="medium",
        policy_notes=notes,
        compiled_at=datetime.now(timezone.utc)
    )

# =====================================================================
# 3. MOCK DATA & SCENARIO RUNNER
# =====================================================================

def create_mock_evidence(source: str, content: str) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=generate_id("ev"),
        source=source,
        modality="text",
        observed_time=datetime.now(timezone.utc),
        effective_time=datetime.now(timezone.utc),
        ingest_time=datetime.now(timezone.utc),
        ttl_seconds=86400,
        reliability_prior=0.9,
        entity_tags=["mock"],
        lineage_id="mock_lineage",
        payload_hash="mock_hash",
        raw_payload={"content": content}
    )

def create_mock_cognition(bias: str, text: str) -> Tuple[Hypothesis, ActionIntent]:
    base_time = datetime.now(timezone.utc)
    hyp_id = generate_id("hyp")
    hyp = Hypothesis(
        hypothesis_id=hyp_id, status=HypothesisStatus.EMERGING,
        thesis_text=text, thesis_summary=text, horizon="d7", bias=bias,
        causal_chain=[], primary_mechanism_tags=[], supporting_evidence_refs=[],
        counter_evidence_refs=[], missing_evidence_refs=[], overlap_groups_touched=[],
        evidence_diversity_score=0.5, echo_risk_score=0.1, fragility="medium",
        reflexivity_risk="medium", invalidation_conditions=[], ambiguity_notes=[],
        confidence_expression="strong", generated_by="mock", generated_at=base_time
    )
    intent = ActionIntent(
        intent_id=generate_id("intent"), hypothesis_id=hyp_id,
        primary_bias=bias, aggression="high", conviction_style="strong",
        hold_profile="tactical", fragility="high", hedge_preference="strong",
        expected_confirmation_window="short", required_confirmations=[],
        invalidation_triggers=[], action_notes=[], generated_at=base_time
    )
    return hyp, intent


def run_scenario(name: str, intent_bias: str, micro_content: str, macro_content: str):
    print(f"\n==================================================")
    print(f"   SCENARIO: {name.upper()}")
    print(f"==================================================")

    ev_micro = create_mock_evidence("crypto_micro", micro_content)
    ev_macro = create_mock_evidence("policy_pressure", macro_content)
    evidences = [ev_micro, ev_macro]

    hyp, intent = create_mock_cognition(intent_bias, f"LLM Intent is {intent_bias.upper()}")
    
    print(f"[LLM] Bias: {intent_bias.upper()}")
    print(f"[Data] Micro: {micro_content.strip()}")
    print(f"[Data] Macro: {macro_content.strip()}")

    # Validation
    report = run_multi_court_validation(hyp, intent, evidences)
    print("\n  [Validation Outputs]")
    for note in report.validator_notes:
        print(f"    {note}")
    print(f"    -> Support: {report.support_score:.2f} | Contradiction: {report.contradiction_score:.2f}")
    print(f"    -> Semantic Conflict: {report.veto_flags['semantic_numeric_conflict']}")

    # Compile
    env = compile_policy_envelope(hyp, intent, report)
    print("\n  [Compiler Outputs]")
    print(f"    -> {env.policy_notes[0]}")
    print(f"    -> Allowed: {env.allowed_direction.upper()} | Band: [{env.target_exposure_band.lower}, {env.target_exposure_band.upper}]")

    # Lifecycle
    runner = LifecycleRunner()
    result = runner.run_cycle([hyp], {hyp.hypothesis_id: report}, {hyp.hypothesis_id: [env]})
    print("\n  [Lifecycle Result]")
    if result["transitions"]:
        print(f"    >> {result['transitions'][0]}")
    else:
        print(f"    >> No transition. Remained {hyp.status.value}")

def main():
    print("==================================================")
    print("   Trading Agent Architecture 4.0 - MULTI COURT")
    print("==================================================")

    # 场景 1：双支持 (LLM做空，微观低流速支持，宏观紧缩支持)
    run_scenario(
        name="1. DUAL SUPPORT (双支持放行)",
        intent_bias="short",
        micro_content="- **全网稳定币日流速 (Velocity)**: 2.64%",
        macro_content="- **当前 TIPS 收益率**: 1.8%"
    )

    # 场景 2：双反对 (LLM做多，微观低流速反对，宏观紧缩反对)
    run_scenario(
        name="2. DUAL REJECT (双反对冻结)",
        intent_bias="long",
        micro_content="- **全网稳定币日流速 (Velocity)**: 2.64%",
        macro_content="- **当前 TIPS 收益率**: 1.8%"
    )

    # 场景 3：分裂法庭 (LLM做多，微观低流速反对，但宏观宽松支持)
    run_scenario(
        name="3. SPLIT COURT (内部分歧缩放)",
        intent_bias="long",
        micro_content="- **全网稳定币日流速 (Velocity)**: 2.64%",   # 资金没动，不支持做多
        macro_content="- **当前 TIPS 收益率**: 1.2%"    # TIPS回落，支持做多
    )

if __name__ == "__main__":
    main()
