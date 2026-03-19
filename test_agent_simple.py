import subprocess
import json
import sys

# Test 1: Simple documentation question
question = "What is a merge conflict? (answer in one sentence)"
result = subprocess.run(
    [sys.executable, "agent.py", question],
    capture_output=True,
    text=True,
    timeout=30,
    env={**subprocess.os.environ, 
         "LLM_API_KEY": "test",
         "LLM_API_BASE": "http://localhost:42005/v1",
         "LLM_MODEL": "test",
         "LMS_API_KEY": "test"}
)

print(f"Return code: {result.returncode}")
print(f"Stderr: {result.stderr[:500]}")
print(f"Stdout: {result.stdout[:500]}")

if result.returncode == 0:
    try:
        data = json.loads(result.stdout)
        print(f"\n✓ Valid JSON output")
        print(f"  Tools used: {[t['tool'] for t in data.get('tool_calls', [])]}")
    except:
        print("✗ Invalid JSON output")
