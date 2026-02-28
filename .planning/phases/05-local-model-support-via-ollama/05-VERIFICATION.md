---
phase: 05-local-model-support-via-ollama
verified: 2026-02-28T09:10:00Z
status: passed
score: 12/12 must-haves verified
re_verification:
  previous_status: gaps_found
  previous_score: 10/12
  gaps_closed:
    - "Ollama code generation streams tokens through the on_output callback progressively"
    - "ENG-05 traceability table in REQUIREMENTS.md is complete"
  gaps_remaining: []
  regressions: []
human_verification:
  - test: "Run IronClaw CLI with PROVIDER=ollama and Ollama running; observe code generation step"
    expected: "Agent generates code using Ollama; tokens appear progressively rather than all at once"
    why_human: "Streaming UX requires a running Ollama instance and visual inspection of output timing"
  - test: "Run IronClaw CLI with PROVIDER=ollama and Ollama stopped; start the CLI"
    expected: "Prints provider banner, then prompts 'Ollama unavailable at http://localhost:11434. Fall back to cloud? [y/N]'"
    why_human: "Requires an unresponsive Ollama endpoint to trigger the fallback path"
  - test: "Run Chainlit web UI with PROVIDER=ollama and Ollama stopped; open a chat"
    expected: "Welcome message shows provider banner; AskActionMessage with 'Fall back to cloud' / 'Abort session' buttons appears"
    why_human: "Chainlit UI behavior cannot be verified programmatically"
---

# Phase 5: Local Model Support via Ollama — Verification Report

**Phase Goal:** Allow users to run IronClaw with a locally-hosted Ollama model instead of cloud APIs.
**Verified:** 2026-02-28T09:10:00Z
**Status:** passed
**Re-verification:** Yes — after gap closure (Plan 05-04)

## Re-verification Summary

The initial verification (2026-02-28T08:18:57Z) found 2 gaps (score 10/12). Plan 05-04 was executed to close them via commits `d5d5a11` and `373825a`. This re-verification confirms both gaps are closed and no regressions were introduced.

**Gaps closed:**

1. **Streaming callback not wired** — `@ironclaw_agent.tool_plain` in `core.py` changed to `@ironclaw_agent.tool` (line 50); `ctx: RunContext[AgentDeps]` added as first parameter; `on_output = ctx.deps.on_output if ctx.deps else None` extracted and forwarded to `_run_system_task(task, on_output=on_output)`. Module-level `run_system_task` wrapper in `sandbox.py` (line 179) updated from `(task: str)` to `(task: str, on_output: Optional[Callable[[str], None]] = None)` and forwards to `get_sandbox_tool().run_system_task(task, on_output=on_output)`.

2. **REQUIREMENTS.md traceability stale** — ENG-05 row updated from `05-01, 05-02 | In Progress` to `05-01, 05-02, 05-03 | Complete`. Last updated date set to 2026-02-28.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | PROVIDER=ollama reads OLLAMA_MODEL, OLLAMA_AGENT_MODEL, OLLAMA_CODEGEN_MODEL, OLLAMA_BASE_URL from env | VERIFIED | `get_provider_config()` in provider.py resolves all four env vars with correct fallback chain |
| 2 | Provider module can ping Ollama health endpoint and report reachability | VERIFIED | `check_ollama_health()` uses `httpx.AsyncClient` to GET `/api/tags` with 5s timeout; returns `(bool, list[str])` without raising |
| 3 | Provider module can list locally pulled models and check if a given model tag is available | VERIFIED | `get_missing_models()` performs exact-match plus tagless base-name matching against pulled models list |
| 4 | Provider config object exposes resolved agent_model and codegen_model names | VERIFIED | `ProviderConfig.ollama_agent_model` and `ollama_codegen_model` populated; assertions pass in import test |
| 5 | When PROVIDER=ollama, Pydantic AI agent uses OllamaModel not Google/Anthropic/OpenAI model | VERIFIED | core.py lines 19-28: `OllamaProvider + OpenAIModel` constructed for Ollama; cloud string models for others |
| 6 | When PROVIDER=ollama, run_system_task calls Ollama for code generation instead of google-genai | VERIFIED | sandbox.py lines 101-120: `config.provider == "ollama"` branch calls `ollama_lib.generate(stream=True)` |
| 7 | HITL contract (CodeExecutionRequest) is preserved identically for Ollama provider | VERIFIED | `CodeExecutionRequest` fields `status/blocks/reasoning` unchanged; both branches call `_parse_code_blocks()` and return the same model |
| 8 | Ollama code generation streams tokens through the on_output callback progressively | VERIFIED | core.py line 50: `@ironclaw_agent.tool` (not tool_plain); line 56: `on_output = ctx.deps.on_output if ctx.deps else None`; line 57: forwarded to `_run_system_task(task, on_output=on_output)`. sandbox.py line 179: module-level wrapper accepts `on_output` and forwards to `SandboxedTool.run_system_task()`. Callback forwarding at sandbox.py lines 114-115 confirmed intact. |
| 9 | Cloud provider path is unchanged when PROVIDER is not ollama | VERIFIED | sandbox.py else branch (lines 121-129) is the original Gemini block unmodified; core.py cloud branches identical to pre-phase strings |
| 10 | Mid-session Ollama connection failure surfaces a clear error and does not silently retry | VERIFIED | sandbox.py lines 116-120: try/except raises `OllamaUnavailableError` with base URL; no fallback or retry |
| 11 | CLI prints provider banner on startup showing active provider and model names | VERIFIED | main.py lines 31-32: `_cfg = get_provider_config(); print(provider_banner(_cfg))` inside `main()` before event loop |
| 12 | CLI with PROVIDER=ollama pings Ollama health; if unreachable prompts user to fall back to cloud or abort | VERIFIED | main.py lines 35-56: health check, `input("... Fall back to cloud? [y/N]")`, fallback via env pop or abort |
| 13 | CLI exits with pull command if required models are not pulled | VERIFIED | main.py lines 51-56: `get_missing_models()` called; prints `ollama pull {m}` and returns |
| 14 | Web UI welcome message includes provider banner | VERIFIED | web_ui.py line 91: `_banner = provider_banner(_cfg)`; line 92: included in welcome message send |
| 15 | Web UI with PROVIDER=ollama shows AskActionMessage fallback button if Ollama is unreachable | VERIFIED | web_ui.py lines 95-115: `cl.AskActionMessage` with "Fall back to cloud" / "Abort session" actions |
| 16 | Web UI exits startup path with pull command message if required models are not pulled | VERIFIED | web_ui.py lines 117-123: `get_missing_models()` called; sends pull command message and returns early |

