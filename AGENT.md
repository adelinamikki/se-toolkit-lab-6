# Agent Architecture (Task 2)

This repository contains an `agent.py` CLI that answers questions by **calling an LLM with agentic tools**. Unlike Task 1 (simple LLM calls), Task 2 implements the full **agentic loop**: the LLM can call tools (read_file, list_files) to explore project documentation, and the agent feeds results back to the LLM for reasoning.

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

## Tools

The agent has two tools available via OpenAI-compatible function calling:

### read_file
- **Description**: Read a file from the project repository
- **Parameters**: 
  - `path` (string): Relative path from project root (e.g., "wiki/git.md")
- **Returns**: File contents as string, or error message if file doesn't exist
- **Security**: Rejects paths with `..` or absolute paths to prevent directory traversal

### list_files
- **Description**: List files and directories at a given path
- **Parameters**:
  - `path` (string): Relative directory path from project root (e.g., "wiki")
- **Returns**: Newline-separated listing of entries (directories end with `/`)
- **Security**: Rejects paths with `..` or absolute paths

## Agentic Loop

The agent implements a reasoning loop:

1. **Send question to LLM** with tool schemas defined as JSON function-calling definitions
2. **Parse LLM response**:
   - If the response includes `tool_calls` → execute each tool, record results, append as "tool" role messages, loop back to step 1
   - If the response is text only (no `tool_calls`) → extract answer, move to step 4
   - If 10 tool calls reached → stop looping, use accumulated answer
3. **Execute tools** with security-validated paths; if tool fails, return error message to LLM
4. **Extract source reference** from LLM's answer (e.g., "wiki/git.md#resolving-merge-conflicts")
5. **Return JSON** with answer, source, and tool_calls log

### System Prompt Strategy
The system prompt directs the LLM to:
- Use `list_files` to explore the wiki directory structure
- Use `read_file` to read relevant documentation files
- Include source file references with section anchors in the final answer
- Stay focused on wiki/ as the authoritative source of documentation

## Request/Response Shape

### Agentic Loop Message Flow
1. **Initial request**: System prompt + user question + tool schemas
2. **Tool call iteration**: 
   - LLM response with `tool_calls` array (each tool call has function name and arguments)
   - Agent executes tools, appends results as "tool" role messages
   - Loop continues until LLM responds with text (no tool_calls) or max iterations reached
3. **Final response**: LLM's text message with source reference

### Output Format
Single JSON line on stdout:
```json
{
  "answer": "Edit the file, resolve conflicts, then stage and commit.",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {"tool": "list_files", "args": {"path": "wiki"}, "result": "git-workflow.md\n..."},
    {"tool": "read_file", "args": {"path": "wiki/git-workflow.md"}, "result": "# Git Workflow\n..."}
  ]
}
```

- **answer**: Final text answer from the LLM
- **source**: Wiki file and section reference where answer was found (e.g., "wiki/file.md#section")
- **tool_calls**: Array of all tool calls executed, including tool name, arguments, and result
  - Limited to maximum 10 tool calls per question

All progress/debug output is written to stderr (stdout must be valid JSON only).

## Run
Example:
```bash
uv run agent.py "How do you resolve a merge conflict?"
```


