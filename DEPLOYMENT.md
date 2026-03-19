# Task 3: System Agent Deployment Guide

## What Changed

The `agent.py` file now includes a third tool: **query_api**

### New Tool: query_api
- Query the deployed backend API for live system data
- Supports GET, POST, PUT, DELETE, PATCH methods
- Authentication: Bearer token using LMS_API_KEY from environment
- Returns: JSON with status_code and response body

### Updated Environment Variables
The agent now reads all configuration from environment:
- `LLM_API_KEY` - LLM provider API key
- `LLM_API_BASE` - LLM API endpoint
- `LLM_MODEL` - Model name
- `LMS_API_KEY` - Backend API key (NEW)
- `AGENT_API_BASE_URL` - Backend base URL (NEW, defaults to http://localhost:42002)

## How to Run

```bash
# Install dependencies
uv sync

# Run agent with a question
uv run agent.py "How many items are in the database?"

# Or directly:
python3 agent.py "What framework does the backend use?"
```

## Expected Questions (from autochecker)

The agent handles 10 types of questions:

### Documentation Questions (read_file)
1. "According to the project wiki, what steps are needed to protect a branch on GitHub?"
2. "What Python web framework does this project's backend use?"
5. "Read the docker-compose.yml and the backend Dockerfile. Explain the full journey..."
6. "What does the project wiki say about cleaning up Docker?"
7. "Read the Dockerfile. What technique is used to keep the final Docker image small?"
9. "Read the analytics router source code (analytics.py). Which endpoints can crash..."
10. "Compare how the ETL pipeline handles failures vs how the API endpoints handle failures..."

### API Data Questions (query_api)
3. "How many items are currently stored in the database?"
4. "Query the /analytics/completion-rate endpoint for a lab that has no data (e.g., lab-99)..."
8. "How many distinct learners have submitted data?"

## Verification

To verify locally before autochecker runs:

```bash
# With stub servers running (see tests/test_task3_system_agent.py for example):
python3 -m pytest tests/test_task3_system_agent.py -v

# Or with actual backend running:
uv run run_eval.py
```

## Branch Information

- Task 3 implementation: branch `task-3-system-agent`
- Commit: 4684c71
- Files modified:
  - `agent.py` - Added query_api tool implementation
  - `AGENT.md` - Documentation updated to 400+ words
  - `plans/task-3.md` - Implementation plan and design
  - `tests/test_task3_system_agent.py` - 2 regression tests

## Deployment Checklist for Autochecker

- [x] agent.py is Python 3 compatible
- [x] agent.py can be run with `python3 agent.py "question"`
- [x] All environment variables come from os.environ (no hardcoded values)
- [x] query_api tool authenticates with Bearer token
- [x] System prompt guides tool selection
- [x] Agent handles both documentation (read_file) and data queries (query_api)
- [x] Output is valid JSON with "answer", "source", "tool_calls" fields

## Troubleshooting

If autochecker reports "agent.py not found":
1. Verify repository is cloned on the VM
2. Verify correct branch/commit is checked out
3. Verify Python 3 is available and httpx is installed
4. Check that .env.agent.secret and .env.docker.secret are present (or env vars injected)

The agent is **production-ready** and requires:
- Python 3.9+
- httpx library (in pyproject.toml dependencies)
- LLM API credentials (LLM_API_KEY, LLM_API_BASE, LLM_MODEL)
- Backend API credentials (LMS_API_KEY)
- Backend API running on AGENT_API_BASE_URL (default: http://localhost:42002)
