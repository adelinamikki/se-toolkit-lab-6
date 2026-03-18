import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


class _StubLLMHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self.send_response(404)
            self.end_headers()
            return

        # Read and ignore request body (we only need to respond OpenAI-compatible JSON).
        length = int(self.headers.get("Content-Length", "0"))
        if length:
            _ = self.rfile.read(length)

        response = {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "model": "qwen3-coder-plus",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Representational State Transfer.",
                    },
                    "finish_reason": "stop",
                }
            ],
        }

        payload = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        # Silence HTTP server logs during tests.
        return


def test_agent_task1_outputs_required_json_fields() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    agent_py = repo_root / "agent.py"
    assert agent_py.exists(), "Expected agent.py at repository root"

    server = HTTPServer(("127.0.0.1", 0), _StubLLMHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    env = os.environ.copy()
    env.update(
        {
            "LLM_API_KEY": "key6",
            "LLM_API_BASE": f"http://127.0.0.1:{port}/v1",
            "LLM_MODEL": "qwen3-coder-plus",
        }
    )

    try:
        proc = subprocess.run(
            [sys.executable, str(agent_py), "What does REST stand for?"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
        )

        assert proc.returncode == 0, (
            f"agent.py exited with {proc.returncode}\n"
            f"stdout: {proc.stdout}\n"
            f"stderr: {proc.stderr}"
        )

        assert proc.stdout.strip(), "agent.py produced no stdout"
        data = json.loads(proc.stdout.strip())
        assert isinstance(data, dict), "stdout JSON must be an object"
        assert "answer" in data, "stdout JSON must include 'answer'"
        assert "tool_calls" in data, "stdout JSON must include 'tool_calls'"
        assert isinstance(data["tool_calls"], list), "'tool_calls' must be a list"
        assert data["tool_calls"] == [], "'tool_calls' must be [] for Task 1"
    finally:
        server.shutdown()
        server.server_close()

