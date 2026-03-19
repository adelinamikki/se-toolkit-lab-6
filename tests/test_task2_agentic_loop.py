import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


class _StubLLMHandler(BaseHTTPRequestHandler):
    """Stub LLM server that responds with tool calls or final answers."""

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self.send_response(404)
            self.end_headers()
            return

        # Read request body to inspect what the client is sending
        length = int(self.headers.get("Content-Length", "0"))
        body = b""
        if length:
            body = self.rfile.read(length)

        # Parse request to determine response type
        try:
            request_data = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            request_data = {}

        messages = request_data.get("messages", [])
        user_message = ""
        if messages:
            user_message = messages[-1].get("content", "")

        # Decide response based on user question
        if "merge conflict" in user_message.lower():
            # Check if this is a follow-up (tool results already in conversation)
            has_tool_results = any(m.get("role") == "tool" for m in messages)
            
            if has_tool_results:
                # Follow-up: Return final answer with wiki reference
                response = {
                    "id": "chatcmpl-test-1b",
                    "object": "chat.completion",
                    "model": "qwen3-coder-plus",
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "To resolve a merge conflict, you need to edit the conflicted files to remove conflict markers and keep the desired changes. The wiki/git.md file has detailed steps for resolving merge conflicts.",
                            },
                            "finish_reason": "stop",
                        }
                    ],
                }
            else:
                # Initial response: Make a read_file call to git.md
                response = {
                    "id": "chatcmpl-test-1",
                    "object": "chat.completion",
                    "model": "qwen3-coder-plus",
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "Let me search the wiki for merge conflict resolution.",
                                "tool_calls": [
                                    {
                                        "id": "call_1",
                                        "type": "function",
                                        "function": {
                                            "name": "read_file",
                                            "arguments": '{"path": "wiki/git.md"}',
                                        },
                                    }
                                ],
                            },
                            "finish_reason": "tool_calls",
                        }
                    ],
                }
        elif "what files" in user_message.lower() and "wiki" in user_message.lower():
            # Test 2: list_files response
            response = {
                "id": "chatcmpl-test-2",
                "object": "chat.completion",
                "model": "qwen3-coder-plus",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I'll list the wiki files for you.",
                            "tool_calls": [
                                {
                                    "id": "call_2",
                                    "type": "function",
                                    "function": {
                                        "name": "list_files",
                                        "arguments": '{"path": "wiki"}',
                                    },
                                }
                            ],
                        },
                        "finish_reason": "tool_calls",
                    }
                ],
            }
        else:
            # Default: simple text answer
            response = {
                "id": "chatcmpl-test-default",
                "object": "chat.completion",
                "model": "qwen3-coder-plus",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I don't have more tools to search for that.",
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


def test_task2_agent_read_file_tool() -> None:
    """Test that agent uses read_file tool when answering documentation questions."""
    repo_root = Path(__file__).resolve().parents[1]
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
            [sys.executable, str(agent_py), "How do you resolve a merge conflict?"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env,
            timeout=40,
        )

        assert proc.returncode == 0, (
            f"agent.py exited with {proc.returncode}\n"
            f"stdout: {proc.stdout}\n"
            f"stderr: {proc.stderr}"
        )

        assert proc.stdout.strip(), "agent.py produced no stdout"
        data = json.loads(proc.stdout.strip())

        # Task 2 checks
        assert isinstance(data, dict), "stdout JSON must be an object"
        assert "answer" in data, "stdout JSON must include 'answer'"
        assert "tool_calls" in data, "stdout JSON must include 'tool_calls'"
        assert "source" in data, "stdout JSON must include 'source'"
        assert isinstance(data["tool_calls"], list), "'tool_calls' must be a list"
        
        # Verify tool was called (from stub response with tool_calls)
        # The stub LLM returns tool_calls, which agent should execute
        assert len(data["tool_calls"]) > 0, "Expected at least one tool call"
        
        # Check that source contains a wiki reference
        assert data["source"], "Source should not be empty"
        assert data["source"].startswith("wiki/"), f"Source should start with 'wiki/', got: {data['source']}"

    finally:
        server.shutdown()
        server.server_close()


def test_task2_agent_list_files_tool() -> None:
    """Test that agent uses list_files tool to discover files."""
    repo_root = Path(__file__).resolve().parents[1]
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
            [sys.executable, str(agent_py), "What files are in the wiki?"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env,
            timeout=40,
        )

        assert proc.returncode == 0, (
            f"agent.py exited with {proc.returncode}\n"
            f"stdout: {proc.stdout}\n"
            f"stderr: {proc.stderr}"
        )

        assert proc.stdout.strip(), "agent.py produced no stdout"
        data = json.loads(proc.stdout.strip())

        # Task 2 checks
        assert isinstance(data, dict), "stdout JSON must be an object"
        assert "answer" in data, "stdout JSON must include 'answer'"
        assert "tool_calls" in data, "stdout JSON must include 'tool_calls'"
        assert "source" in data, "stdout JSON must include 'source'"
        assert isinstance(data["tool_calls"], list), "'tool_calls' must be a list"
        
        # Verify list_files was called
        assert len(data["tool_calls"]) > 0, "Expected at least one tool call"
        
        # Check that at least one tool call is list_files
        has_list_files = any(
            tc.get("tool") == "list_files" for tc in data["tool_calls"]
        )
        assert has_list_files, "Expected 'list_files' tool to be called"

    finally:
        server.shutdown()
        server.server_close()
