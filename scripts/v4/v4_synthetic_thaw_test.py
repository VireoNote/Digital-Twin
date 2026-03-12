import json
import re
import os
from datetime import datetime, timezone
from typing import Dict, Any

# 引入核心逻辑组件
from v4_multi_court_demo import (
    create_mock_evidence, create_mock_cognition, 
    run_multi_court_validation, compile_policy_envelope
)
from schemas.v4_core import HypothesisStatus
from lifecycle_runner import LifecycleRunner

# 测试记录路径
THAW_TEST_LOG = "/home/liwu/digital_twin/06_Governance/shadow/thaw_tests.jsonl"

def get_thaw_class(mode: str) -> str:
    if mode == "frozen": return "NO_THAW"
    if mode == "tactical_only": return "TACTICAL_THAW"
    if mode == "structural_allowed": return "STRUCTURAL_THAW"
    return "UNKNOWN"

def run_thaw_scenario(id: str, velocity: float, tips: float, etf_vol: int, weather_behavior: str, description: str):
    print(f"\n>>> Running Test {id}: {description}")
    
    # 构造合成 Ingest 内容
    micro_content = f"- **全网稳定币日流速 (Velocity)**: {velocity}%\n- **贝莱德现货 ETF (IBIT)**: $38.96 (单日交易量: {etf_vol:,})"
    if "Spot Strong" in description or "Offensive Alpha" in description or "Strong Spot" in description:
        micro_content += "\n🟢 【现货支撑】观察到 ETF 大量申购，资金属性健康。"
        
    macro_content = f"- **当前 TIPS 收益率**: {tips}%"
    weather_content = f"## 市场资金行为推演\n**当前资金面状态**: {weather_behavior}"
    
    ev_micro = create_mock_evidence("crypto_micro", micro_content)
    ev_macro = create_mock_evidence("policy_pressure", macro_content)
    ev_weather = create_mock_evidence("crypto_weather", weather_content)
    
    # 在解冻测试中，我们统一模拟 LLM 具有看多意图 (LONG)，看系统是否放行
    hyp, intent = create_mock_cognition("long", f"Thaw Test {id}")
    
    # 1. Validation (四合一逻辑)
    report = run_multi_court_validation(hyp, intent, [ev_micro, ev_macro, ev_weather])
    
    # 2. Compilation
    env = compile_policy_envelope(hyp, intent, report)
    
    # 3. Lifecycle
    runner = LifecycleRunner()
    result = runner.run_cycle([hyp], {hyp.hypothesis_id: report}, {hyp.hypothesis_id: [env]})
    
    # 提取分型
    split_type = "None"
    for note in report.validator_notes:
        if "SPLIT COURT DETECTED" in note:
            split_type = note.split(": ")[1].split(" (")[0]

    # 4. 构建结果记录
    test_result = {
        "test_id": id,
        "description": description,
        "input_velocity": velocity,
        "input_tips": tips,
        "input_etf": etf_vol,
        "split_court_detected": "SPLIT COURT DETECTED" in "".join(report.validator_notes),
        "split_court_type": split_type,
        "support_score": round(report.support_score, 3),
        "contradiction_score": round(report.contradiction_score, 3),
        "compiler_mode": env.compiler_mode.value,
        "target_band": [env.target_exposure_band.lower, env.target_exposure_band.upper],
        "hypothesis_status_after": hyp.status.value,
        "thaw_class": get_thaw_class(env.compiler_mode.value),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # 打印核心输出
    print(f"    [Result] Thaw Class: {test_result['thaw_class']}")
    print(f"    [Result] Split Type: {test_result['split_court_type']}")
    print(f"    [Result] Band      : {test_result['target_band']}")
    print(f"    [Result] Hyp Status: {test_result['hypothesis_status_after']}")
    
    with open(THAW_TEST_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(test_result) + "\n")

def main():
    print("==================================================")
    print("   ARCHITECTURE 4.2 - IMPACT TEST (NEW JUDGE)")
    print("==================================================\n")

    # 按优先级顺序执行
    
    # Test B：Macro 先改善 (背景改善，场内未确认)
    run_thaw_scenario("B", 2.6, 1.1, 15000000, "Short Build-up", "Macro Support, Micro/Spot Reject")
    
    # Test A：Micro 先改善 (短线改善，大背景压制)
    run_thaw_scenario("A", 5.6, 1.8, 15000000, "Short Build-up", "Micro Support, Macro/Spot Reject")
    
    # Test D：边界改善 + 现货确认 (验证第一刀的效果)
    # 临界点: Velocity 4.8 (不到5), TIPS 1.45 (到1.5), 增加 Strong Spot
    run_thaw_scenario("D", 4.8, 1.45, 25000000, "Long Build-up", "Boundary Case + Strong Spot Support")
    
    # Test E: 极端特赦测试 (双防守法官反对，双进攻法官支持)
    # Velocity 2.6 (死水), TIPS 1.8 (高压) | Spot 30M, Weather Short Covering
    run_thaw_scenario("E", 2.6, 1.8, 30000000, "Short Covering", "Dual Reject but Offensive Alpha (Squeeze Play)")

    # Test C：全放行
    run_thaw_scenario("C", 6.5, 1.1, 30000000, "Long Build-up", "Dual Support + Spot Strong")

    print("\n==================================================")
    print(f" TEST LOG SAVED TO: {THAW_TEST_LOG}")
    print("==================================================")

if __name__ == "__main__":
    main()
