import json
import uuid
import os
import argparse
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

# Assuming v4_multi_court_demo contains our working Logic
from v4_multi_court_demo import (
    create_mock_evidence, create_mock_cognition, 
    run_multi_court_validation, compile_policy_envelope
)
from schemas.v4_core import HypothesisStatus
from lifecycle_runner import LifecycleRunner

# The JSONL target
SHADOW_LOG_PATH = "/home/liwu/digital_twin/06_Governance/shadow/shadow_runs.jsonl"

def generate_run_id() -> str:
    return f"run_{uuid.uuid4().hex[:8]}"

def determine_decision_delta_class(shadow_dir: str, legacy_dir: str, shadow_band_upper: float, legacy_exp: float) -> str:
    if shadow_dir == "neutral" and legacy_dir != "neutral" and legacy_exp > 0:
        return "shadow_frozen_legacy_active"
    
    if shadow_dir != legacy_dir:
        return "direction_disagreement"

    # Same direction. Compare sizing.
    if abs(shadow_band_upper - legacy_exp) < 0.1:
        return "same_direction_same_risk"
    elif shadow_band_upper < legacy_exp:
        return "same_direction_shadow_more_conservative"
    else:
        return "same_direction_shadow_more_aggressive"


def run_shadow_pass(legacy_direction: str, legacy_exposure: float, micro_content: str, macro_content: str, weather_content: str):
    """
    执行单次影子编译与比对，并将结构化结果写入 JSONL
    """
    run_id = generate_run_id()
    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. 挂载真实数据
    ev_micro = create_mock_evidence("crypto_micro", micro_content)
    ev_macro = create_mock_evidence("policy_pressure", macro_content)
    ev_weather = create_mock_evidence("crypto_weather", weather_content)
    
    # 模拟当前的 LLM 认知倾向（这里为了 Demo 我们随机根据 legacy 逆推一个 mock 认知）
    # 真实场景应该调用 Gemini，这里用参数模拟
    hyp_bias = legacy_direction if legacy_direction != "neutral" else "long" # Fallback guess
    hyp, intent = create_mock_cognition(hyp_bias, "Shadow LLM Analysis")

    # 2. 跑 Shadow 链路
    report = run_multi_court_validation(hyp, intent, [ev_micro, ev_macro, ev_weather])
    env = compile_policy_envelope(hyp, intent, report)
    
    # Lifecycle Mock 
    runner = LifecycleRunner()
    result = runner.run_cycle([hyp], {hyp.hypothesis_id: report}, {hyp.hypothesis_id: [env]})
    
    hyp_status_after = hyp.status.value
    lifecycle_transition = result["transitions"][0] if result["transitions"] else "None"

    # 3. 提取分歧模式
    split_court_detected = False
    split_court_type = "None"
    
    for note in report.validator_notes:
        if "SPLIT COURT DETECTED" in note:
            split_court_detected = True
            if "macro_support_micro_reject" in note:
                split_court_type = "macro_support_micro_reject"
            elif "macro_reject_micro_support" in note:
                split_court_type = "macro_reject_micro_support"

    band_width = env.target_exposure_band.upper - env.target_exposure_band.lower
    delta_class = determine_decision_delta_class(
        env.allowed_direction, legacy_direction, 
        env.target_exposure_band.upper, legacy_exposure
    )

    # 4. 构建结构化日志对象 (符合您的字段要求)
    record = {
        # 基础标识
        "run_id": run_id,
        "timestamp": now_iso,
        "scenario_type": "live_shadow",
        "asset_scope": "BTC",
        
        # 认知层
        "hypothesis_id": hyp.hypothesis_id,
        "hypothesis_status_before": "emerging",
        "hypothesis_status_after": hyp_status_after,
        "hypothesis_bias": hyp.bias,
        "action_intent_bias": intent.primary_bias,
        "action_intent_aggression": intent.aggression,
        
        # 验证层
        "support_score": round(report.support_score, 3),
        "contradiction_score": round(report.contradiction_score, 3),
        "semantic_numeric_conflict": report.veto_flags["semantic_numeric_conflict"],
        "split_court_detected": split_court_detected,
        "split_court_type": split_court_type,
        
        # 编译层
        "compiler_mode": env.compiler_mode.value,
        "allowed_direction": env.allowed_direction,
        "target_band_lower": env.target_exposure_band.lower,
        "target_band_upper": env.target_exposure_band.upper,
        "band_width": round(band_width, 3),
        
        # 生命周期
        "lifecycle_transition": lifecycle_transition,
        "superseded": False, # Mock
        
        # 新旧对照
        "legacy_direction": legacy_direction,
        "legacy_target_exposure": legacy_exposure,
        "shadow_vs_legacy_diverged": delta_class != "same_direction_same_risk",
        "decision_delta_class": delta_class
    }

    # 5. 落盘 JSONL
    os.makedirs(os.path.dirname(SHADOW_LOG_PATH), exist_ok=True)
    with open(SHADOW_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    
    print(f"[{now_iso}] Shadow Run {run_id} completed. Delta Class: {delta_class}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy_dir", type=str, default="long")
    parser.add_argument("--legacy_exp", type=float, default=0.8)
    parser.add_argument("--micro_file", type=str, required=True, help="Path to latest crypto_micro markdown")
    parser.add_argument("--macro_file", type=str, required=True, help="Path to latest policy_pressure markdown")
    parser.add_argument("--weather_file", type=str, required=True, help="Path to latest crypto_weather markdown")
    args = parser.parse_args()

    with open(args.micro_file, "r", encoding="utf-8") as f:
        micro_content = f.read()
        
    with open(args.macro_file, "r", encoding="utf-8") as f:
        macro_content = f.read()

    with open(args.weather_file, "r", encoding="utf-8") as f:
        weather_content = f.read()

    run_shadow_pass(args.legacy_dir, args.legacy_exp, micro_content, macro_content, weather_content)
