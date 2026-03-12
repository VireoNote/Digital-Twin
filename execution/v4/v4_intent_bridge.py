import json
import os
from datetime import datetime, timezone

# 物理路径定义
WORKSPACE = "/home/liwu/digital_twin"
DECISION_DIR = os.path.join(WORKSPACE, "04_Decision")
EXECUTION_DIR = os.path.join(WORKSPACE, "05_Execution")

def run_intent_bridge():
    print(f"\n[Intent Bridge] Calculating Execution Deltas...")
    
    # 1. 加载 4.0 官方政策
    policy_path = os.path.join(DECISION_DIR, "v4_policy_envelope.json")
    if not os.path.exists(policy_path):
        print("  - [Error] v4_policy_envelope.json not found.")
        return
        
    with open(policy_path, "r") as f:
        policy = json.load(f)
        
    band_lower = policy["target_exposure_band"]["lower"]
    band_upper = policy["target_exposure_band"]["upper"]
    allowed_dir = policy["allowed_direction"]
    
    # 2. 获取当前物理仓位 (Mocking from system state)
    # 在真实系统中，这里会调用交易所 API 或读取账户快照
    current_exposure = 0.8 # 假设当前仍处于旧系统的重仓状态
    
    print(f"  - Current Exposure: {current_exposure}")
    print(f"  - Target 4.0 Band: [{band_lower}, {band_upper}] ({allowed_dir.upper()})")
    
    # 3. 计算受控 Delta
    delta = 0.0
    action = "HOLD"
    
    if current_exposure > band_upper:
        delta = band_upper - current_exposure
        action = "REDUCE (减仓)"
    elif current_exposure < band_lower:
        delta = band_lower - current_exposure
        action = "INCREASE (加仓)"
    else:
        action = "MAINTAIN (维持)"
        
    # 4. 生成执行意图对象 (Stage 5 输入)
    execution_intent = {
        "intent_id": f"exec_{int(datetime.now().timestamp())}",
        "envelope_id": policy["envelope_id"],
        "asset": "BTC",
        "current_exposure": current_exposure,
        "target_band": [band_lower, band_upper],
        "required_delta": round(delta, 4),
        "recommended_action": action,
        "urgency": policy["execution_urgency"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    output_path = os.path.join(EXECUTION_DIR, "v4_execution_intent.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(execution_intent, f, indent=2)
        
    print(f"  - Recommended Action: {action} | Delta: {delta:.4f}")
    print(f"  - Execution Intent saved to: {output_path}")

if __name__ == "__main__":
    run_intent_bridge()
