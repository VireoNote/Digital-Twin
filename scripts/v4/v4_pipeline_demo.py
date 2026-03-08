import json
import uuid
import hashlib
import os
import re
from datetime import datetime, timezone, timedelta
from typing import List, Tuple

# Pydantic schemas
from schemas.v4_core import (
    EvidenceRecord, Hypothesis, CounterHypothesis, ActionIntent,
    ValidationReport, PolicyEnvelope, ExposureBand, DecayProfile,
    EnvelopeStatus, HypothesisStatus
)
from lifecycle_runner import LifecycleRunner

# Use google-generativeai if available
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def load_evidence(file_path: str, source: str) -> EvidenceRecord:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    return EvidenceRecord(
        evidence_id=generate_id("ev"),
        source=source,
        modality="text",
        observed_time=datetime.now(timezone.utc),
        effective_time=datetime.now(timezone.utc),
        ingest_time=datetime.now(timezone.utc),
        ttl_seconds=86400,
        reliability_prior=0.9,
        entity_tags=["macro", "crypto"],
        lineage_id="lineage_default",
        payload_hash=hashlib.md5(content.encode()).hexdigest(),
        raw_payload={"content": content}
    )

def call_llm_for_cognition(evidences: List[EvidenceRecord], scenario: str = "aligned_short") -> Tuple[Hypothesis, CounterHypothesis, ActionIntent]:
    """
    Step 2: LLM Cognition
    Supports testing scenarios: 'aligned_short' vs 'conflicting_long'
    """
    print(f"\n[Step 2] -> Requesting LLM Cognition (Mocking structure for stability or calling API)... [Scenario: {scenario}]")
    
    # Check if API key is in env
    api_key = os.environ.get("GEMINI_API_KEY")
    if HAS_GENAI and api_key and scenario == "real_api":
        genai.configure(api_key=api_key)
        # Using structured output feature
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        prompt = "Based on the following evidence, generate a market Hypothesis, CounterHypothesis, and ActionIntent. Reply ONLY in JSON containing these three objects.\n\n"
        for ev in evidences:
            prompt += f"--- Evidence ({ev.source}) ---\n{ev.raw_payload['content']}\n\n"
            
        try:
            print("  Calling real Gemini API...")
            resp = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            data = json.loads(resp.text)
            print("  API Call successful! Parsing JSON...")
            pass 
        except Exception as e:
            print(f"  API Call or parsing failed ({e}). Falling back to MOCK JSON.")
    else:
        print("  Using MOCK JSON generator for testing scenario.")

    base_time = datetime.now(timezone.utc)
    hyp_id = generate_id("hyp")
    
    if scenario == "conflicting_long":
        # Case B: LLM goes wild, highly bullish narrative completely ignoring low velocity and bad macro
        hyp = Hypothesis(
            hypothesis_id=hyp_id,
            status=HypothesisStatus.EMERGING,
            thesis_text="结构性牛市起步，风险偏好扩张，ETF资金的流入将产生巨大的财富效应，完全无视短期的流动性缩减。",
            thesis_summary="结构性牛市起步，风险偏好扩张",
            horizon="d30",
            bias="long",
            causal_chain=[
                {"step": 1, "statement": "IBIT单日交易量巨大，说明散户资金源源不断。", "supporting_claim_ids": [], "supporting_event_ids": []}
            ],
            primary_mechanism_tags=["retail_fomo", "wealth_effect"],
            supporting_evidence_refs=[],
            counter_evidence_refs=[],
            missing_evidence_refs=[],
            overlap_groups_touched=[],
            evidence_diversity_score=0.2,
            echo_risk_score=0.8,
            fragility="high",
            reflexivity_risk="high",
            invalidation_conditions=[],
            ambiguity_notes=[],
            confidence_expression="strong",
            generated_by="gemini_cognition_mock",
            generated_at=base_time
        )
        chyp = CounterHypothesis(
            counter_hypothesis_id=generate_id("chyp"),
            primary_hypothesis_id=hyp_id,
            thesis_text="流动性不支持上涨。",
            thesis_summary="熊市",
            horizon="d7",
            bias="short",
            strongest_conflict_points=[],
            supporting_evidence_refs=[],
            missing_evidence_refs=[],
            what_would_make_this_dominate=[],
            confidence_expression="weak",
            generated_by="gemini_cognition_mock",
            generated_at=base_time
        )
        intent = ActionIntent(
            intent_id=generate_id("intent"),
            hypothesis_id=hyp_id,
            primary_bias="long",
            aggression="high",
            conviction_style="strong",
            hold_profile="structural",
            fragility="high",
            hedge_preference="none",
            expected_confirmation_window="immediate",
            required_confirmations=[],
            invalidation_triggers=[],
            action_notes=["满仓做多"],
            generated_at=base_time
        )
    else:
        # Case A: Default 'aligned_short' scenario
        hyp = Hypothesis(
            hypothesis_id=hyp_id,
            status=HypothesisStatus.EMERGING,
            thesis_text="散户正在通过ETF推高BTC价格，但缺乏机构资金与宏观流动性的实质性支撑，属于场内存量博弈的脆弱上涨。",
            thesis_summary="散户逼空，流动性死水，反弹脆弱",
            horizon="d7",
            bias="short",
            causal_chain=[
                {"step": 1, "statement": "IBIT交易量放大但CME主力合约未见显著增量，说明由散户主导。", "supporting_claim_ids": [], "supporting_event_ids": []},
                {"step": 2, "statement": "稳定币流速极低，说明大量资金沉淀吃息，无实质增量购买力。", "supporting_claim_ids": [], "supporting_event_ids": []}
            ],
            primary_mechanism_tags=["retail_squeeze", "liquidity_trap"],
            supporting_evidence_refs=[],
            counter_evidence_refs=[],
            missing_evidence_refs=[],
            overlap_groups_touched=[],
            evidence_diversity_score=0.8,
            echo_risk_score=0.2,
            fragility="high",
            reflexivity_risk="medium",
            invalidation_conditions=[
                {"condition_id": "inv_1", "description": "如果稳定币流速 (Velocity) 突破 5%，说明真实资金下场。", "expected_validator": "crypto_micro", "deadline": None}
            ],
            ambiguity_notes=[],
            confidence_expression="moderate",
            generated_by="gemini_cognition_mock",
            generated_at=base_time
        )
        chyp = CounterHypothesis(
            counter_hypothesis_id=generate_id("chyp"),
            primary_hypothesis_id=hyp_id,
            thesis_text="ETF资金流入本身就是新周期的第一波流动性，机构可能会在价格突破关键阻力位后被动追高填补CME敞口。",
            thesis_summary="ETF主导的结构性牛市起步",
            horizon="d30",
            bias="long",
            strongest_conflict_points=["忽视了ETF资金的粘性", "机构可能只是慢半拍"],
            supporting_evidence_refs=[],
            missing_evidence_refs=[],
            what_would_make_this_dominate=["CME未平仓合约连续3天飙升", "TIPS收益率掉头向下"],
            confidence_expression="weak",
            generated_by="gemini_cognition_mock",
            generated_at=base_time
        )
        intent = ActionIntent(
            intent_id=generate_id("intent"),
            hypothesis_id=hyp_id,
            primary_bias="short",
            aggression="low",
            conviction_style="tentative",
            hold_profile="tactical",
            fragility="high",
            hedge_preference="strong",
            expected_confirmation_window="short",
            required_confirmations=["CME持续不跟", "散户情绪指标触顶"],
            invalidation_triggers=["Velocity > 5%"],
            action_notes=["不建议直接重仓做空，而是逢高卖出或做空波动率"],
            generated_at=base_time
        )

    return hyp, chyp, intent