**Score:** 12/12 truths fully verified (gap #8 closed by Plan 05-04; administrative gap #2 closed by same plan)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/agent/provider.py` | ProviderConfig dataclass, get_provider_config(), check_ollama_health(), OllamaUnavailableError | VERIFIED | All 6 exports present and substantive; no stubs |
| `requirements.txt` | ollama and httpx package dependencies | VERIFIED | Both lines present |
| `src/agent/core.py` | Provider-aware ironclaw_agent construction; @ironclaw_agent.tool for run_system_task with RunContext | VERIFIED | `@ironclaw_agent.tool` (line 50, not tool_plain); `ctx: RunContext[AgentDeps]` first param; `on_output` threaded from `ctx.deps` |
| `src/agent/tools/sandbox.py` | Provider-aware run_system_task (Ollama streaming or Gemini); module-level wrapper accepts on_output | VERIFIED | Module-level wrapper (line 179) signature `(task: str, on_output: Optional[Callable[[str], None]] = None)`; forwards to `SandboxedTool.run_system_task(task, on_output=on_output)` |
| `src/main.py` | Startup Ollama health check, fallback prompt, provider banner print | VERIFIED | `check_ollama_health`, `provider_banner`, `Fall back to cloud`, `ollama pull` all present and wired |
| `src/web_ui.py` | Startup Ollama health check, AskActionMessage fallback, provider banner in welcome | VERIFIED | All required patterns present and wired in `on_chat_start()` |
| `.planning/REQUIREMENTS.md` | ENG-05 row: 05-01, 05-02, 05-03 with Complete status | VERIFIED | Line 51: `| ENG-05 | Phase 5 | 05-01, 05-02, 05-03 | Complete |` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `src/agent/provider.py` | Ollama /api/tags endpoint | `httpx.AsyncClient GET` in `check_ollama_health()` | WIRED | `async with httpx.AsyncClient(timeout=5.0) as client: response = await client.get(url)` |
| `src/agent/core.py` | `src/agent/provider.py` | `get_provider_config()` at module load | WIRED | Line 8: `from src.agent.provider import get_provider_config`; line 17: `_provider_config = get_provider_config()` |
| `src/agent/core.py` | `src/agent/tools/sandbox.py` | `run_system_task(task, on_output=on_output)` where on_output comes from `ctx.deps` | WIRED | Line 56: `on_output = ctx.deps.on_output if ctx.deps else None`; line 57: `return _run_system_task(task, on_output=on_output)` — gap closed by Plan 05-04 |
| `src/agent/tools/sandbox.py` | `src/agent/provider.py` | `get_provider_config()` in `run_system_task` | WIRED | Line 10: import; line 92: `config = get_provider_config()` |
| `src/agent/tools/sandbox.py` | ollama python library | `ollama.generate(stream=True)` | WIRED | Line 6: `import ollama as ollama_lib`; lines 105-115: `ollama_lib.generate(model=..., stream=True)` with token loop |
| `src/agent/tools/sandbox.py` | `on_output` callback | `token` forwarding in Ollama branch | WIRED | Module-level wrapper (line 179) accepts `on_output`; `SandboxedTool.run_system_task` (line 114-115): `if on_output: on_output(token)` — gap closed |
| `src/main.py` | `src/agent/provider.py` | `check_ollama_health()`, `provider_banner()`, `get_missing_models()` | WIRED | Line 18: full import; lines 32-56: all three functions called at startup |
| `src/web_ui.py` | `src/agent/provider.py` | `check_ollama_health()`, `provider_banner()`, `get_missing_models()` | WIRED | Line 41: full import; lines 91-123: all three functions called in `on_chat_start()` |

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| ENG-05 | 05-01, 05-02, 05-03, 05-04 | Local model support (Ollama/LocalAI integration) for 100% private execution | SATISFIED | provider.py, core.py, sandbox.py, main.py, web_ui.py all implement Ollama routing; PROVIDER=ollama enables fully offline operation; on_output callback now fully wired for streaming UX |
| ENG-05 (traceability table) | REQUIREMENTS.md | Traceability row accurate | SATISFIED | Line 51: `| ENG-05 | Phase 5 | 05-01, 05-02, 05-03 | Complete |` — gap closed by Plan 05-04 |

### Regression Check (Previously Passing Items)

| Item | Check | Result |
|------|-------|--------|
| `src/agent/core.py` imports cleanly with PROVIDER=gemini | Python import test | PASS — "core.py import OK" |
| `@ironclaw_agent.tool_plain` not used for run_system_task | Source inspection | PASS — tool_plain only on `list_workspace_files` (line 67) |
| Module-level sandbox wrapper has `on_output` in signature | `inspect.signature(run_system_task)` | PASS — `(task: str, on_output: Callable[[str], NoneType] | None = None)` |
| main.py startup wiring intact (check_ollama_health, provider_banner, AskActionMessage) | grep | PASS — all patterns present |
| web_ui.py startup wiring intact | grep | PASS — all patterns present |
| Commits documented in SUMMARY exist in repo | `git show` | PASS — `d5d5a11` and `373825a` both verified |

### Anti-Patterns Found

No new anti-patterns introduced by Plan 05-04. The @tool_plain -> @tool change is a correct pydantic-ai API usage, not a workaround.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | — | — | — | — |

**Note:** A pre-existing test failure in `tests/test_hitl.py::test_run_system_task_generates_request` was documented in the 05-04 SUMMARY as out-of-scope — the test mocks `genai.Client` (Gemini path) but not `ollama_lib.generate` (Ollama path), so it fails when Ollama is running. This predates Phase 05-04 and is logged to `deferred-items.md`.

### Human Verification Required

#### 1. Ollama Streaming UX (Gap Now Fixed)

**Test:** With Ollama running, set `PROVIDER=ollama OLLAMA_MODEL=llama3.2`, run the CLI, ask the agent to "list files in /tmp". Watch the code generation output.
**Expected:** Tokens from Ollama appear progressively during the code-generation step, not all at once after a delay.
**Why human:** Requires a running Ollama instance and real-time output observation.

#### 2. CLI Ollama Unreachable Fallback

**Test:** Stop Ollama, set `PROVIDER=ollama`, run `python3 src/main.py`. When prompted "Fall back to cloud? [y/N]", type "y".
**Expected:** Session continues using Gemini (or whichever cloud key is set); banner updates to show the new provider.
**Why human:** Requires an unreachable Ollama endpoint to trigger the interactive prompt path.

#### 3. Web UI Ollama Unreachable Fallback

**Test:** Stop Ollama, set `PROVIDER=ollama`, run `chainlit run src/web_ui.py`, open the chat. Observe the startup AskActionMessage.
**Expected:** Welcome message shows Ollama banner; then AskActionMessage appears with "Fall back to cloud" and "Abort session" buttons.
**Why human:** Chainlit UI actions cannot be verified programmatically without a running server.

### Gaps Summary

No gaps remain. Both gaps from the initial verification were closed by Plan 05-04:

**Gap 1 (closed):** The `on_output` callback chain is now fully wired. `core.py` uses `@ironclaw_agent.tool` (not `tool_plain`) so `RunContext[AgentDeps]` is available. `ctx.deps.on_output` is extracted and forwarded through the module-level `run_system_task` wrapper in `sandbox.py` to `SandboxedTool.run_system_task()`, where it forwards each Ollama token progressively. The callback pattern matches the existing `confirm_execution` implementation exactly.

**Gap 2 (closed):** REQUIREMENTS.md traceability row for ENG-05 now reads `05-01, 05-02, 05-03 | Complete`. The last-updated date is 2026-02-28.

---

_Verified: 2026-02-28T09:10:00Z_
_Verifier: Claude (gsd-verifier)_
_Re-verification: Yes (initial: gaps_found 10/12, re-verified: passed 12/12)_
