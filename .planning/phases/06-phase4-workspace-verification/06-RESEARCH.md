# Phase 6: Phase 4 Workspace Verification - Research

**Researched:** 2026-02-28
**Domain:** UAT execution and formal verification documentation
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Test execution
- Tests are manual and interactive — the user runs the Chainlit web UI and actually exercises each feature
- The plan should guide an executor to walk through each test step-by-step and record results
- Integration checker already confirmed all code wiring is present; this phase captures live functional evidence

#### Failure handling
- All 5 tests must be attempted regardless of outcome
- If a test fails, document it with `[FAIL]` and note the observed behavior
- VERIFICATION.md is created regardless — it records the actual outcome (pass/fail per requirement)
- A failing test does NOT block creation of VERIFICATION.md; it documents partial status if needed

#### VERIFICATION.md structure
- Match the format used in phases 1, 2, 3, and 5 (requirement-by-requirement evidence with pass/fail per criterion)
- File location: `.planning/phases/04-workspace-file-management/04-VERIFICATION.md`
- Must formally sign off on ENG-03 and WEB-03 by referencing UAT test results as evidence

### Claude's Discretion
- Exact markdown styling within VERIFICATION.md (follow existing phase patterns)
- How to structure the evidence summary (reference UAT test numbers, not raw log output)

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ENG-03 | Support workspace file management (upload/download/read/write) for the agent | All 5 UAT tests exercise ENG-03 behaviors; code wiring confirmed by integration checker (handle_file_uploads, list_workspace_files, Docker bind-mount /workspace) |
| WEB-03 | Provide a UI-based file manager for interacting with the agent's workspace | UAT tests 1, 4, 5 specifically cover UI-side behavior (/files command, auto-discovery via send_file_diff, upload confirmation); integration checker confirmed wiring in web_ui.py |
</phase_requirements>

---

## Summary

This phase is a pure verification and documentation exercise — no new code is written. Phase 4 workspace file management was implemented across two plans (04-01 and 04-02) and independently confirmed wired by an integration checker. The gap is purely formal: no VERIFICATION.md exists and the 04-UAT.md file has all 5 tests stuck at `[pending]`.

The work consists of two sequential steps: (1) an executor runs the Chainlit web UI and Docker sandbox, walks through each of the 5 UAT tests interactively, and records pass/fail results in 04-UAT.md; (2) the executor writes 04-VERIFICATION.md following the format established by phases 1, 3, and 5, citing UAT test numbers as evidence for ENG-03 and WEB-03 satisfaction.

Because all code is already implemented and independently verified as wired, tests are expected to pass. The plan must still accommodate the documented failure policy: all 5 tests get attempted regardless, VERIFICATION.md is produced regardless of outcome, and any failures are documented with observed behavior.

**Primary recommendation:** Plan a single wave with two tasks — (T1) execute UAT and update 04-UAT.md with results, (T2) write 04-VERIFICATION.md using UAT evidence.

---

## Standard Stack

No new libraries or installations are needed. This phase uses the existing project runtime.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Chainlit web UI | existing | Runtime for interactive UAT | All 5 tests require a live Chainlit session |
| Docker (`ironclaw-agent` image) | existing | Sandbox for tests 3 and 5 | Agent code runs inside Docker; test 3 reads files at /workspace |
| pytest | existing | Pre-existing automated tests remain green | Baseline regression check before UAT |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `./workspace` directory | auto-created | File drop zone for upload/download tests | Must exist (workspace.py auto-creates it) |
| `04-UAT.md` | existing | Test script with expected criteria | Executor reads expected: fields for pass/fail determination |
| Phases 1/3/5 VERIFICATION.md files | existing | Format reference | Planner should embed format in task instructions |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Manual interactive UAT | Automated Playwright/Selenium | Automation is out of scope (user decided manual); Chainlit UI interactions are difficult to automate reliably |

**Installation:** None required.

---

## Architecture Patterns

### Phase Structure
```
.planning/phases/04-workspace-file-management/
├── 04-UAT.md              # Test script — update result: fields in place
└── 04-VERIFICATION.md     # NEW: created by this phase (write here, not in phase 06 dir)
```

### Pattern 1: UAT Execution Pattern
**What:** Each test in 04-UAT.md has an `expected:` field describing observable behavior. The executor performs the action, compares actual behavior to expected, and overwrites the `result:` field from `[pending]` to `[pass]` or `[fail: <description>]`.

**When to use:** All 5 UAT test entries

**Example result field update:**
```markdown
### 1. Upload a file via the web UI
expected: In the Chainlit web UI, attach a file...
result: [pass]
```

Or on failure:
```markdown
result: [fail: file appeared in ./workspace but no confirmation message was shown in chat]
```