def run_simple_validator(hyp: Hypothesis, intent: ActionIntent, evidences: List[EvidenceRecord]) -> ValidationReport:
    """
    Step 3: Simple Validation
    检查业务逻辑：LLM看多但数据看空，或者反之。
    """
    print("\n[Step 3] -> Running Validator (Data vs Narrative challenge)...")
    
    # Extract velocity from crypto_micro evidence manually (like a real regex scraper)
    micro_ev = next(e for e in evidences if e.source == "crypto_micro")
    
    # Text looks like: - **全网稳定币日流速 (Velocity)**: 2.64%
    velocity_match = re.search(r'\(Velocity\)\*\*:\s*([\d\.]+)%', micro_ev.raw_payload["content"])
    if velocity_match:
        velocity = float(velocity_match.group(1))
    else:
        print("  [Validator ERROR] Failed to parse Velocity from evidence. Using fallback 0.0, but raising missing_core_confirmation.")
        velocity = 0.0
        
    # Base scores
    support = 0.6
    contradiction = 0.2
    semantic_numeric_conflict = False

    # Validation Rule: 
    # 如果 LLM intent.primary_bias 是 "long" 且 velocity < 5%，则属于严重冲突！
    if intent.primary_bias == "long" and velocity < 5.0:
        print(f"  [Validator ALERT] Semantic/Numeric Conflict! Bias is LONG but Velocity is low ({velocity}%).")
        contradiction = 0.85 # High challenge!
        support = 0.3
        semantic_numeric_conflict = True
    
    # 刚好我们 mock 的 LLM 偏向 "short" 且抓住了 "散户逼空"。
    # 所以 validator 认为它很贴合现实。
    elif intent.primary_bias == "short" and velocity < 5.0:
        print(f"  [Validator] Narrative aligns with Data. Bias SHORT, Velocity low ({velocity}%).")
        support = 0.85
        contradiction = 0.1

    missing_core = True if velocity == 0.0 else False

    return ValidationReport(
        validation_id=generate_id("val"),
        hypothesis_id=hyp.hypothesis_id,
        intent_id=intent.intent_id,
        support_score=support,
        contradiction_score=contradiction,
        alignment_score=0.9 if not semantic_numeric_conflict else 0.2,
        freshness_score=0.9,
        redundancy_score=0.1,
        calibration_class="historically_robust",
        validator_notes=[f"Checked Velocity={velocity}% against bias={intent.primary_bias}"],
        veto_flags={
            "stale_critical_data": False,
            "semantic_numeric_conflict": semantic_numeric_conflict,
            "missing_core_confirmation": missing_core,
            "excessive_echo_risk": False,
            "historical_low_repeatability": False
        },
        generated_at=datetime.now(timezone.utc),
        valid_until=datetime.now(timezone.utc) + timedelta(hours=4)
    )

