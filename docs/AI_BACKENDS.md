# AI Backends / AI 后端

ACE-Omega can run without AI. AI is optional and mainly used for natural-language interpretation.

Supported modes:

1. `openai` - OpenAI-compatible API.
2. `ollama` - local Ollama server.
3. `gguf` - local GGUF model through llama.cpp-style runtime.
4. `fallback` - simple rule-based fallback.

## Security notes / 安全说明

API keys should never be committed to GitHub. The app may save local configuration to `config.yaml`; this file is ignored by `.gitignore`.

Do not send private, unpublished or sensitive literature data to external APIs unless you understand the privacy and legal risks.

不要把 API key 提交到 GitHub。不要在没有理解风险的情况下，把私有、未发表或敏感文献数据发送到外部 API。
