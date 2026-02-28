---
phase: 05-local-model-support-via-ollama
plan: 01
subsystem: infra
tags: [ollama, httpx, provider-config, model-resolution, health-check]

# Dependency graph
requires: []
provides:
  - ProviderConfig dataclass resolving all provider env-vars in one place
  - get_provider_config() with PROVIDER auto-detect + manual override
  - check_ollama_health() async ping of /api/tags endpoint via httpx
  - get_missing_models() identifying required models not yet pulled
  - provider_banner() human-readable startup line for all four providers
  - OllamaUnavailableError sentinel exception
affects:
  - 05-02 (agent core integration)
  - 05-03 (sandbox codegen integration)

# Tech tracking
tech-stack:
  added: [ollama, httpx]
  patterns:
    - "Centralised provider config module — single source of truth for all env-var reading"
    - "Async HTTP health check with timeout; returns (bool, list) never raises"

key-files:
  created:
    - src/agent/provider.py
  modified:
    - requirements.txt

key-decisions:
  - "httpx used for async health check (not requests) — compatibility with async callers in core.py and web_ui.py"
  - "OLLAMA_MODEL as shared fallback for both agent and codegen; OLLAMA_AGENT_MODEL / OLLAMA_CODEGEN_MODEL for independent override"
  - "Provider auto-detect order: GEMINI_API_KEY -> ANTHROPIC_API_KEY -> OPENAI_API_KEY -> gemini default"
  - "check_ollama_health() never raises — callers decide how to handle unreachable Ollama"

patterns-established:
  - "Provider singleton pattern: call get_provider_config() once at startup, pass ProviderConfig around"
  - "Model fallback chain: SPECIFIC_MODEL_VAR -> OLLAMA_MODEL -> hardcoded default (llama3.2)"

requirements-completed: [ENG-05]

# Metrics
duration: 2min
completed: 2026-02-28
---

# Phase 05 Plan 01: Provider Configuration Module Summary

**ProviderConfig dataclass + Ollama health-check module centralising all provider env-var reading with httpx async /api/tags ping and per-role model resolution**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-02-28T07:18:24Z
- **Completed:** 2026-02-28T07:20:06Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Created `src/agent/provider.py` — single contract for provider env-var reading used by Wave 2 plans
- `get_provider_config()` handles PROVIDER override (case-insensitive) and auto-detects from API key chain
- `check_ollama_health()` pings `/api/tags` via `httpx.AsyncClient` with 5s timeout; returns `(bool, list[str])` without raising
- `get_missing_models()` performs exact-string deduplication check against pulled models list
- `provider_banner()` returns formatted startup line for all four providers (ollama, gemini, anthropic, openai)
- Added `ollama` and `httpx` to `requirements.txt`

## Task Commits

Each task was committed atomically:

1. **Task 1: Add ollama to requirements.txt** - `9be4043` (chore)
2. **Task 2: Create src/agent/provider.py** - `e03a4c1` (feat)

**Plan metadata:** _(docs commit follows)_

## Files Created/Modified
- `src/agent/provider.py` - ProviderConfig dataclass, get_provider_config(), check_ollama_health(), get_missing_models(), provider_banner(), OllamaUnavailableError
- `requirements.txt` - Added ollama and httpx packages

## Decisions Made
- httpx chosen over requests for async compatibility with Chainlit/Pydantic AI callers
- OLLAMA_MODEL acts as shared fallback for both agent and codegen model names; fine-grained OLLAMA_AGENT_MODEL / OLLAMA_CODEGEN_MODEL override independently
- Provider auto-detect preserves existing env-key chain (GEMINI -> ANTHROPIC -> OPENAI -> gemini default)
- check_ollama_health() returns (False, []) on any connection/timeout error rather than raising — callers (Wave 2) decide whether to abort or warn

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Used venv Python for verification**
- **Found during:** Task 2 verification
- **Issue:** System Python 3.14 does not have httpx installed; standard `python3` command fails import
- **Fix:** Used `/home/brassy/github/ironclaw/venv/bin/python3` for all verification commands; httpx already present in project venv at version 0.28.1
- **Files modified:** None (no code change, environment-only discovery)
- **Verification:** All assertions passed with venv Python
- **Committed in:** N/A (no code change required)

---

**Total deviations:** 1 (1 blocking — environment discovery, no code change)
**Impact on plan:** Zero code impact. Venv already contained httpx; verification ran cleanly.

## Issues Encountered
- System Python 3.14 lacks httpx; project venv at `/home/brassy/github/ironclaw/venv/` has it. All future verification in phase 05 should use the venv interpreter.

## User Setup Required
None — provider.py reads env vars already documented in CLAUDE.md. New vars (PROVIDER, OLLAMA_MODEL, etc.) are optional with sensible defaults.

## Next Phase Readiness
- `src/agent/provider.py` is ready to import in Wave 2 plans
- `get_provider_config()` and `check_ollama_health()` are the primary integration points for 05-02 (core.py) and 05-03 (sandbox.py)
- All exports verified: ProviderConfig, get_provider_config, check_ollama_health, get_missing_models, provider_banner, OllamaUnavailableError

## Self-Check: PASSED

- FOUND: src/agent/provider.py
- FOUND: requirements.txt (with ollama and httpx)
- FOUND: 05-01-SUMMARY.md
- FOUND commit 9be4043 (chore: requirements.txt)
- FOUND commit e03a4c1 (feat: provider.py)

---
*Phase: 05-local-model-support-via-ollama*
*Completed: 2026-02-28*
