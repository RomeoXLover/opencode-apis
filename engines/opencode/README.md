# OpenCode Package Engine (`@opencode/cli`)

The backend engine is powered directly by the official **OpenCode** package ([opencode.ai](https://opencode.ai) / `@opencode/cli`).

## Key Features
- **Headless Server Mode**: Runs with `opencode serve --hostname 0.0.0.0 --port 4096`.
- **Built-in Free Models**: Provides instant access to free coding models such as `opencode/flint-40b-free` without requiring local model weights download.
- **REST & SSE Endpoints**: Supports `/api/session`, `/api/model`, `/api/experimental/generate/text`, and web console pairing links.
- **Cross-Platform**: Runs natively via standalone binary or global npm package (`npm i -g @opencode/cli`).
