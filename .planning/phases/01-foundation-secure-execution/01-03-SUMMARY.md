---
phase: 01
plan: 03
name: fix-hitl-architecture-decouple-code-generation
subsystem: agent-tools
tags: [pydantic-ai, google-genai, open-interpreter, hitl, code-execution, sandbox]

dependency-graph:
  requires: [01-01, 01-02]
  provides: [decoupled-code-generation, CodeExecutionRequest-passthrough, direct-gemini-api-call]
  affects: [agent-loop, uat-test-5]

tech-stack:
  added: [google-genai-sdk-direct-usage]
  patterns: [direct-llm-for-code-gen, oi-computer-for-execution-only, hitl-at-pydantic-ai-layer]

key-files:
  created: []
  modified:
    - src/agent/tools/sandbox.py
    - src/agent/prompts.py
    - src/sandbox/languages.py
    - src/agent/core.py
    - src/main.py

decisions:
  - id: direct-genai-over-interpreter-chat
    choice: Use google-genai Client directly in run_system_task instead of interpreter.chat()
    rationale: interpreter.chat() runs OI's own HITL loop internally; code executes before returning to Pydantic AI layer, so CodeExecutionRequest is never surfaced to main.py
  - id: auto-run-true
    choice: Set interpreter.auto_run = True
    rationale: Our HITL is at the Pydantic AI layer. With auto_run=False OI would prompt for approval inside its own loop when confirm_execution calls computer.run() — double gating the wrong layer
  - id: fallback-shell
    choice: Treat unfenced LLM response as shell code
    rationale: Defensive — if model ignores fence instructions, execution still works rather than silently failing

metrics:
  duration: 2m 40s
  completed: 2026-02-24
  tasks-completed: 3/3
  commits: 5
---

# Phase 01 Plan 03: Fix HITL Architecture — Decouple Code Generation from OI Execution Summary

**One-liner:** Decoupled code generation from OI execution by replacing `interpreter.chat()` with direct `google-genai` SDK call so `CodeExecutionRequest` surfaces to Pydantic AI before any code runs.

## What Was Built

The root cause of UAT test 5 failure was `interpreter.chat(task)` running OI's full pipeline internally (LLM → HITL prompt → execute). By the time it returned to Pydantic AI, code had already run and the `CodeExecutionRequest` was never surfaced to `main.py`'s reasoning display.

### Core Fix — `src/agent/tools/sandbox.py`

Replaced `interpreter.chat()` with a direct `google.genai.Client.models.generate_content()` call:

1. Build a focused prompt asking only for fenced code blocks
2. Parse ```` ```python ```` / ```` ```bash ```` fences via regex
3. Normalise language identifiers (`bash/sh/zsh` → `shell`, `py/python3` → `python`)
4. Store blocks in `self.pending_blocks`; return `CodeExecutionRequest` immediately — **no code executed**
5. `confirm_execution()` unchanged — still calls `interpreter.computer.run()` with Docker-backed languages

Set `interpreter.auto_run = True` so OI's internal HITL loop doesn't re-gate execution when `confirm_execution()` calls `computer.run()` directly.

### Prompt Update — `src/agent/prompts.py`

Strengthened agent instructions with explicit rules:
- Always call `run_system_task` for any OS/shell/file task
- **Return the `CodeExecutionRequest` object directly** — never summarize it
- Never attempt self-generated code

Added a concise 3-step HITL table and "What NOT to do" section.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed DockerLanguage BaseLanguage interface compliance**

- **Found during:** Task 3 (import verification exploration)
- **Issue:** `DockerPython`/`DockerShell` didn't inherit `BaseLanguage`, missing required `stop()`, `terminate()`, `name`, `file_extension`, `aliases` — OI's computer would reject them at runtime
- **Fix:** Added `BaseLanguage` inheritance, lifecycle methods, and class attributes; fixed output dict format (`type/format/content` instead of `output` key)
- **Files modified:** `src/sandbox/languages.py`
- **Commit:** `54cf70b`

**2. [Rule 1 - Bug] Fixed Pydantic AI `result_type` → `output_type` API**

- **Found during:** Task 3 (import verification)
- **Issue:** `main.py` used `result_type=` kwarg removed in Pydantic AI v0.4+; would raise `TypeError` at runtime
- **Fix:** Renamed to `output_type=` in both `ironclaw_agent.run()` calls
- **Files modified:** `src/main.py`
- **Commit:** `104b3a4`

**3. [Rule 1 - Bug] Aligned model name in `core.py`**

- **Found during:** Task 3 (import verification)
- **Issue:** `core.py` defaulted to `gemini-1.5-flash` while `sandbox.py` used `gemini-3-flash-preview` — inconsistency
- **Fix:** Updated `default_model` to `gemini-3-flash-preview`
- **Files modified:** `src/agent/core.py`
- **Commit:** `104b3a4`

## Commits

| Hash    | Message |
|---------|---------|
| `80d80cc` | fix(01-03): rewrite run_system_task to use google-genai SDK directly |
| `4e65572` | fix(01-03): update system prompt to enforce CodeExecutionRequest passthrough |
| `54cf70b` | fix(01-03): fix DockerLanguage to properly implement BaseLanguage interface |
| `104b3a4` | fix(01-03): fix Pydantic AI API usage and align model name |

## Success Criteria Verification

| Criterion | Status |
|-----------|--------|
| `sandbox.py` no longer calls `interpreter.chat()` | ✅ Removed |
| `run_system_task` uses google-genai SDK directly | ✅ `genai.Client().models.generate_content()` |
| `run_system_task` returns `CodeExecutionRequest` when code generated | ✅ Returns object before any execution |
| `confirm_execution` still uses `interpreter.computer.run()` | ✅ Unchanged |
| Imports succeed with no errors | ✅ Verified |

## Next Phase Readiness

The HITL architecture gap is closed. `run_system_task` now surfaces `CodeExecutionRequest` to Pydantic AI's layer, enabling `main.py` to display reasoning and proposed code to the user before any execution. UAT test 5 should now pass.

Remaining risk: Gemini model name `gemini-3-flash-preview` needs a valid `GEMINI_API_KEY` at runtime.
