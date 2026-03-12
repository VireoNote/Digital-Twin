#!/bin/bash
# run_shadow_pipeline.sh (v4.1 - Backfill & Reconnection Edition)
# 职责：确保不漏掉任何一个时序样本，支持断线后的自动追赶。

set -e

# 辅助函数：过滤小于等于给定时间戳的文件
function filter_le() {
    local target="$1"
    while read -r line; do
        local file_ts=$(echo "$line" | grep -oE '[0-9]{8}_[0-9]{6}')
        if [[ "$file_ts" < "$target" ]] || [[ "$file_ts" == "$target" ]]; then
            echo "$line"
        fi
    done
}

WORKSPACE="/home/liwu/digital_twin"
VENV_PYTHON="$WORKSPACE/venv/bin/python"
DAEMON_SCRIPT="$WORKSPACE/06_Governance/shadow/shadow_compiler_daemon.py"
INGEST_DIR="$WORKSPACE/01_Ingest"
SHADOW_DIR="$WORKSPACE/06_Governance/shadow"
CHECKPOINT_FILE="$SHADOW_DIR/.processed_checkpoint"

# 环境变量设置
export PYTHONPATH="$WORKSPACE/03_State:$PYTHONPATH"

# 如果没有锚点文件，则从当前最新文件的前一个开始，或者处理所有。
# 为了稳妥，初次运行我们设置锚点为“空”，即处理所有未处理文件。
touch "$CHECKPOINT_FILE"
LAST_PROCESSED=$(cat "$CHECKPOINT_FILE")

echo "--- Shadow Pipeline Pulse: $(date -u +'%Y-%m-%dT%H:%M:%SZ') ---"

# 获取所有 crypto_micro 文件，并按名称（即时间）排序
MICRO_FILES=$(ls "$INGEST_DIR"/crypto_micro_*.md 2>/dev/null | sort)

if [ -z "$MICRO_FILES" ]; then
    echo "[Error] No micro artifacts found."
    exit 1
fi

COUNT=0
for FILE in $MICRO_FILES; do
    FILENAME=$(basename "$FILE")
    
    # 追赶逻辑：只处理比锚点更新的文件
    if [[ "$FILENAME" > "$LAST_PROCESSED" ]]; then
        # 提取时间戳字符串 (例如 20260307_000531)
        TS_STR=$(echo "$FILENAME" | grep -oE '[0-9]{8}_[0-9]{6}')
        
        # 寻找当时最匹配的 Macro 和 Weather 文件
        # 策略：找时间戳小于或等于当前 Micro 时间戳的最晚一个文件
        LATEST_MACRO=$(ls "$INGEST_DIR"/policy_pressure_*.md 2>/dev/null | filter_le "$TS_STR" | tail -n 1)
        LATEST_WEATHER=$(ls "$INGEST_DIR"/crypto_weather_*.md 2>/dev/null | filter_le "$TS_STR" | tail -n 1)
        
        # 如果找不到对齐文件，降级使用目录下最晚的
        [[ -z "$LATEST_MACRO" ]] && LATEST_MACRO=$(ls -t "$INGEST_DIR"/policy_pressure_*.md | head -n 1)
        [[ -z "$LATEST_WEATHER" ]] && LATEST_WEATHER=$(ls -t "$INGEST_DIR"/crypto_weather_*.md | head -n 1)

        echo "[Processing] $FILENAME (TS: $TS_STR)"
        
        # 执行影子编译
        $VENV_PYTHON "$DAEMON_SCRIPT" \
            --legacy_dir "long" \
            --legacy_exp 0.8 \
            --micro_file "$FILE" \
            --macro_file "$LATEST_MACRO" \
            --weather_file "$LATEST_WEATHER"
        
        # 更新锚点
        echo "$FILENAME" > "$CHECKPOINT_FILE"
        LAST_PROCESSED="$FILENAME"
        COUNT=$((COUNT + 1))
    fi
done

# 假死检测
LATEST_TIMESTAMP=$(ls -t "$INGEST_DIR"/crypto_micro_*.md | head -n 1 | grep -oE '[0-9]{8}_[0-9]{6}')
# 此处可添加更复杂的日期比对逻辑，目前先输出状态
echo "[Status] Catch-up complete. Processed $COUNT new samples. Current Anchor: $LAST_PROCESSED"

# 辅助函数：过滤小于等于给定时间戳的文件
function filter_le() {
    local target="$1"
    while read -r line; do
        local file_ts=$(echo "$line" | grep -oE '[0-9]{8}_[0-9]{6}')
        if [[ "$file_ts" < "$target" ]] || [[ "$file_ts" == "$target" ]]; then
            echo "$line"
        fi
    done
}
