import json
import os
import uuid
from datetime import datetime, timezone
from typing import List

# 导入成熟的逻辑模块
from v4_multi_court_demo import (
    create_mock_evidence, create_mock_cognition, 
    run_multi_court_validation, compile_policy_envelope
)
from schemas.v4_core import Hypothesis, PolicyEnvelope, EnvelopeStatus
from lifecycle_runner import LifecycleRunner

# 物理路径定义
WORKSPACE = "/home/liwu/digital_twin"
INGEST_DIR = os.path.join(WORKSPACE, "01_Ingest")
DECISION_DIR = os.path.join(WORKSPACE, "04_Decision")
REGISTRY_PATH = os.path.join(WORKSPACE, "03_State/active_state/registry.json")

def load_latest_file(pattern: str) -> str:
    import glob
    files = [f for f in glob.glob(os.path.join(INGEST_DIR, pattern))]
    if not files:
        raise FileNotFoundError(f"No files found for pattern: {pattern}")
    return sorted(files)[-1] # 按名称拿最晚的

def save_registry(hypotheses: List[Hypothesis], envelopes: List[PolicyEnvelope]):
    data = {
        "active_hypotheses": [h.model_dump(mode='json') for h in hypotheses if h.status != "archived"],
        "active_envelopes": [e.model_dump(mode='json') for e in envelopes if e.status not in ["executed", "expired", "superseded"]]
    }
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def run_production_pulse():
    print(f"\n[Production Pulse] Starting 4.0 Decision Cycle at {datetime.now(timezone.utc).isoformat()}")
    
    # 1. 摄入最新真实证据
    micro_path = load_latest_file("crypto_micro_*.md")
    macro_path = load_latest_file("policy_pressure_*.md")
    weather_path = load_latest_file("crypto_weather_*.md")
    
    print(f"  - Using Evidence: {os.path.basename(micro_path)}, {os.path.basename(macro_path)}, {os.path.basename(weather_path)}")
    
    with open(micro_path, "r") as f: micro_raw = f.read()
    with open(macro_path, "r") as f: macro_raw = f.read()
    with open(weather_path, "r") as f: weather_raw = f.read()
    
    ev_micro = create_mock_evidence("crypto_micro", micro_raw)
    ev_macro = create_mock_evidence("policy_pressure", macro_raw)
    ev_weather = create_mock_evidence("crypto_weather", weather_raw)
    
    # 2. 认知生成 (保持 LONG 意图模拟，或者您可以改为读取真实 Legacy 倾向)
    hyp, intent = create_mock_cognition("long", "Production Analysis Cycle")
    
    # 3. 四路法庭交叉质询
    report = run_multi_court_validation(hyp, intent, [ev_micro, ev_macro, ev_weather])
    print(f"  - Validation Support: {report.support_score:.2f}, Contra: {report.contradiction_score:.2f}")
    
    # 4. 政策编译 (产出 PolicyEnvelope)
    env = compile_policy_envelope(hyp, intent, report)
    print(f"  - Compiled Policy: {env.compiler_mode.value} | Band: [{env.target_exposure_band.lower}, {env.target_exposure_band.upper}]")
    
    # 5. 生命周期状态机运作 (处理激活与级联)
    runner = LifecycleRunner()
    # 这里模拟从 registry 加载之前的对象，目前我们简化为只处理本轮产出的
    result = runner.run_cycle([hyp], {hyp.hypothesis_id: report}, {hyp.hypothesis_id: [env]})
    
    # 6. 正式发布决策输出 (供执行层消费)
    output_path = os.path.join(DECISION_DIR, "v4_policy_envelope.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(env.model_dump(mode='json'), f, indent=2)
    
    # 7. 持久化到注册表
    save_registry([hyp], [env])
    
    print(f"  - Production Decision persistent at: {output_path}")
    return env

if __name__ == "__main__":
    run_production_pulse()