def compile_policy_envelope(hyp: Hypothesis, intent: ActionIntent, val: ValidationReport) -> PolicyEnvelope:
    """
    Step 4: Policy Compiler
    将认知和质询结果静态编译。
    """
    print("\n[Step 4] -> Compiling PolicyEnvelope...")
    
    # Hardcoded Rules
    allowed_dir = intent.primary_bias
    
    # Determine exposure bounds based on validation scores
    if val.veto_flags["semantic_numeric_conflict"] or val.contradiction_score > 0.7:
        target_band = ExposureBand(lower=0.0, upper=0.0) # Vetoed by compiler logic basically
        aggression = "low"
    else:
        # Scale exposure based on support
        if val.support_score > 0.8:
            target_band = ExposureBand(lower=0.2, upper=0.5)
            aggression = "medium"
        else:
            target_band = ExposureBand(lower=0.0, upper=0.2)
            aggression = "low"

    return PolicyEnvelope(
        envelope_id=generate_id("env"),
        hypothesis_id=hyp.hypothesis_id,
        intent_id=intent.intent_id,
        validation_id=val.validation_id,
        constitution_decision_id="const_dummy_001", # Assume passed Constitution
        allowed_direction=allowed_dir,
        max_exposure=target_band.upper,
        min_exposure=target_band.lower,
        target_exposure_band=target_band,
        aggression_cap=aggression,
        decay_profile=DecayProfile(mode="fast", ttl_seconds=14400),
        invalidation_triggers=intent.invalidation_triggers,
        execution_urgency="low",
        policy_notes=["Compiled statically by demo rules"],
        compiled_at=datetime.now(timezone.utc)
    )

def run_scenario(scenario_name: str, evidences: List[EvidenceRecord]):
    print(f"\n==================================================")
    print(f"   SCENARIO: {scenario_name.upper()}")
    print(f"==================================================")

    # Step 2
    hyp, chyp, intent = call_llm_for_cognition(evidences, scenario=scenario_name)
    print("\n  [Cognition Outputs]")
    print(f"  - Hypothesis ({hyp.status.value}): {hyp.thesis_summary}")
    print(f"  - ActionIntent: {intent.primary_bias.upper()}, Aggression={intent.aggression}")

    # Step 3
    report = run_simple_validator(hyp, intent, evidences)
    print("\n  [Validation Outputs]")
    print(f"  - Support: {report.support_score} | Contradiction: {report.contradiction_score}")
    print(f"  - Semantic/Numeric Conflict: {report.veto_flags['semantic_numeric_conflict']}")
    print(f"  - Missing Core Confirmation: {report.veto_flags['missing_core_confirmation']}")

    # Step 4
    env = compile_policy_envelope(hyp, intent, report)
    print("\n  [Compiler Outputs]")
    print(f"  - Envelope ({env.status.value}): AllowedDir={env.allowed_direction.upper()}, TargetBand=[{env.target_exposure_band.lower}, {env.target_exposure_band.upper}], Aggression={env.aggression_cap}")

    # Step 5 & 6
    print("\n[Step 5] -> Feeding to LifecycleRunner...")
    runner = LifecycleRunner()
    report_store = {hyp.hypothesis_id: report}
    env_store = {hyp.hypothesis_id: [env]}
    
    result = runner.run_cycle([hyp], report_store, env_store)
    
    print("\n  [Lifecycle Results]")
    if result["transitions"]:
        for t in result["transitions"]:
            print(f"  >> {t}")
    else:
        print(f"  >> {hyp.hypothesis_id}: No transition. Remained {hyp.status.value}")
        
    for updated_env in result["updated_envelopes"]:
        print(f"  >> Cascaded Envelope: {updated_env.envelope_id} -> {updated_env.status.value}")


def main():
    print("==================================================")
    print("   Trading Agent Architecture 4.0 - E2E DEMO")
    print("==================================================\n")

    # Step 1
    print("[Step 1] -> Loading Ingest Artifacts (Evidence)...")
    path_macro = "/home/liwu/digital_twin/01_Ingest/policy_pressure_20260307_000456.md"
    path_micro = "/home/liwu/digital_twin/01_Ingest/crypto_micro_20260307_000531.md"
    
    ev_macro = load_evidence(path_macro, "policy_pressure")
    ev_micro = load_evidence(path_micro, "crypto_micro")
    evidences = [ev_macro, ev_micro]
    
    for ev in evidences:
        print(f"  - Loaded {ev.source} ({len(ev.raw_payload['content'])} bytes)")

    # Run Dual Scenarios
    run_scenario("aligned_short", evidences)
    run_scenario("conflicting_long", evidences)

    print("\n==================================================")
    print("   END OF DEMO")
    print("==================================================")


if __name__ == "__main__":
    main()
