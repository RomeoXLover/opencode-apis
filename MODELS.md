# Supported Models Matrix & Hardware Guide

**OpenCode APIs** allows you to run any open-weight code generation and reasoning model, while also supporting closed flagship models (like Claude 3.5 Sonnet and GPT-4o) via its integrated **Hybrid Upstream Router**.

> 💡 **Need deep VPS hosting advice?** Check out [**VPS_SPECS.md**](VPS_SPECS.md) for full RAM formulas, CPU vs GPU benchmarks, and provider pricing from solo dev ($5/mo) to mass enterprise ($900/mo).

---

## ⚡ What About Claude 3.5 Sonnet, GPT-4o & Gemini?

Many developers ask: **"Can I download Claude 3.5 Sonnet or GPT-4o weights onto my VPS?"**

### 1. Closed-Source vs Open-Source Models
- **Proprietary (Closed) Models**: **Claude 3.5 Sonnet** (Anthropic), **GPT-4o** (OpenAI), and **Gemini 1.5 Pro** (Google) do **NOT** have downloadable weights (`.gguf` or `.safetensors`). Their model weights are guarded proprietary trade secrets hosted in multi-billion dollar datacenters. Nobody can run them directly on raw VPS hardware without an API.
- **Open-Weight Models**: **Qwen 2.5 Coder**, **DeepSeek Coder**, **CodeLlama**, and **Llama 3.3** are 100% open-weight. You can download their full weights directly to your VPS and run them indefinitely with **zero subscription costs**, total privacy, and offline autonomy.

### 2. How OpenCode APIs Solves This: **Hybrid Upstream Router**
OpenCode APIs includes a built-in proxy router. If you want a **single unified API endpoint** on your VPS for both free local models and frontier cloud models:
1. Put your OpenRouter or Anthropic key in `.env`:
   ```properties
   UPSTREAM_API_KEY=sk-or-v1-YOUR_KEY
   ```
2. Your VPS API now seamlessly routes both:
   - Request `qwen2.5-coder:7b` ➔ Runs **100% locally** on your VPS for free.
   - Request `claude-3-5-sonnet` or `gpt-4o` ➔ The gateway securely proxies the request upstream with real-time SSE streaming.

### 3. Open-Source Alternatives that Rival Claude 3.5 Sonnet
If you want to stay 100% self-hosted without paying cloud API fees, here is how open models compare:

| Proprietary Cloud Model | Open-Source Self-Hosted Equivalent | Local VRAM / RAM Required | How Close Is It? |
| :--- | :--- | :--- | :--- |
| **Claude 3.5 Sonnet** | **`qwen2.5-coder:32b`** | 20GB – 24GB VRAM | **Near Parity**: Matches or beats Sonnet on HumanEval (92.7% vs 93.7%) and MultiPL-E. |
| **GPT-4o** | **`deepseek-coder-v2:16b`** | 10GB – 12GB VRAM | **Excellent**: MoE architecture provides elite reasoning and code infilling. |
| **GPT-4o-mini** | **`qwen2.5-coder:7b`** | 5GB – 6GB VRAM / RAM | **Equivalent**: Beats GPT-4o-mini on multiple programming benchmarks. |

---

## 📊 Quick Hardware Tier Summary

| Tier | Min RAM | GPU VRAM | Recommended Models | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1 (Budget VPS)** | 2GB – 4GB | None (CPU only) | `qwen2.5-coder:0.5b`, `qwen2.5-coder:1.5b`, `llama3.2:1b` | Fast code autocomplete, shell scripting, small scripts |
| **Tier 2 (Standard VPS)** | 8GB – 16GB | 6GB – 8GB (optional) | `qwen2.5-coder:7b`, `deepseek-coder:6.7b`, `codellama:7b` | Full stack web dev, refactoring, bug fixing, test writing |
| **Tier 3 (Powerhouse VPS)**| 32GB – 64GB | 16GB – 24GB (Nvidia) | `qwen2.5-coder:14b`, `deepseek-coder-v2:16b`, `qwen2.5-coder:32b` | Complex architecture, large multi-file diffs, full codebases |

---

## 🏆 Detailed Model Directory

### 0. OpenCode Native Models (Zero-Download Cloud Inference)
Powered out-of-the-box by the **OpenCode package** without requiring gigabytes of model weights to be downloaded:

#### • `opencode/flint-40b-free` *(Default OpenCode Model)*
- **Parameters**: 40 Billion
- **VPS RAM Requirement**: Minimal (< 500 MB RAM needed by OpenCode process)
- **Features**: Free built-in code completion and reasoning model provided through OpenCode.
- **Best For**: General programming, refactoring, bash automation, code exploration.

---

### 1. Qwen 2.5 Coder Series (Alibaba Cloud) — *Top Recommendation*
The current gold standard in open-source coding models, outperforming many proprietary APIs on HumanEval, MultiPL-E, and SWE-bench.

