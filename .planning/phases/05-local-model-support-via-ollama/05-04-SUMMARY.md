---
phase: 05-local-model-support-via-ollama
plan: 04
subsystem: agent
tags: [ollama, streaming, on_output, callback, hitl, tool-registration, requirements]

# Dependency graph
requires:
  - phase: 05-01
    provides: get_provider_config(), OllamaUnavailableError
  - phase: 05-02
    provides: SandboxedTool.run_system_task() with on_output parameter, Ollama streaming branch
  - phase: 05-03
    provides: startup health checks wired into entry points

provides:
  - on_output callback flows from AgentDeps through RunContext into module-level run_system_task wrapper and on to SandboxedTool.run_system_task()
  - Ollama tokens stream progressively during code generation (no silent batch accumulation)
  - ENG-05 traceability row accurate: lists 05-01, 05-02, 05-03 with Complete status
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "@ironclaw_agent.tool (not tool_plain) for tools needing RunContext access to deps"
    - "Pattern: on_output = ctx.deps.on_output if ctx.deps else None — defensive None guard"

key-files:
  created: []
  modified:
    - src/agent/core.py
    - src/agent/tools/sandbox.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Switched @tool_plain -> @tool for run_system_task registration in core.py to gain RunContext access — mirrors the existing confirm_execution pattern already in the file"
  - "Module-level sandbox.py wrapper accepts on_output as Optional[Callable] with None default — backward compatible with existing callers that omit it"

patterns-established:
  - "All tools needing deps access use @ironclaw_agent.tool with ctx: RunContext[AgentDeps] as first param"

requirements-completed: [ENG-05]

# Metrics
duration: 2min
completed: 2026-02-28
---

# Phase 05 Plan 04: Gap Closure — Streaming Callback and Requirements Traceability Summary

**on_output callback wired from AgentDeps through RunContext into run_system_task tool and module-level wrapper; ENG-05 traceability row updated to Complete with all three plans listed**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-02-28T08:26:51Z
- **Completed:** 2026-02-28T08:29:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- `src/agent/core.py`: `@ironclaw_agent.tool_plain` changed to `@ironclaw_agent.tool`; `ctx: RunContext[AgentDeps]` added as first param; `on_output = ctx.deps.on_output if ctx.deps else None` extracted and forwarded to `_run_system_task(task, on_output=on_output)` — matches the existing pattern used by `confirm_execution`
- `src/agent/tools/sandbox.py`: Module-level `run_system_task` wrapper signature updated from `(task: str)` to `(task: str, on_output: Optional[Callable[[str], None]] = None)` and forwards `on_output` to `get_sandbox_tool().run_system_task(task, on_output=on_output)` — no new imports needed
- `.planning/REQUIREMENTS.md`: ENG-05 traceability row updated from `05-01, 05-02 | In Progress` to `05-01, 05-02, 05-03 | Complete`; Last updated date changed to 2026-02-28

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire on_output streaming callback into run_system_task** - `d5d5a11` (feat)
2. **Task 2: Update ENG-05 traceability row in REQUIREMENTS.md** - `373825a` (chore)

**Plan metadata:** _(docs commit follows)_

## Files Created/Modified
- `src/agent/core.py` - run_system_task tool registration: tool_plain -> tool, ctx param added, on_output threaded
- `src/agent/tools/sandbox.py` - module-level run_system_task wrapper: on_output parameter added and forwarded
- `.planning/REQUIREMENTS.md` - ENG-05 row: 05-03 added, status set to Complete, date updated

## Decisions Made
- Used `@ironclaw_agent.tool` (not `tool_plain`) so RunContext is passed — the same approach already used by `confirm_execution`, making the codebase consistent
- No new imports were needed in either file — `Optional`, `Callable` already imported in sandbox.py; `RunContext` already imported in core.py
- Module-level wrapper default `on_output=None` preserves backward compatibility for any call sites that omit the argument

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

**Pre-existing test failure (out of scope):** `tests/test_hitl.py::test_run_system_task_generates_request` fails when Ollama is running because the test mocks `genai.Client` (Gemini path) but not `ollama_lib.generate` (Ollama path). This failure predates 05-04 — confirmed by reverting changes and re-running. Logged to `deferred-items.md`. No action taken (out of scope for this plan).

## Self-Check: PASSED

- FOUND: src/agent/core.py (contains `@ironclaw_agent.tool`, `ctx: RunContext[AgentDeps]`, `on_output.*ctx\.deps`)
- FOUND: src/agent/tools/sandbox.py (module-level wrapper contains `on_output: Optional[Callable[[str], None]] = None`)
- FOUND: .planning/REQUIREMENTS.md (ENG-05 row shows `05-01, 05-02, 05-03 | Complete`)
- FOUND commit d5d5a11 (feat(05-04): wire on_output streaming callback into run_system_task)
- FOUND commit 373825a (chore(05-04): update ENG-05 traceability row to Complete)
- Signature verification passed: `(task: str, on_output: Callable[[str], NoneType] | None = None) -> ...`

---
*Phase: 05-local-model-support-via-ollama*
*Completed: 2026-02-28*
