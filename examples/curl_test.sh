#!/usr/bin/env bash
# OpenCode APIs - Example cURL Requests

# Replace with your actual VPS IP or Domain
HOST="http://127.0.0.1:8000"
API_KEY="sk-opencode-sample-key"

echo "=== 1. Health Check ==="
curl -s "$HOST/health" | jq .

echo -e "\n=== 2. List Models ==="
curl -s "$HOST/v1/models" | jq .

echo -e "\n=== 3. Non-Streaming Chat Completion ==="
curl -s -X POST "$HOST/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "qwen2.5-coder:7b",
    "messages": [
      {"role": "system", "content": "You are a concise code helper."},
      {"role": "user", "content": "Write a 3-line Python function to reverse a string."}
    ],
    "temperature": 0.2
  }' | jq .

echo -e "\n=== 4. Streaming SSE Chat Completion ==="
curl -N -X POST "$HOST/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "qwen2.5-coder:7b",
    "messages": [
      {"role": "user", "content": "Explain what a pointer is in C in 2 sentences."}
    ],
    "stream": true
  }'
echo ""
