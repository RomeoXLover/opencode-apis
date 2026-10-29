#!/usr/bin/env python3
"""
OpenCode APIs - Python Integration Example
Demonstrates how to use the official OpenAI Python SDK with your self-hosted VPS endpoint.
Install SDK: pip install openai
"""
import os
from openai import OpenAI

# 1. Point base_url to your VPS IP or Domain
VPS_URL = os.getenv("OPENCODE_API_URL", "http://127.0.0.1:8000/v1")
API_KEY = os.getenv("OPENCODE_API_KEY", "sk-opencode-sample-key")

client = OpenAI(
    base_url=VPS_URL,
    api_key=API_KEY
)

def run_chat_example():
    print(f"Connecting to OpenCode VPS API at: {VPS_URL}...\n")

    # 1. Non-streaming call
    print("--- [Standard Request] ---")
    response = client.chat.completions.create(
        model="qwen2.5-coder:7b",
        messages=[
            {"role": "system", "content": "You are a professional software architect."},
            {"role": "user", "content": "Give 3 clean architecture rules for microservices."}
        ],
        temperature=0.3,
        max_tokens=400
    )
    print(response.choices[0].message.content)
    print("\n--------------------------\n")

    # 2. Streaming call
    print("--- [Streaming Response] ---")
    stream = client.chat.completions.create(
        model="qwen2.5-coder:7b",
        messages=[
            {"role": "user", "content": "Write a TypeScript debounce function."}
        ],
        temperature=0.2,
        stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        print(delta, end="", flush=True)
    print("\n--------------------------")

if __name__ == "__main__":
    run_chat_example()
