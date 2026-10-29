# VPS Specifications & Hardware Scaling Guide

This guide details the exact hardware specifications, RAM/VRAM calculations, and hosting recommendations for running **OpenCode APIs** across different usage levels—from an individual developer writing code in VS Code up to high-concurrency mass public deployments.

---

## 🧮 How to Calculate Required VPS Specs

Total server RAM/VRAM requirement is determined by three variables:
$$\text{Total Memory} = \text{Model Weights} + \text{KV Cache (Context)} + \text{System \& Gateway Overhead}$$

1. **Model Weights**:
   - 4-bit Quantized (Q4_K_M GGUF): $\approx 0.6 \text{ GB}$ to $0.7 \text{ GB}$ per billion parameters.
     - *7B model $\approx 4.5\text{ GB}$*
     - *14B model $\approx 9.0\text{ GB}$*
     - *32B model $\approx 20\text{ GB}$*
   - 16-bit Unquantized (FP16 / BF16 for vLLM): $\approx 2.0 \text{ GB}$ per billion parameters.
     - *7B model $\approx 14.5\text{ GB}$*
2. **KV Cache (Context Memory)**:
   - Memory consumed per active user session as code context fills up.
   - At 16K context, a 7B model requires $\approx 1.2\text{ GB}$ per concurrent user stream.
3. **OS & Gateway Overhead**:
   - Linux OS, Nginx, Python Uvicorn Gateway, Docker runtime: Reserve $\approx 1.5\text{ GB}$ to $2.0\text{ GB}$ RAM.

---

## 📊 Hardware Tiers at a Glance

| Level | Target Audience | Concurrent Streams | Recommended Engine | Min CPU | Min RAM | GPU VRAM | Est. Monthly Cost |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Level 1** | Individual / Solo Dev | 1 – 2 users | Ollama / llama.cpp | 2 – 4 vCPU | 8 GB | None (CPU only) | **$5 – $12 / mo** |
| **Level 2** | Small Team / Startup | 3 – 10 users | Ollama / llama.cpp | 4 – 8 vCPU | 16 – 32 GB | Optional (6–8 GB) | **$18 – $45 / mo** |
| **Level 3** | Mid-size Org / Agency | 10 – 50 users | vLLM / Ollama GPU | 8 – 16 vCPU | 32 – 64 GB | 16 – 24 GB VRAM | **$60 – $160 / mo** |
| **Level 4** | Mass Use / Public API | 50 – 500+ users | vLLM (Cluster) | 16 – 32 vCPU | 64 – 128 GB | 48 – 80 GB+ (A100/H100) | **$250 – $900+ / mo** |

---

## 🔍 Detailed Specifications by Usage Level

### 🟢 Level 1: Individual Developer / Solo Hobbyist
> **Target**: You want a private coding assistant for your own IDE (VS Code, Cursor, Neovim) or Discord bot without paying monthly OpenAI subscriptions.

- **Concurrent Users**: 1 – 2 simultaneous requests.
- **Recommended Model**:
  - `qwen2.5-coder:7b` (Best code quality)
  - `qwen2.5-coder:1.5b` (If on ultra-budget $4/mo machine)
- **Engine**: **Ollama** or **llama.cpp** (CPU mode).
- **Minimum Specs**:
  - **CPU**: 2 to 4 vCPUs (Modern AMD EPYC, Intel Xeon, or ARM Ampere Altra).
  - **RAM**: 8 GB DDR4 / DDR5 (Leaves ~3GB headroom for OS and caching).
  - **Storage**: 40 GB NVMe SSD (High random read speeds are crucial for model loading).
  - **Bandwidth**: 100 Mbps – 1 Gbps (Token streaming requires minimal bandwidth, ~10 KB/s per stream).
  - **GPU**: Not required.
- **Expected Speed**:
  - `qwen2.5-coder:7b`: ~8 – 16 tokens/second (comfortable reading speed).
  - `qwen2.5-coder:1.5b`: ~35 – 55 tokens/second (near instant).
- **Recommended Cloud Providers**:
  - **Hetzner Cloud**: CAX11 / CPX21 ($5 – $9/mo) — *Best value in Europe/US*.
  - **DigitalOcean**: Basic Droplet 8GB RAM ($48/mo) or Droplet with NVMe.
  - **OVHcloud**: VPS Starter / Value 8GB ($8 – $12/mo).
  - **Contabo**: Cloud VPS S (6 vCPU, 8GB RAM for ~$6/mo).

---

### 🟡 Level 2: Small Team / Startup (3 – 10 Developers)
> **Target**: A development team sharing an internal API endpoint for PR reviews, coding help, and continuous integration scripts.

- **Concurrent Users**: 3 – 10 simultaneous requests.
- **Recommended Models**:
  - `qwen2.5-coder:7b` (Primary general coder)
  - `deepseek-coder:6.7b` (Alternative review model)
- **Engine**: **Ollama** with `OLLAMA_NUM_PARALLEL=4` or **llama.cpp** with `--cont-batching`.
- **Minimum Specs (CPU-Only Setup)**:
  - **CPU**: 8 to 16 vCPUs (High clock speed >3.0 GHz preferred).
  - **RAM**: 16 GB to 32 GB DDR5 RAM.
  - **Storage**: 80 GB NVMe PCIe 4.0.
  - **Network**: 1 Gbps port.
- **Alternative Specs (Budget GPU VPS)**:
  - **GPU**: 1x NVIDIA RTX 3060 (12GB VRAM) or RTX 4060 Ti (16GB VRAM) or NVIDIA T4 (16GB).
  - **RAM**: 16 GB System RAM.
  - **Speed with GPU**: ~60 – 85 tokens/second total throughput.
