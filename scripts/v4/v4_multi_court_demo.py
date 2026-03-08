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

def run_multi_court_validation(hyp: Hypothesis, intent: ActionIntent, evidences: List[EvidenceRecord]) -> ValidationReport:
    """
    Validation Engine: 汇总多路法庭证词
    """
    micro_ev = next(e for e in evidences if e.source == "crypto_micro")
    macro_ev = next(e for e in evidences if e.source == "policy_pressure")
    
    micro_res = crypto_micro_validator(intent.primary_bias, micro_ev.raw_payload["content"])
    macro_res = policy_pressure_validator(intent.primary_bias, macro_ev.raw_payload["content"])

    # 聚合打分 (取最悲观的 contradiction 作为防御底线，平均 support 作为信心线)
    overall_support = (micro_res["support"] + macro_res["support"]) / 2.0
    overall_contradiction = max(micro_res["contradiction"], macro_res["contradiction"])
    
    any_conflict = micro_res["conflict"] or macro_res["conflict"]
    any_missing = micro_res["missing"] or macro_res["missing"]
    
    validator_notes = [f"[Micro]: {micro_res['notes']}", f"[Macro]: {macro_res['notes']}"]
    if micro_res["conflict"] != macro_res["conflict"]:
        if macro_res["support"] > 0.5 and micro_res["conflict"]:
            validator_notes.append(">> SPLIT COURT DETECTED: macro_support_micro_reject (背景改善，但场内没确认)")
        elif micro_res["conflict"] and macro_res["support"] <= 0.5:
            # Fallback for logical completeness in demo
            validator_notes.append(">> SPLIT COURT DETECTED: macro_reject_micro_support (短线技术性支持，但大背景仍压制)")
        else:
            validator_notes.append(">> SPLIT COURT DETECTED: macro_reject_micro_support (短线技术性支持，但大背景仍压制)")

    return ValidationReport(
        validation_id=generate_id("val"),
        hypothesis_id=hyp.hypothesis_id,
        intent_id=intent.intent_id,
        validator_family_scores={
            "macro_structure": macro_res["support"],
            "liquidity_conversion": micro_res["support"]
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
# 2. POLICY COMPILER (学会处理分歧)
# =====================================================================

def compile_policy_envelope(hyp: Hypothesis, intent: ActionIntent, val: ValidationReport) -> PolicyEnvelope:
    """
    处理 3 种多法庭结果：放行(一致支持)、冻结(一致反对)、缩放(分裂)
    """
    macro_score = val.validator_family_scores["macro_structure"]
    micro_score = val.validator_family_scores["liquidity_conversion"]
    
    macro_support = macro_score > 0.5
    micro_support = micro_score > 0.5

    notes = []
    
    # 场景 2：双反对 (一致否定) -> 冻结
    if not macro_support and not micro_support:
        allowed_dir = "neutral"
        target_band = ExposureBand(lower=0.0, upper=0.0)
        aggression = "low"
        c_mode = "frozen"
        notes.append("Compiler Rule: DUAL REJECT -> Vetoed/Frozen")
        
    # 场景 3：分裂 (一支持一反对) -> 缩放
    elif macro_support != micro_support:
        allowed_dir = intent.primary_bias
        target_band = ExposureBand(lower=0.0, upper=0.15) # 极小仓位
        aggression = "low"
        c_mode = "tactical_only"
        notes.append("Compiler Rule: SPLIT COURT -> Scaled Down (Tactical Only)")
        
    # 场景 1：双支持 (一致肯定) -> 放行
    else:
        allowed_dir = intent.primary_bias
        target_band = ExposureBand(lower=0.2, upper=0.5)
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
