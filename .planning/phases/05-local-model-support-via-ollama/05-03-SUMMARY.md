---
phase: 05-local-model-support-via-ollama
plan: 03
subsystem: ui
tags: [ollama, chainlit, cli, startup, health-check, provider-banner, fallback]

# Dependency graph
requires:
  - phase: 05-01
    provides: get_provider_config(), check_ollama_health(), get_missing_models(), provider_banner(), OllamaUnavailableError
  - phase: 05-02
    provides: provider-aware ironclaw_agent, run_system_task() with Ollama branch
provides:
  - Provider banner printed on CLI startup for all providers
  - CLI Ollama health check with interactive fallback prompt and pull-command hint
  - CLI __main__ guard allowing PROVIDER=ollama without cloud API keys
  - Web UI provider banner embedded in on_chat_start welcome message
  - Web UI Ollama health check with AskActionMessage fallback/abort buttons
  - Web UI pull-command hint and early return if required models not pulled
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Startup health check pattern: call check_ollama_health() in entry points before entering main loop"
    - "CLI fallback: input() prompt -> pop PROVIDER env var -> re-resolve config"
    - "Web UI fallback: AskActionMessage -> pop PROVIDER env var -> re-resolve config"

key-files:
  created: []
  modified:
    - src/main.py
    - src/web_ui.py

key-decisions:
  - "Provider banner included in web_ui.py welcome message (not a separate message) for a cleaner startup UX"
  - "__main__ guard updated to allow PROVIDER=ollama without cloud API keys — Ollama is a valid standalone provider"
  - "AskActionMessage payload access via .get() defensively — Chainlit 2.x returns None if user dismisses without choosing"

patterns-established:
  - "Entry-point provider check pattern: get_provider_config() -> provider_banner() -> check_ollama_health() if ollama"
  - "Fallback chain: pop PROVIDER env var, re-call get_provider_config() — stateless re-resolution, no special fallback logic"

requirements-completed: [ENG-05]

# Metrics
duration: 1min
completed: 2026-02-28
---

# Phase 05 Plan 03: Startup Integration Summary

**Provider banner and Ollama startup health check wired into both CLI (main.py) and Web UI (web_ui.py) entry points with interactive fallback and pull-command hints**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-02-28T07:31:04Z
- **Completed:** 2026-02-28T07:31:59Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `src/main.py`: provider_banner() printed on every startup; PROVIDER=ollama triggers health check with "Fall back to cloud? [y/N]" prompt if unreachable; prints "ollama pull {model}" and aborts if models missing; `__main__` guard updated to allow Ollama without cloud API keys
- `src/web_ui.py`: provider_banner() embedded in on_chat_start welcome message; PROVIDER=ollama triggers health check with AskActionMessage offering "Fall back to cloud" / "Abort session"; pull-command hint shown with early return if models not pulled
- Both files verified with ast.parse — no syntax errors

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Ollama startup check and provider banner to src/main.py** - `e88d594` (feat)
2. **Task 2: Add Ollama startup check and provider banner to src/web_ui.py** - `487e706` (feat)

**Plan metadata:** _(docs commit follows)_

## Files Created/Modified
- `src/main.py` - Provider banner + Ollama health check in main(); __main__ guard updated for PROVIDER=ollama
- `src/web_ui.py` - Provider banner in welcome message + Ollama health check with AskActionMessage in on_chat_start()

## Decisions Made
- Provider banner included in the welcome message content (not a separate cl.Message call) to keep startup UX clean
- `__main__` guard updated to check `_startup_cfg.provider != "ollama"` before requiring cloud API keys — Ollama is a fully independent provider
- AskActionMessage payload access uses `.get()` defensively per Chainlit 2.x API — returns None if user closes without choosing (defaults to "abort")

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Already done] main.py main() function was already partially implemented**
- **Found during:** Task 1 start (file inspection)
- **Issue:** The `main()` async function already contained the provider banner and Ollama health check code (lines 31-56). Only the `__main__` guard at lines 130-137 still used the old cloud-key-only check.
- **Fix:** Applied only the `__main__` guard update; skipped re-adding the already-present main() code to avoid duplication
- **Files modified:** src/main.py (guard only)
- **Verification:** ast.parse + all assertions passed including 'PROVIDER=ollama' in guard
- **Committed in:** e88d594

---

**Total deviations:** 1 (1 pre-completed sub-task — no scope creep)
**Impact on plan:** Zero scope creep. The main() body was already wired in a prior session; only the guard update was needed.

## Issues Encountered
- System Python 3.14 lacks project dependencies; used venv interpreter `/home/brassy/github/ironclaw/venv/bin/python3` for all verification (consistent with 05-01 and 05-02 discoveries).

## User Setup Required
None — all behaviour is driven by existing env vars (PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL, etc.) documented in CLAUDE.md.

## Next Phase Readiness
- Phase 05 is now complete: provider.py (05-01), agent/sandbox integration (05-02), and entry-point startup flows (05-03) all done
- ENG-05 (local model support via Ollama) fully delivered
- No remaining blockers

## Self-Check: PASSED

- FOUND: src/main.py (with check_ollama_health, provider_banner, Fall back to cloud, ollama pull, PROVIDER=ollama guard)
- FOUND: src/web_ui.py (with check_ollama_health, provider_banner, AskActionMessage, Fall back, ollama pull)
- FOUND commit e88d594 (feat: main.py startup wiring)
- FOUND commit 487e706 (feat: web_ui.py startup wiring)
- FOUND: 05-03-SUMMARY.md

---
*Phase: 05-local-model-support-via-ollama*
*Completed: 2026-02-28*
