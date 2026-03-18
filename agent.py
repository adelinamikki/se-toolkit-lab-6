#!/usr/bin/env python3
"""
Task 1: Call an LLM from code.

CLI usage:
  uv run agent.py "What does REST stand for?"

Output:
  A single JSON line to stdout:
    {"answer": "...", "tool_calls": []}

All debug/progress output goes to stderr.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import httpx


def _load_env_file(path: str) -> None:
    """
    Load KEY=VALUE pairs into os.environ.

    Only sets values for keys that are not already present in os.environ.
    This lets the autochecker safely inject its own credentials.
    """

    if not os.path.exists(path):
        return

    try:
        content = open(path, "r", encoding="utf-8").read()
    except OSError:
        # If the file can't be read, we fall back to environment variables.
        return

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')

        if key and key not in os.environ:
            os.environ[key] = value


def _require_env(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _extract_answer(payload: dict[str, Any]) -> str:
    """
    Extract a plain text answer from an OpenAI-compatible response.
    """

    choices = payload.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if content is None:
        return ""
    return str(content).strip()


def _call_llm(question: str) -> str:
    api_base = _require_env("LLM_API_BASE").rstrip("/")
    api_key = _require_env("LLM_API_KEY")
    model = _require_env("LLM_MODEL")

    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    request_body: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer the user directly.",
            },
            {"role": "user", "content": question},
        ],
        "temperature": 0,
    }

    # Keep this well below the 60s end-to-end limit for the CLI.
    timeout = httpx.Timeout(timeout=50.0, connect=10.0)

    # Disable proxy auto-detection to keep local tests deterministic.
    with httpx.Client(timeout=timeout, trust_env=False) as client:
        resp = client.post(url, headers=headers, json=request_body)
        resp.raise_for_status()
        data = resp.json()

    if not isinstance(data, dict):
        raise RuntimeError("LLM response was not a JSON object")

    return _extract_answer(data)


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: uv run agent.py "Your question here"', file=sys.stderr)
        sys.exit(2)

    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Question cannot be empty", file=sys.stderr)
        sys.exit(2)

    # Local convenience for development; autochecker injects env vars.
    _load_env_file(".env.agent.secret")

    try:
        answer = _call_llm(question)
    except Exception as e:
        print(f"Agent error: {e}", file=sys.stderr)
        sys.exit(1)

    result = {"answer": answer, "tool_calls": []}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

