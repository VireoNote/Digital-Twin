#!/bin/bash
# run_shadow_pipeline.sh
# This script wraps the shadow compiler daemon for easy cron scheduling.
# It automatically picks the most recent ingest artifacts.

set -e

WORKSPACE="/home/liwu/digital_twin"
VENV_PYTHON="$WORKSPACE/venv/bin/python"
DAEMON_SCRIPT="$WORKSPACE/06_Governance/shadow/shadow_compiler_daemon.py"
INGEST_DIR="$WORKSPACE/01_Ingest"

# We need the 03_State directory in PYTHONPATH so the daemon can import the 4.0 modules
export PYTHONPATH="$WORKSPACE/03_State:$PYTHONPATH"

# Find latest micro and macro files
LATEST_MICRO=$(ls -t "$INGEST_DIR"/crypto_micro_*.md 2>/dev/null | head -n 1)
LATEST_MACRO=$(ls -t "$INGEST_DIR"/policy_pressure_*.md 2>/dev/null | head -n 1)

if [ -z "$LATEST_MICRO" ] || [ -z "$LATEST_MACRO" ]; then
    echo "[Error] Could not find latest ingest artifacts."
    exit 1
fi

# Here you can plug in the actual legacy state reading logic.
# For now, we mock the legacy system's output (e.g. legacy system is always structurally long).
LEGACY_DIR="long"
LEGACY_EXP=0.8

echo "Starting Shadow Run at $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
echo "Using Micro: $LATEST_MICRO"
echo "Using Macro: $LATEST_MACRO"

$VENV_PYTHON "$DAEMON_SCRIPT" \
    --legacy_dir "$LEGACY_DIR" \
    --legacy_exp "$LEGACY_EXP" \
    --micro_file "$LATEST_MICRO" \
    --macro_file "$LATEST_MACRO"

echo "Shadow Run completed successfully."