### Pattern 2: VERIFICATION.md Format (from phases 1, 3, 5)
**What:** Frontmatter block + requirement-by-requirement evidence table. Uses "Observable Truths" table mapping each behavior to VERIFIED/FAILED with specific evidence. Ends with Requirements Coverage table.

**When to use:** Writing 04-VERIFICATION.md

**Example (based on phase 1 and phase 5 structure):**
```markdown
---
phase: 04-workspace-file-management
verified: <timestamp>
status: passed   # or: partial
score: X/Y criteria verified
---

# Phase 4: Workspace & File Management — Verification Report

**Phase Goal:** Bidirectional file exchange between the user, the agent, and the Docker sandbox.
**Verified:** <date>
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Files uploaded via Chainlit UI appear in ./workspace | VERIFIED | UAT Test 1: [pass] |
| 2 | Agent can list ./workspace contents via list_workspace_files tool | VERIFIED | UAT Test 2: [pass] |
| 3 | Uploaded files accessible inside Docker at /workspace | VERIFIED | UAT Test 3: [pass] |
| 4 | /files command returns workspace listing with download links | VERIFIED | UAT Test 4: [pass] |
| 5 | Agent-created files auto-discovered and offered for download | VERIFIED | UAT Test 5: [pass] |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| src/agent/tools/workspace.py | list_workspace_files, get_workspace_snapshot, get_workspace_diff | VERIFIED | ... |
| src/web_ui.py | handle_file_uploads, send_file_diff, /files command | VERIFIED | ... |
| Docker bind-mount | ./workspace → /workspace inside container | VERIFIED | ... |

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| ENG-03 | 04-01, 04-02 | Workspace file management for agent | SATISFIED | UAT tests 1–5 all pass |
| WEB-03 | 04-02 | UI-based file manager | SATISFIED | UAT tests 1, 4, 5 confirm upload, /files, auto-discovery |

### Gaps Summary
No gaps found. (or: Gap description if any test fails)
```

### Anti-Patterns to Avoid
- **Writing VERIFICATION.md to the wrong directory:** The file MUST go to `.planning/phases/04-workspace-file-management/04-VERIFICATION.md`, NOT into the phase 06 directory.
- **Skipping failed tests:** All 5 must be recorded regardless of outcome; do not mark as `[pending]` after attempting.
- **Summarizing UAT results without test numbers:** VERIFICATION.md evidence must reference specific UAT test numbers (e.g., "UAT Test 3: [pass]"), not just say "tested manually."
- **Omitting the frontmatter block:** All existing VERIFICATION.md files include a YAML frontmatter block. Follow the same pattern.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Format reference for VERIFICATION.md | Invent a new format | Follow phases 1, 3, 5 existing VERIFICATION.md files | Consistency across phases is required by locked decision |
| Test pass/fail determination | Write scripts | Manual visual check against expected: in 04-UAT.md | Tests are inherently interactive UI tests; the expected: field is the acceptance criterion |

---

## Common Pitfalls

### Pitfall 1: Wrong Output File Location
**What goes wrong:** VERIFICATION.md lands in `.planning/phases/06-phase4-workspace-verification/` instead of the Phase 4 directory.
**Why it happens:** Phase 6 is the executing phase, so it's the natural default location.
**How to avoid:** The locked decision specifies `.planning/phases/04-workspace-file-management/04-VERIFICATION.md` explicitly. The plan task must hardcode this path.
**Warning signs:** Phase 6 directory has a 04-VERIFICATION.md file — it should only ever have 06-* files.

### Pitfall 2: Test 3 Fails Due to Docker Not Running
**What goes wrong:** Test 3 (file accessible inside Docker) fails not because the feature is broken, but because `ironclaw-agent` Docker image isn't built or the container isn't started.
**Why it happens:** The sandbox starts on demand when the agent executes code; if Docker daemon is stopped, the entire execution fails.
**How to avoid:** Plan setup steps must explicitly include: `docker build -t ironclaw-agent .` and verify Docker daemon is running before UAT.
**Warning signs:** Test 3 fails but tests 1 and 2 pass — likely a Docker setup issue, not a feature regression.

### Pitfall 3: Test 5 (Auto-Discovery) Requires Code Approval
**What goes wrong:** Test 5 appears to stall because the agent presents a HITL approval step before creating the file.
**Why it happens:** Test 5 asks the agent to "create a file" which triggers run_system_task → CodeExecutionRequest → approval buttons. The executor must click Approve before the file is created.
**How to avoid:** Plan must note that HITL approval is a required intermediate step in test 5, not a bug.
**Warning signs:** Executor reports "auto-discovery not working" but actually just forgot to approve the code.

