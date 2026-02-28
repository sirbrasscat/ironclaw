---
phase: 07-ollama-cli-streaming-fix
plan: 01
subsystem: cli
tags: [ollama, streaming, pydantic-ai, agentdeps, open-interpreter]

# Dependency graph
requires:
  - phase: 05-local-model-support-via-ollama
    provides: on_output callback infrastructure in sandbox.py and core.py
provides:
  - AgentDeps wired into both ironclaw_agent.run() calls in main.py — Ollama tokens stream progressively to CLI
  - Dead OI LLM config removed from SandboxedTool.__init__; interpreter.offline = True
affects: [main.py, sandbox.py]

# Tech tracking
tech-stack:
  added: []
  patterns: [Pass AgentDeps(on_output=callback) once before the while loop — reuse across iterations]

key-files:
  created: []
  modified:
    - src/main.py
    - src/agent/tools/sandbox.py

key-decisions:
  - "AgentDeps callback defined once before the while loop (not re-created per iteration)"
  - "Trailing print() after planning run ensures approval prompt starts on its own line"
  - "interpreter.offline = True — OI used as execution engine only, no LLM config needed"

patterns-established:
  - "Wire AgentDeps(on_output=callback) to ironclaw_agent.run() — cloud providers silently ignore it, Ollama uses it"

requirements-completed: [ENG-05]

# Metrics
duration: 2min
completed: 2026-02-28
---

# Phase 7 Plan 01: Ollama CLI Streaming Fix Summary

**AgentDeps(on_output=callback) wired into both ironclaw_agent.run() calls in main.py; dead interpreter.llm config removed from SandboxedTool.__init__ and interpreter.offline set to True — closes GAP-01 and GAP-02 from v1.0 audit**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-28T10:40:58Z
- **Completed:** 2026-02-28T10:42:55Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Wired AgentDeps streaming callback into main.py CLI loop — Ollama tokens now print progressively to terminal, not buffered until full response
- Added trailing print() after planning run so approval prompt starts on its own line
- Confirmed both ironclaw_agent.run() calls (planning and confirmation) receive deps=_deps
- Removed dead `interpreter.llm.model` and `interpreter.llm.api_key` lines from SandboxedTool.__init__
- Set interpreter.offline = True (was erroneously False)
- Non-Ollama providers (Gemini, Anthropic, OpenAI) unaffected — callback present but never invoked by their branch

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire AgentDeps streaming callback into main.py CLI loop** - `3c94745` (feat)
2. **Task 2: Remove dead OI LLM config from SandboxedTool.__init__ and set offline=True** - `91925d1` (fix)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `src/main.py` - Added AgentDeps import; defined _callback and _deps before while loop; passed deps=_deps to both ironclaw_agent.run() calls; added trailing print() after planning call
- `src/agent/tools/sandbox.py` - Removed interpreter.llm.model and interpreter.llm.api_key; set interpreter.offline = True; added one-liner comment

## Decisions Made
- AgentDeps callback defined once before the while loop (not inside it) — reused across all iterations, per plan spec
- Trailing print() added only after the planning run (not confirmation) — confirmation result already ends with its own newline
- No provider-conditional guard added — cloud providers silently ignore the callback

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Import smoke test with `/usr/bin/python3` failed because pydantic_ai is only installed in `venv/`. Re-ran with `venv/bin/python3` — passed immediately. Not a code issue.

## ENG-05 Traceability

Phase 7 closes GAP-01 (main.py missing deps=AgentDeps()) and GAP-02 (hardcoded interpreter.llm.model) from the v1.0 milestone audit. ENG-05 (Ollama streaming) is now fully complete end-to-end:

- Phase 05-02: on_output token loop in sandbox.py
- Phase 05-04: ctx.deps guard in core.py
- Phase 07-01 (this plan): deps=AgentDeps wired at the call site in main.py

## Verification Results

All automated checks passed:

- main.py: AgentDeps imported, _callback defined, _deps defined, 2x deps=_deps, print() present, ast.parse() clean
- sandbox.py: interpreter.llm.model absent, interpreter.llm.api_key absent, offline=True, auto_run=True, safe_mode=False, one-liner comment present, ast.parse() clean
- Import smoke test (venv/bin/python3): `imports OK: <class 'src.agent.core.AgentDeps'>`

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- ENG-05 is fully closed. v1.0 milestone audit items GAP-01 and GAP-02 resolved.
- No blockers.

---
## Self-Check: PASSED

- FOUND: src/main.py
- FOUND: src/agent/tools/sandbox.py
- FOUND: .planning/phases/07-ollama-cli-streaming-fix/07-01-SUMMARY.md
- FOUND commit: 3c94745 (Task 1)
- FOUND commit: 91925d1 (Task 2)

*Phase: 07-ollama-cli-streaming-fix*
*Completed: 2026-02-28*
