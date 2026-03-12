#!/bin/bash
# run_v4_production.sh (v4.2 Production)
# 职责：每 4 小时执行一次 4.0 核心决策脉搏，生成物理执行意图。

set -e

WORKSPACE="/home/liwu/digital_twin"
VENV_PYTHON="$WORKSPACE/venv/bin/python"
PROD_ENGINE="$WORKSPACE/03_State/v4_production_engine.py"
INTENT_BRIDGE="$WORKSPACE/05_Execution/v4_intent_bridge.py"
LOG_FILE="$WORKSPACE/06_Governance/production.log"

# 环境变量：确保能找到 4.0 模块
export PYTHONPATH="$WORKSPACE/03_State:$PYTHONPATH"

echo "--- [PROD PULSE] Starting Cycle: $(date -u +'%Y-%m-%dT%H:%M:%SZ') ---" >> "$LOG_FILE"

# 1. 运行 4.0 决策引擎
$VENV_PYTHON "$PROD_ENGINE" >> "$LOG_FILE" 2>&1

# 2. 运行执行桥接器 (生成 Delta)
$VENV_PYTHON "$INTENT_BRIDGE" >> "$LOG_FILE" 2>&1

echo "--- [PROD PULSE] Cycle Completed Successfully ---" >> "$LOG_FILE"
