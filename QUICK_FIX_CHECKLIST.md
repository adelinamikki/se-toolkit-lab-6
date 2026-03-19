# Quick Fix Checklist for Task 3 Autochecker

## Immediate Actions Required

### Step 1: Understand the Issue ✓
- [x] Agent code is complete and correct (on task-3-system-agent branch commit 1b25cae)
- [x] All deliverables are in git (AGENT.md, agent.py, plans/task-3.md, tests/)
- [ ] Autochecker can't find agent.py on its VM (needs investigation)

### Step 2: Verify Local Gene Works
```bash
cd /path/to/se-toolkit-lab-6

# Test 1: Check Python syntax
python3 -m py_compile agent.py

# Test 2: Check query_api is present
grep -c "def _tool_query_api" agent.py
# Should return: 1

# Test 3: Run regression tests
python3 -m pytest tests/test_task3_system_agent.py -v
```

### Step 3: Check Git Status
```bash
# Verify branch and commits
git branch -v
git log --oneline -5
git remote -v

# Ensure all files are committed and pushed
git status  # Should be clean ("nothing to commit")
```

### Step 4: Identify Autochecker Branch
Contact your lab instructor to confirm:
- [ ] Which branch does autochecker monitor? (task-2-documentation-agent? main? task-3-system-agent?)
- [ ] Does autochecker clone fresh repo or pull existing?
- [ ] Are there specific branch/tag requirements?

### Step 5: Deploy to Correct Branch

**If autochecker uses task-2-documentation-agent:**
```bash
git checkout task-2-documentation-agent
git merge task-3-system-agent --no-edit
git push origin task-2-documentation-agent
```

**If autochecker uses main:**
```bash
# Option A: Direct merge (if allowed)
git checkout main
git pull origin main
git merge task-3-system-agent --no-edit
git push origin main

# Option B: Create PR for review
git checkout task-3-system-agent
git push origin task-3-system-agent
# Then create PR from task-3-system-agent to main on GitHub
```

**If autochecker uses task-3-system-agent:**
```bash
# Ensure it's pushed (should be done)
git push origin task-3-system-agent

# Inform autochecker operator:
# - Branch: task-3-system-agent
# - Commit: 1b25cae
```

### Step 6: Verify Deployment
After pushing to the target branch:

```bash
# Confirm remote has changes
git fetch origin
git show origin/BRANCH_NAME:agent.py | grep -c "query_api"
# Should return: > 0

# Force autochecker to re-clone or pull
# (Contact operator if needed)
```

### Step 7: Rerun Autochecker
- Request autochecker to:
  - [ ] Clone/pull from correct branch
  - [ ] Verify agent.py exists at path: `/se-toolkit-lab-6/agent.py`
  - [ ] Confirm Python 3 available
  - [ ] Re-run evaluation

## Common Failure Modes & Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| `agent.py not found` | On wrong branch | Merge changes to correct branch |
| `ModuleNotFoundError: httpx` | Dependencies not installed | `pip install httpx` or `uv sync` |
| `LMS_API_KEY not set` | Missing env var | `export LMS_API_KEY=...` or inject via autochecker |
| Tool calls fail | LLM unreachable | Check LLM_API_BASE is correct |
| API queries fail | Backend unreachable | Check AGENT_API_BASE_URL and VPN/firewall |
| JSON parse error | Agent crashes | Check stderr output for exact error |

## Files to Verify Exist

On the evaluation branch, confirm these files exist:

```
se-toolkit-lab-6/
├── agent.py                       # Main agent (Task 3 version)
├── AGENT.md                       # Documentation (updated)
├── plans/task-3.md                # Plan document
├── tests/test_task3_system_agent.py # Regression tests
├── DEPLOYMENT.md                  # Deployment guide
├── AUTOCHECKER_TROUBLESHOOTING.md # This file's sibling
├── wiki/                          # Documentation files
├── backend/                       # Source code
└── .env.agent.secret              # Credentials (autochecker injects)
```

## Test Questions Reference

The autochecker will ask approximately these question types:

| # | Question | Tool | Expected |
|---|----------|------|----------|
| 1 | "protect a branch" | read_file | wiki/git.md reference |
| 2 | "web framework" | read_file | FastAPI |
| 3 | "how many items" | query_api | GET /items/ |
| 4 | "analytics endpoint error" | query_api + read_file | Identifies bug |
| 5 | "Docker journey" | read_file | Traces request path |
| 6-10 | Mixed types (hidden) | Various | Depends on question |

## Success Criteria

After deployment, should see:
- ✅ All 5 open questions > 80% correct
- ✅ After that, hidden questions > 80% correct
- ✅ Tool usage verified (correct tool per question type)
- ✅ Agent completes within time limit

## Support

If problems persist after these steps:

1. **Check the git log:**
   ```bash
   git log --oneline origin/BRANCH_NAME | head -10
   # Should show commit 1b25cae or later
   ```

2. **Verify file contents:**
   ```bash
   grep "def _tool_query_api" agent.py
   grep "query_api" AGENT.md
   ls -la plans/task-3.md
   ls -la tests/test_task3_system_agent.py
   ```

3. **Create issue report** with:
   - Branch being evaluated
   - Exact error message
   - Output of `git log --oneline -5`
   - Output of `ls -la agent.py` 
   - Python version

4. **Contact lab instructor** with the details above

## Git Commands Quick Reference

```bash
# See what's on different branches
git show task-3-system-agent:agent.py | wc -l      # File line count
git show task-2-documentation-agent:agent.py | wc -l

# Merge one branch into another  
git checkout TARGET_BRANCH
git merge SOURCE_BRANCH --no-edit
git push origin TARGET_BRANCH

# Force full re-push
git push origin +BRANCH_NAME

# See commits not yet in main
git log main..BRANCH_NAME --oneline
```

---

**Last Updated:** March 2026  
**Task:** Task 3 - System Agent  
**Branch:** task-3-system-agent  
**Commit:** 1b25cae  
**Status**: Complete, pending autochecker VM deployment