### Pitfall 4: Stale UAT Summary Block
**What goes wrong:** After updating individual test results, the `## Summary` block at the bottom of 04-UAT.md still shows `passed: 0, pending: 5`.
**Why it happens:** The summary is a manual count field, not auto-generated.
**How to avoid:** After recording all test results, update the summary block to reflect actual pass/fail/pending counts.
**Warning signs:** All results say `[pass]` but summary still shows `passed: 0`.

### Pitfall 5: /files Command Test (Test 4) Shows No Files
**What goes wrong:** Test 4 runs `/files` but gets "No files in workspace." instead of a listing.
**Why it happens:** The workspace might be empty if test 1 (upload) was not completed or the uploaded file was deleted.
**How to avoid:** Run tests in order — test 4 depends on the workspace having files from test 1. Or upload a file specifically before test 4.
**Warning signs:** Test 4 receives "No files in workspace." — check that test 1 or test 3 left a file behind.

---

## Code Examples

All code is pre-existing. These are the relevant sections the plan's verification steps should reference.

### handle_file_uploads (ENG-03, WEB-03 — Test 1)
```python
# Source: src/web_ui.py
async def handle_file_uploads(message: cl.Message):
    """Process any files attached to a message, saving them to the workspace."""
    # Saves uploaded files to ./workspace/
```

### list_workspace_files tool (ENG-03 — Test 2)
```python
# Source: src/agent/tools/workspace.py
def list_workspace_files() -> List[str]:
    """Returns list of all files in ./workspace directory."""
    workspace_path = "./workspace"
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)
        return []
    files = [f for f in os.listdir(workspace_path) if os.path.isfile(...)]
    return files
```

### /files command handler (WEB-03 — Test 4)
```python
# Source: src/web_ui.py on_message()
if message.content == "/files":
    files = list_workspace_files()
    if not files:
        await cl.Message(content="No files in workspace.").send()
        return
    # ... sends cl.File elements for each file
```

### send_file_diff — auto-discovery (WEB-03 — Test 5)
```python
# Source: src/web_ui.py
async def send_file_diff(old_snapshot):
    new_snapshot = get_workspace_snapshot()
    diff = get_workspace_diff(old_snapshot, new_snapshot)
    if diff:
        # sends cl.File elements for each changed/new file
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| @cl.on_file_upload decorator | @cl.on_files decorator | Phase 4 (04-01) | Breaking API change in Chainlit; already fixed in implementation |
| No UAT results | All 5 tests recorded in 04-UAT.md | After Phase 6 | Closes the formal verification gap |
| No 04-VERIFICATION.md | 04-VERIFICATION.md with ENG-03/WEB-03 sign-off | After Phase 6 | Brings milestone v1.0 from 9/11 to 11/11 requirements formally verified |

---

## Open Questions

1. **Test environment state between tests**
   - What we know: Tests 2, 3, 4 depend on files existing from test 1; tests run in documented order
   - What's unclear: Whether workspace will be clean at start or have leftover files from previous runs
   - Recommendation: Plan should include a "clean workspace" step or document that leftover files are acceptable for testing

2. **Which LLM provider will be active during UAT**
   - What we know: Project supports Gemini (default), Anthropic, OpenAI, and Ollama
   - What's unclear: Which provider will be active when the executor runs the tests
   - Recommendation: Tests are provider-agnostic (they test file I/O, not LLM output quality); any provider is acceptable. Plan should note this so executor doesn't need to configure a specific one.

---

## Sources

### Primary (HIGH confidence)
- Direct file inspection: `.planning/phases/06-phase4-workspace-verification/06-CONTEXT.md` — locked decisions and phase scope
- Direct file inspection: `.planning/phases/04-workspace-file-management/04-UAT.md` — all 5 tests with expected criteria
- Direct file inspection: `src/agent/tools/workspace.py` — implementation of list_workspace_files, get_workspace_snapshot, get_workspace_diff
- Direct file inspection: `src/web_ui.py` — handle_file_uploads, send_file_diff, /files command handler confirmed present
- Direct file inspection: `.planning/v1.0-MILESTONE-AUDIT.md` — integration checker confirmed all wiring present; gap defined as missing VERIFICATION.md only
- Direct file inspection: phases 1, 3, 5 VERIFICATION.md files — format reference established

### Secondary (MEDIUM confidence)
- `.planning/phases/04-workspace-file-management/04-01-SUMMARY.md` / `04-02-SUMMARY.md` — implementation decisions and what was built

### Tertiary (LOW confidence)
None — all research based on direct project file inspection.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new libraries; existing runtime already in place
- Architecture patterns: HIGH — VERIFICATION.md format directly derived from existing phase 1, 3, 5 files
- Pitfalls: HIGH — derived from direct code inspection and UAT test analysis
- UAT test behavior: HIGH — all 5 test expected criteria read directly from 04-UAT.md

**Research date:** 2026-02-28
**Valid until:** 60 days (stable — no external dependencies; all findings from project files)
