# Supported Models Matrix & Hardware Guide

**OpenCode APIs** allows you to run any open-weight code generation and reasoning model. Below is the comprehensive matrix of supported free models, categorized by VPS hardware tier.

> 💡 **Need deep VPS hosting advice?** Check out [**VPS_SPECS.md**](VPS_SPECS.md) for full RAM formulas, CPU vs GPU benchmarks, and provider pricing from solo dev ($5/mo) to mass enterprise ($900/mo).

---

## 📊 Quick Hardware Tier Summary

| Tier | Min RAM | GPU VRAM | Recommended Models | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1 (Budget VPS)** | 2GB – 4GB | None (CPU only) | `qwen2.5-coder:0.5b`, `qwen2.5-coder:1.5b`, `llama3.2:1b` | Fast code autocomplete, shell scripting, small scripts |
| **Tier 2 (Standard VPS)** | 8GB – 16GB | 6GB – 8GB (optional) | `qwen2.5-coder:7b`, `deepseek-coder:6.7b`, `codellama:7b` | Full stack web dev, refactoring, bug fixing, test writing |
| **Tier 3 (Powerhouse VPS)**| 32GB – 64GB | 16GB – 24GB (Nvidia) | `qwen2.5-coder:14b`, `deepseek-coder-v2:16b`, `qwen2.5-coder:32b` | Complex architecture, large multi-file diffs, full codebases |

---

## 🏆 Detailed Model Directory

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
