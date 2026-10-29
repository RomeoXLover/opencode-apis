# llama.cpp Engine for Low-Spec / Budget VPS

If you are running on a budget VPS (e.g. 4GB - 16GB RAM without dedicated GPU):
- `llama.cpp` has zero Python overhead.
- Written in pure C/C++ with SIMD/AVX2/AVX-512 optimizations.
- Supports 4-bit (Q4_K_M) and 5-bit (Q5_K_M) GGUF quantizations, allowing 7B models to run comfortably in ~5GB of RAM.
- Features continuous batching and native OpenAI `/v1/chat/completions` compatibility.