- **Recommended Cloud Providers**:
  - **Hetzner Cloud**: CPX41 (8 vCPUs, 16GB RAM for ~$30/mo) or Dedicated Server EX44.
  - **RunPod / Vast.ai**: Community Cloud 1x RTX 3090/4090 ($0.25 – $0.35/hour $\approx$ $35 – $70/mo if spot/on-demand).
  - **Linode / Akamai**: Dedicated 16GB ($72/mo).

---

### 🟠 Level 3: Mid-Size Organization / Agency (10 – 50 Users)
> **Target**: Multiple engineering squads, automated QA test generators, and Discord/Slack bots querying continuously throughout the workday.

- **Concurrent Users**: 10 – 50 simultaneous requests.
- **Recommended Models**:
  - `qwen2.5-coder:14b` (Higher intelligence for multi-file refactoring)
  - `deepseek-coder-v2:16b` (Deep architectural reasoning)
  - `qwen2.5-coder:7b` (High-speed autocomplete)
- **Engine**: **vLLM** (`engines/vllm/docker-compose.yml`) utilizing PagedAttention and continuous batching.
- **Minimum Specs**:
  - **GPU**: 1x NVIDIA A10G (24GB VRAM), NVIDIA L4 (24GB VRAM), or RTX 3090 / 4090 (24GB VRAM).
  - **System RAM**: 32 GB to 64 GB.
  - **CPU**: 8 to 16 Cores.
  - **Storage**: 150 GB – 250 GB NVMe SSD.
  - **Network**: 1 Gbps – 2.5 Gbps unmetered.
- **Expected Speed**:
  - 150 – 350 tokens/second aggregate cluster throughput across all active streams.
- **Recommended Cloud Providers**:
  - **Lambda Labs**: 1x A10 ($0.60/hour $\approx$ $140/mo for regular business hours).
  - **RunPod Secure Cloud**: 1x RTX 4090 24GB ($0.44/hour $\approx$ $95/mo reserved).
  - **Hetzner Server Auction**: Dedicated server with GPU ($65 – $95/mo).
  - **AWS EC2**: `g5.xlarge` (1x A10G 24GB VRAM, 4 vCPU, 16GB RAM $\approx$ $150 – $220/mo).

---

### 🔴 Level 4: Mass Use / Public API / Enterprise (50 – 500+ Concurrent Users)
> **Target**: Running a public coding API, a high-traffic SaaS integration, or an organization with hundreds of developers and automated CI pipelines.

- **Concurrent Users**: 50 to 500+ simultaneous requests.
- **Recommended Models**:
  - `qwen2.5-coder:32b` (GPT-4o benchmark tier)
  - `qwen2.5-coder:14b` or `qwen2.5-coder:7b` (High concurrency endpoints)
- **Engine**: **vLLM Multi-GPU Tensor Parallelism** with `ray` worker backend + Nginx load balancing.
- **Minimum Specs**:
  - **GPU**: 2x to 4x NVIDIA A100 (80GB VRAM) or 2x NVIDIA H100 (80GB SXM5) or 4x NVIDIA L40S (48GB).
  - **System RAM**: 128 GB to 256 GB ECC DDR5.
  - **CPU**: 32 to 64 Cores (AMD EPYC 9004 series or Intel Xeon Platinum).
  - **Storage**: 500 GB – 1 TB Enterprise NVMe (U.2 / U.3 with >7,000 MB/s read).
  - **Network**: 10 Gbps redundant uplink.
- **Expected Speed**:
  - 1,200 – 4,000+ tokens/second aggregate throughput.
  - Sub-150ms Time-To-First-Token (TTFT) even under 100+ concurrent requests.
- **Recommended Cloud Providers**:
  - **Lambda Labs / CoreWeave**: 8x A100 / H100 clusters.
  - **RunPod Secure Cloud**: 2x or 4x A100 80GB instances.
  - **Google Cloud Platform (GCP)**: `a2-highgpu-1g` / `a2-ultragpu-1g`.
  - **AWS EC2**: `p4de.24xlarge` or `g6e.12xlarge` (NVIDIA L40S).

---

## 💡 Practical Hardware Tips & Optimization Tricks

### 1. NVMe Storage vs Standard SATA SSD
AI models are massive binary weight files (4GB to 30GB+). When the engine boots or swaps models:
- **Standard HDD/SATA SSD**: Takes 45 – 90 seconds to load weights into RAM.
- **PCIe 4.0 NVMe**: Loads a 7B model into RAM in **under 1.8 seconds**.
*Always choose NVMe storage for your VPS.*

### 2. Swap Space: Never Run Out of Memory (OOM)
If your VPS runs out of physical RAM, the Linux Kernel OOM killer will terminate Ollama or the Python Gateway instantly.
To prevent crashes during unexpected traffic spikes, configure an 8GB NVMe swap file:
```bash
# Create an 8GB emergency swap file
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 3. CPU AVX2 / AVX-512 Support
When running without a GPU (Level 1 & Level 2), model inference relies on vector CPU extensions.
Verify your VPS processor supports AVX2:
```bash
grep -E 'avx|avx2|avx512' /proc/cpuinfo
```
Modern AMD EPYC (Zen 3/4) and Intel Xeon processors with AVX2 run inference **3x to 5x faster** than older legacy CPUs.

### 4. GPU Layer Offloading (Hybrid Mode)
If you have a modest GPU with only 4GB – 8GB VRAM:
Ollama automatically splits model layers. For instance, with a 7B model (33 layers):
- 22 layers offloaded to GPU VRAM.
- 11 layers offloaded to System RAM.
This gives you ~70% of pure GPU speed without requiring expensive enterprise hardware.
