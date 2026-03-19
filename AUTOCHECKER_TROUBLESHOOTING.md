# Task 3: Autochecker Deployment Troubleshooting

## Current Status

✅ **Local Evaluation Complete**
- Plan (plans/task-3.md) - created
- query_api tool (agent.py) - implemented  
- AGENT.md documentation - updated (400+ words)
- 2 regression tests (tests/test_task3_system_agent.py) - created

❌ **Autochecker VM Deployment Issue**
- Autochecker reports: "Could not find agent.py on VM 10.93.24.149"
- Local checks passed: "Plan, query_api tool, and AGENT.md (200+ words) ✅"
- Remote checks failed: Unable to run local/hidden questions

## Root Cause Analysis

The autochecker seems to be looking for agent.py on a specific VM but it's not being found. Possible reasons:

1. **Branch Issue**: Autochecker may be looking on `task-2-documentation-agent` or another branch
2. **Deployment Configuration**: The VM might need to pull from a specific branch or the repo wasn't initialized
3. **Path Issue**: The file might be expected in a different location

## Solution Options

### Option A: Merge to task-2-documentation-agent (Recommended)
The autochecker may be running Task 3 evaluation against `task-2-documentation-agent` branch (the current Task 2 branch). Merging our changes there would make them available:

```bash
# Switch to task-2-documentation-agent
git checkout task-2-documentation-agent

# Merge task-3-system-agent  
git merge task-3-system-agent -m "Merge Task 3 system agent implementation"

# Push to remote
git push origin task-2-documentation-agent
```

Then update the autochecker configuration to use `task-2-documentation-agent` as the evaluation branch.

### Option B: Update Autochecker Configuration
If the autochecker monitors a configuration file, specify the correct branch/tag:
- Specify branch: `task-3-system-agent`
- Specify tag: Create a tag like `v3-system-agent` and push it
- Specify commit: Use commit `1b25cae` or later

### Option C: Create PR to Main
Create a pull request from `task-3-system-agent` to main, get approval, and merge. This ensures:
- Code review via PR
- Changes available on main branch
- Autochecker can evaluate from main if configured that way

## Quick Verification Commands

Test if agent.py works locally:
```bash
# Test import
python3 -c "
with open('agent.py') as f:
    code = f.read()
compile(code, 'agent.py', 'exec')
print('✓ agent.py syntax valid')
"

# Test query_api availability
python3 << 'EOF'
import sys
import json

# Parse agent.py to check tools
with open('agent.py') as f:
    content = f.read()

tools_available = 'query_api' in content and '_tool_query_api' in content
print(f"✓ query_api tool: {'present' if tools_available else 'MISSING'}")
EOF

# Test with stub servers
python3 -m pytest tests/test_task3_system_agent.py -v
```

## Files Deployed

These files are ready on `task-3-system-agent` branch:

1. **agent.py** (modified)
   - Added `_tool_query_api()` function
   - Updated tool schemas in `_get_tool_schemas()`
   - Updated `_call_tool()` dispatcher  
   - Enhanced system prompt with tool selection guidance
   - Load both .env files in `main()`

2. **AGENT.md** (modified)
   - 400+ words explaining Task 3 architecture
   - Tool descriptions with use cases
   - Authentication details
   - Lessons learned section

3. **plans/task-3.md** (new)
   - Implementation plan and design decisions
   - Tool schema specs
   - Error handling strategy

4. **tests/test_task3_system_agent.py** (new)
   - Test 1: Verify read_file for documentation
   - Test 2: Verify query_api for data queries

5. **DEPLOYMENT.md** (new)
   - Deployment guide
   - Environment variable requirements
   - Verification steps

## Autochecker Integration Steps

1. **Verify Repository Access**
   - Confirm VM can clone/access repo
   - Confirm correct branch is checked out
   - Confirm Python 3 is available

2. **Ensure Directory Structure**
   - agent.py should be in root: `/se-toolkit-lab-6/agent.py`
   - Supporting files: wiki/, backend/, plans/, tests/

3. **Verify Environment**
   - LLM credentials available (LLM_API_KEY, LLM_API_BASE, LLM_MODEL)
   - Backend credentials available (LMS_API_KEY)
   - Backend service running on AGENT_API_BASE_URL

4. **Test End-to-End**
   ```bash
   # From project root
   python3 agent.py "How many items are in the database?"
   ```

## Expected Autochecker Behavior

The autochecker should run 10 questions total:

**5 Open Questions (local eval):**
1. Wiki protection steps → read_file
2. Backend framework → read_file  
3. Item count → query_api
4. Analytics error/bug diagnosis → query_api + read_file
5. Docker journey explanation → read_file + analysis

**5 Hidden Questions (after local passes 80%):**
- Similar mix of documentation and API queries

## Next Steps for Resolution

1. Verify which branch autochecker expects
2. Either:
   - Merge `task-3-system-agent` to that branch, OR
   - Update autochecker config to use `task-3-system-agent`, OR
   - Create PR to main for broader availability
3. Confirm autochecker VM has pull/clone latest code
4. Re-run autochecker evaluation

Contact your lab instructor or autochecker operator with:
- This troubleshooting guide
- Branch information: `task-3-system-agent`
- Commit: `1b25cae`
- Confirm: agent.py, AGENT.md, plans/task-3.md, tests/test_task3_system_agent.py all present
