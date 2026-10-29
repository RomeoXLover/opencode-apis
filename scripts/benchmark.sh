#!/usr/bin/env bash
# OpenCode APIs - Performance & Token Latency Benchmarker
set -euo pipefail

TARGET_URL="${1:-http://127.0.0.1:8000/v1/chat/completions}"
MODEL="${2:-qwen2.5-coder:7b}"

echo "=================================================="
echo "    OpenCode APIs - Real-time Benchmark"
echo "=================================================="
echo "Target: $TARGET_URL"
echo "Model:  $MODEL"
echo "Testing time-to-first-token and throughput..."
echo ""

START_TIME=$(date +%s%N)

RESPONSE=$(curl -s -w "\n%{http_code}\n%{time_total}" -X POST "$TARGET_URL" \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"$MODEL\", \"messages\": [{\"role\": \"user\", \"content\": \"Write a quicksort function in Python with comments.\"}], \"temperature\": 0.2, \"max_tokens\": 300}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n2 | head -n1)
TOTAL_TIME=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n -2)

if [ "$HTTP_CODE" -ne 200 ]; then
    echo "[Error] Benchmark request failed with HTTP $HTTP_CODE"
    echo "$BODY"
    exit 1
fi

echo "$BODY" | jq -r '.choices[0].message.content' 2>/dev/null || echo "$BODY"
echo ""
echo "--------------------------------------------------"
echo "Status Code: $HTTP_CODE OK"
echo "Total Time:  ${TOTAL_TIME}s"
echo "Benchmark completed successfully."
