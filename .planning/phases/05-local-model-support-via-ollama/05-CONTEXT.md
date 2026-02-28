# Phase 5: Local Model Support via Ollama - Context

**Gathered:** 2026-02-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Add Ollama as a local LLM backend so IronClaw can run fully offline without cloud API keys. Users configure a local Ollama model via env vars; the agent uses it for both the Pydantic AI agent loop and the direct code-generation step (run_system_task). Both CLI and Web UI are covered.

</domain>

<decisions>
## Implementation Decisions

### Provider Selection
- Explicit `PROVIDER` env var with accepted values: `ollama`, `gemini`, `anthropic`, `openai`
- `PROVIDER=ollama` routes all LLM calls to Ollama
- If `PROVIDER=gemini` but `GEMINI_API_KEY` is unset, fall through to the next cloud provider (existing fallback chain behavior — no hard error)
- Active provider displayed on startup: CLI prints `[*] Provider: Ollama (llama3.2 / llama3.2)`; Web UI shows it in the welcome message or chat header

### Model Configuration
- `OLLAMA_MODEL` — base model used for all roles if role-specific vars are not set
- `OLLAMA_AGENT_MODEL` — model for Pydantic AI agent calls (defaults to `OLLAMA_MODEL`)
- `OLLAMA_CODEGEN_MODEL` — model for the `run_system_task` code-generation call (defaults to `OLLAMA_MODEL`)
- `OLLAMA_BASE_URL` — Ollama endpoint, defaults to `http://localhost:11434`; overridable for remote or custom-port Ollama
- Model names are exact Ollama tags (e.g. `llama3.2`, `mistral:7b`) — no friendly-name mapping

### Ollama API Integration
- Use the Ollama **native Python API** (not the OpenAI-compatible `/v1/` endpoint)
- Pydantic AI remains the tool orchestration layer — Ollama is swapped in as the underlying model provider
- Structured output (CodeExecutionRequest) uses Ollama's `format='json'` JSON mode — same HITL contract maintained
- Streaming: use Ollama's streaming API so the Web UI shows tokens as they arrive (same UX as cloud providers)

### Startup Behaviour
- On startup with `PROVIDER=ollama`: ping Ollama at `OLLAMA_BASE_URL` and verify both `OLLAMA_AGENT_MODEL` and `OLLAMA_CODEGEN_MODEL` are available
- If Ollama is **unreachable**: display a warning (don't crash), then interactively ask the user whether to fall back to a cloud provider
  - CLI: `Ollama unavailable at http://localhost:11434. Fall back to cloud? [y/N]`
  - Web UI: show an action button with the same choice
- If model is **not pulled**: print pull command (`ollama pull <model>`) and exit — no auto-pull

### Mid-Session Failure
- If Ollama connection drops during a session: surface a clear error message and pause — do not silently retry or fall back

### Scope
- Both CLI (`src/main.py`) and Web UI (`src/web_ui.py`) must support Ollama
- All LLM calls replaced when `PROVIDER=ollama`:
  - Pydantic AI agent calls (planning, confirmation, tool routing)
  - Direct code-generation call in `run_system_task`

### Claude's Discretion
- System prompt strategy: whether to use the same prompt for Ollama or adjust for local model capabilities
- Exact Ollama Python library usage patterns and streaming implementation details
- Internal provider abstraction / factory pattern in `src/agent/core.py`

</decisions>

<specifics>
## Specific Ideas

- The startup provider banner should clearly show which model(s) are active, e.g. `[*] Provider: Ollama — agent: llama3.2, codegen: llama3.2`
- Fallback interaction must be non-surprising — the user explicitly chooses to switch, never silently

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-local-model-support-via-ollama*
*Context gathered: 2026-02-27*
