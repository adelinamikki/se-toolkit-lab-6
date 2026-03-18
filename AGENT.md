# Agent Architecture (Task 1)

This repository contains an `agent.py` CLI that answers questions by calling an **OpenAI-compatible LLM API**.

## Provider (LLM)
- Provider: **Qwen Code API** via `qwen-code-oai-proxy`
- Endpoint: `LLM_API_BASE` + `/chat/completions`
- Authentication: `LLM_API_KEY`
- Model: `LLM_MODEL`

## Environment Configuration
The agent reads configuration from environment variables:
- `LLM_API_KEY`
- `LLM_API_BASE`
- `LLM_MODEL`

For local development, `agent.py` also attempts to load `.env.agent.secret` (if present) and only fills missing values; environment variables injected by the autochecker always take priority.

## Request/Response Shape
`agent.py` sends a chat-completions request with:
- system prompt: short instruction to answer directly
- user message: the CLI question

It parses `choices[0].message.content` and returns a single JSON line on stdout:
`{"answer": "...", "tool_calls": []}`

All progress/debug output is written to stderr (stdout must be valid JSON only).

## Run
Example:
```bash
uv run agent.py "What does REST stand for?"
```