#### • `qwen2.5-coder:0.5b`
- **Parameters**: 0.49 Billion
- **RAM Requirement**: ~500 MB (Runs on even a $3/month 1-core VPS!)
- **Context Window**: 32,768 tokens
- **Speed**: Ultra fast (>60 tokens/sec on CPU)
- **Install Command**: `ollama pull qwen2.5-coder:0.5b`
- **Best For**: Real-time IDE tab autocompletion, commit message generation, regex help.

#### • `qwen2.5-coder:1.5b`
- **Parameters**: 1.54 Billion
- **RAM Requirement**: ~1.3 GB
- **Context Window**: 32,768 tokens
- **Speed**: Very fast (~30-45 tokens/sec on modern CPU)
- **Install Command**: `ollama pull qwen2.5-coder:1.5b`
- **Best For**: Function generation, utility scripts, basic debugging.

#### • `qwen2.5-coder:7b` *(Recommended Default)*
- **Parameters**: 7.61 Billion
- **RAM Requirement**: ~5.2 GB RAM (or 6GB VRAM)
- **Context Window**: 131,072 tokens (Long context)
- **Speed**: ~12-18 tokens/sec on CPU, ~65+ tokens/sec on GPU
- **Install Command**: `ollama pull qwen2.5-coder:7b`
- **Best For**: Everyday full-stack development, Python, JavaScript, TypeScript, Go, Rust, Java, C++, SQL.

#### • `qwen2.5-coder:14b`
- **Parameters**: 14.7 Billion
- **RAM Requirement**: ~9.5 GB RAM (or 12GB VRAM)
- **Context Window**: 131,072 tokens
- **Install Command**: `ollama pull qwen2.5-coder:14b`
- **Best For**: Advanced algorithm design, multi-file refactoring, comprehensive unit test generation.

#### • `qwen2.5-coder:32b`
- **Parameters**: 32.5 Billion
- **RAM Requirement**: ~20 GB RAM (or 24GB VRAM like RTX 3090/4090)
- **Context Window**: 131,072 tokens
- **Install Command**: `ollama pull qwen2.5-coder:32b`
- **Best For**: Enterprise-grade code generation, rivaling GPT-4o and Claude 3.5 Sonnet on coding benchmarks.

---

### 2. DeepSeek-Coder Series
Trained on 2+ trillion tokens of code and natural language across 80+ programming languages.

#### • `deepseek-coder:6.7b`
- **Parameters**: 6.7 Billion
- **RAM Requirement**: ~4.5 GB
- **Context Window**: 16,384 tokens
- **Install Command**: `ollama pull deepseek-coder:6.7b`
- **Best For**: Project-level code completion, infilling (Fill-In-The-Middle), code explanation.

#### • `deepseek-coder-v2:16b`
- **Parameters**: 16 Billion (Mixture-of-Experts: 2.4B active parameters)
- **RAM Requirement**: ~9 GB
- **Context Window**: 128,000 tokens
- **Install Command**: `ollama pull deepseek-coder-v2:16b`
- **Best For**: Math reasoning, deep bug hunting, complex algorithmic challenges.

---

### 3. Meta Code Llama Series
Meta's specialized coding foundation trained on top of Llama 2.

#### • `codellama:7b`
- **Parameters**: 7 Billion
- **RAM Requirement**: ~4.8 GB
- **Context Window**: 16,384 tokens
- **Install Command**: `ollama pull codellama:7b`
- **Best For**: Python / C++ code synthesis, docstring generation.

---

### 4. BigCode StarCoder 2
Trained by the BigCode consortium (Hugging Face & ServiceNow) on 600+ programming languages from GitHub.

#### • `starcoder2:3b`
- **Parameters**: 3 Billion
- **RAM Requirement**: ~2.5 GB
- **Install Command**: `ollama pull starcoder2:3b`
- **Best For**: Fast, low-latency code completion.

#### • `starcoder2:7b`
- **Parameters**: 7 Billion
- **RAM Requirement**: ~5 GB
- **Install Command**: `ollama pull starcoder2:7b`
- **Best For**: Syntax-accurate code generation in niche languages (Lua, Haskell, Zig, Elixir, Julia).

---

### 5. Meta Llama 3.2 Series (Compact Multitaskers)
Extremely fast, modern compact models for lightweight server setups.

#### • `llama3.2:1b` & `llama3.2:3b`
- **RAM Requirement**: 1.1 GB (1B) / 2.2 GB (3B)
- **Context Window**: 128,000 tokens
- **Install Command**: `ollama pull llama3.2:3b`
- **Best For**: Quick natural language-to-code translation, summarization, tool calling.

---

## 🔄 How to Switch Models in Your Application

Because **OpenCode APIs** dynamically queries your installed models, you never have to reconfigure the server when switching models. Simply change the `"model"` string in your request payload:

```bash
# Query Qwen 2.5 Coder 7B
curl http://YOUR_VPS_IP/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen2.5-coder:7b", "messages": [{"role": "user", "content": "hello"}]}'

# Query DeepSeek Coder 6.7B
curl http://YOUR_VPS_IP/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-coder:6.7b", "messages": [{"role": "user", "content": "hello"}]}'
```
