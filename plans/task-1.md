# Task 1 Plan: Call an LLM from Code

## Goal
Implement `agent.py`, a Python CLI that:
1. Takes a user question as the first command-line argument.
2. Calls an OpenAI-compatible chat completions endpoint (no tools yet).
3. Prints exactly one JSON object to stdout:
   `{"answer": "...", "tool_calls": []}`

All logs/debug output must go to stderr; stdout must be valid JSON only.

## LLM Provider and Model
- Provider: **Qwen Code API** (via `qwen-code-oai-proxy`)
- OpenAI-compatible endpoint: `LLM_API_BASE` (from environment)
- Model: `LLM_MODEL` (from environment)
- Auth: `LLM_API_KEY` (from environment)

The agent must not hardcode any of these; the autochecker will inject them.

## Data Flow / Request Structure
1. Parse CLI args to get the `question`.
2. Ensure LLM config is present by reading from environment variables:
   - `LLM_API_KEY`
   - `LLM_API_BASE`
   - `LLM_MODEL`
3. Send a request to:
   - `POST {LLM_API_BASE}/chat/completions`
4. Request body:
   - `model: LLM_MODEL`
   - `messages: [{role: "system", content: ...}, {role: "user", content: question}]`
   - `temperature: 0` (for stability)
5. Parse the response:
   - Read `choices[0].message.content`
6. Print JSON to stdout:
   - `answer`: the extracted content, trimmed
   - `tool_calls`: `[]`

## Timeout / Failure Handling
- The CLI must respond within 60 seconds.
- Use an HTTP request timeout smaller than 60 seconds (e.g., ~45–50s) to account for process overhead.
- On errors (missing env vars, network failure, invalid response):
  - Print a short error message to stderr.
  - Exit with a non-zero code.

## Regression Test Strategy
Create one pytest regression test that does not rely on the real Qwen API:
1. Start a tiny local HTTP stub server that mimics `/v1/chat/completions`.
2. Run `agent.py` as a subprocess with environment variables pointing to the stub.
3. Parse stdout as JSON.
4. Assert:
   - `answer` field exists and is a string
   - `tool_calls` exists and equals `[]`

