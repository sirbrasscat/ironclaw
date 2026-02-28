---
phase: 05-local-model-support-via-ollama
plan: 02
subsystem: infra
tags: [ollama, pydantic-ai, streaming, provider-routing, codegen, error-handling]

# Dependency graph
requires:
  - phase: 05-01
    provides: ProviderConfig dataclass, get_provider_config(), OllamaUnavailableError
provides:
  - Provider-aware ironclaw_agent using OllamaProvider+OpenAIModel or cloud model strings
  - Provider-aware run_system_task() routing to ollama_lib.generate(stream=True) or Gemini
  - _parse_code_blocks() shared fence-parsing helper (no duplication between branches)
  - Mid-session OllamaUnavailableError with base URL in message on connection failure
affects:
  - 05-03 (sandbox codegen integration — uses same provider.py + sandbox.py)

# Tech tracking
tech-stack:
  added: [ollama (python client library, 0.6.1)]
  patterns:
    - "Provider branching in run_system_task: single if/else on config.provider at call time"
    - "Streaming codegen: ollama_lib.generate(stream=True) iterating chunk['response'] tokens"
    - "OllamaProvider + OpenAIModel for pydantic-ai Ollama agent model (OpenAI-compatible API)"

key-files:
  created: []
  modified:
    - src/agent/core.py
    - src/agent/tools/sandbox.py

key-decisions:
  - "OllamaProvider + OpenAIModel used for pydantic-ai Ollama model (not string prefix 'ollama:') — pydantic-ai's OpenAI-compat Ollama provider API is explicit and testable"
  - "chunk.get('response', '') used to access Ollama streaming tokens (ollama-py dict API)"
  - "_parse_code_blocks() extracted as instance method to deduplicate fence-parsing between Ollama and Gemini branches"
  - "OLLAMA_HOST env var set before ollama_lib.generate() so ollama-py reads it for the connection"

patterns-established:
  - "Provider-aware dispatch: call get_provider_config() inside run_system_task() — config is cheap and stateless"
  - "Error isolation: Ollama try/except wraps both generate() call AND stream iteration — catches mid-stream drops"

requirements-completed: [ENG-05]

# Metrics
duration: 10min
completed: 2026-02-27
---

# Phase 05 Plan 02: Agent Core Integration Summary

**Provider-aware agent using OllamaProvider+OpenAIModel for pydantic-ai and ollama_lib.generate(stream=True) for code generation, with OllamaUnavailableError on connection drops**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-02-27T00:00:00Z
- **Completed:** 2026-02-27T00:10:00Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- core.py: Provider-aware ironclaw_agent using `OllamaProvider` + `OpenAIModel` for Ollama; cloud model strings for gemini/anthropic/openai unchanged
- sandbox.py: `run_system_task()` branches on `config.provider`: Ollama path streams via `ollama_lib.generate(stream=True)` accumulating tokens and forwarding each to `on_output` callback
- sandbox.py: `_parse_code_blocks()` helper extracted — shared fence-parsing logic between Ollama and Gemini branches, no duplication
- sandbox.py: Ollama branch wraps both `generate()` call and stream iteration in `try/except` raising `OllamaUnavailableError` with base URL in message — no silent retry or fallback
- `confirm_execution()` unchanged — Docker execution path is provider-agnostic
- Installed `ollama` Python client (0.6.1) into project venv (was missing despite being in requirements.txt)

## Task Commits

Each task was committed atomically:

1. **Task 1: Provider-aware model selection in core.py** - `26f29ec` (feat) — already committed before this plan execution
2. **Task 2+3: Provider-aware sandbox.py with streaming and error handling** - `698d998` (feat)

**Plan metadata:** _(docs commit follows)_

## Files Created/Modified
- `src/agent/core.py` - OllamaProvider+OpenAIModel for ollama; cloud string models for others; uses get_provider_config()
- `src/agent/tools/sandbox.py` - Provider-aware run_system_task(), _parse_code_blocks() helper, OllamaUnavailableError wrapping

## Decisions Made
- `OllamaProvider + OpenAIModel` (not `"ollama:model"` string prefix) — pydantic-ai's Ollama integration uses OpenAI-compatible endpoints; the explicit constructor is clearer
- `chunk.get("response", "")` — ollama-py streaming chunks are dicts with a `"response"` key
- `_parse_code_blocks()` extracted as instance method: shared between Ollama and Gemini branches prevents fence-parsing drift
- `OLLAMA_HOST` env var set before `ollama_lib.generate()` — the ollama-py library reads this for base URL

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed missing ollama Python package**
- **Found during:** Task 2 verification
- **Issue:** `import ollama` failed — package was in requirements.txt but not installed in project venv
- **Fix:** Ran `/home/brassy/github/ironclaw/venv/bin/pip install ollama` (installed 0.6.1)
- **Files modified:** None (package install only; requirements.txt already listed it from 05-01)
- **Verification:** `import ollama as ollama_lib` succeeds in venv
- **Committed in:** N/A (no code change required)

**2. [Rule 1 - Already done] Task 1 (core.py) was already committed**
- **Found during:** Plan start
- **Issue:** `26f29ec` `feat(05-02): wire provider-aware model selection into core.py` already committed to master — core.py was already updated with OllamaProvider+OpenAIModel pattern
- **Fix:** Verified import works for both PROVIDER=gemini and PROVIDER=ollama, proceeded to Task 2
- **Files modified:** None (already complete)
- **Committed in:** 26f29ec (pre-existing commit)

---

**Total deviations:** 2 (1 blocking environment fix, 1 pre-completed task)
**Impact on plan:** Zero scope creep. Blocking fix was environment-only (no code change). Pre-completed Task 1 reduced execution time.

## Issues Encountered
- System Python 3.14 lacks ollama; project venv at `/home/brassy/github/ironclaw/venv/` is the correct interpreter for all verification. Consistent with 05-01 discovery.

## User Setup Required
None — configuration is via existing env vars (PROVIDER, OLLAMA_MODEL, etc.) already documented.

## Next Phase Readiness
- `src/agent/core.py` and `src/agent/tools/sandbox.py` are fully provider-aware
- Ollama streaming code generation path is implemented and tested
- 05-03 (sandbox/web_ui integration) can build on this provider routing

## Self-Check: PASSED

- FOUND: src/agent/core.py (with OllamaProvider + get_provider_config)
- FOUND: src/agent/tools/sandbox.py (with _parse_code_blocks, OllamaUnavailableError, stream=True)
- FOUND commit 26f29ec (feat: core.py provider-aware model)
- FOUND commit 698d998 (feat: sandbox.py provider-aware streaming)

---
*Phase: 05-local-model-support-via-ollama*
*Completed: 2026-02-27*
