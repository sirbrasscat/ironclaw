---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: unknown
last_updated: "2026-02-27T00:10:00Z"
progress:
  total_phases: 5
  completed_phases: 4
  total_plans: 12
  completed_plans: 11
---

# Project State: IronClaw Agent System

## Project Reference
**Core Value**: Empowering users with a proactive, system-aware AI assistant that can be controlled from anywhere safely.
**Current Focus**: Phase 05 — Local model support via Ollama.

## Current Position
**Phase**: 05-local-model-support-via-ollama
**Plan**: 03 (next)
**Status**: In progress — 05-01 and 05-02 complete, 05-03 remaining
**Progress**: [█████████████████████▓] 92% (11/12 plans)

## Performance Metrics
- **Requirement Coverage**: ENG-05 in progress
- **Phase Completion**: 4/5
- **Research Confidence**: HIGH

## Accumulated Context
### Decisions
- Using Pydantic AI for orchestration (from research).
- Mandatory Docker sandboxing for security (from research).
- SQLite/SQLAlchemy for persistence (from research).
- Using google-genai SDK directly for code generation in run_system_task (decoupled from OI's own LLM loop).
- Gemini model: gemini-3-flash-preview.
- Storing Pydantic AI ModelMessage objects as JSON in SQLite for Phase 2 persistence.
- [Phase 02-02]: Use result.new_messages() for incremental DB save to avoid duplicates; fall back to 'kind' field when 'role' absent in ModelMessage dicts.
- [Phase 04]: Used snapshot-based diffing to detect file changes in the workspace for UI downloads.
- [Phase 05]: Skipped Telegram integration as per user request.
- [Phase 05-01]: httpx used for async Ollama health check; OLLAMA_MODEL as shared fallback for agent+codegen; check_ollama_health() never raises.
- [Phase 05-01]: Provider auto-detect order: GEMINI_API_KEY -> ANTHROPIC_API_KEY -> OPENAI_API_KEY -> gemini default.
- [Phase 05-02]: OllamaProvider+OpenAIModel for pydantic-ai Ollama agent (not string prefix); chunk.get('response','') for streaming token accumulation.
- [Phase 05-02]: _parse_code_blocks() extracted as shared helper; OLLAMA_HOST env var set before ollama_lib.generate() so library reads it.

### Roadmap Evolution
- Phase 5 added: Local model support via Ollama

### Todos
- [x] Execute Phase 2: Persistence & History.
- [x] Execute Phase 3: Web Dashboard & Security.
- [x] Execute Phase 4: Workspace & File Management.
- [x] Execute Phase 5-01: Provider config module.
- [x] Execute Phase 5-02: Agent core integration.
- [ ] Execute Phase 5-03: Sandbox codegen integration.

### Blockers
- None.

## Session Continuity
**Last Action**: Executed 05-02 (agent core integration). Updated core.py with OllamaProvider+OpenAIModel; updated sandbox.py with provider-aware run_system_task(), _parse_code_blocks() helper, and OllamaUnavailableError streaming error handling.
**Next Step**: Execute 05-03 (web UI / startup integration — provider_banner, health check display, OllamaUnavailableError handling in web_ui.py and main.py).
