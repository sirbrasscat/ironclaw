# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IronClaw is a self-hosted AI agent system that gives an LLM controlled access to a Docker sandbox for system operations. Users interact via CLI or a Chainlit web UI, review AI-generated code before it runs, and the agent executes only after explicit approval (Human-in-the-Loop).

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Build the Docker sandbox image (required before running)
docker build -t ironclaw-agent .

# Run CLI mode
python3 src/main.py
python3 src/main.py --session my-session

# Run web UI
chainlit run src/web_ui.py

# Run all tests
pytest tests/

# Run a single test file
pytest tests/test_hitl.py

# Run a specific test
pytest tests/test_hitl.py::test_name -v
```

## Environment Setup

Copy `.env` with these keys:

**Provider selection** (auto-detected from API keys; override with `PROVIDER=ollama|gemini|anthropic|openai`):
- `GEMINI_API_KEY` — selects Gemini provider (gemini-2.5-flash); checked first in auto-detect
- `ANTHROPIC_API_KEY` — selects Anthropic provider (claude-3-5-sonnet-latest)
- `OPENAI_API_KEY` — selects OpenAI provider (gpt-4o)

**Ollama** (when `PROVIDER=ollama`):
- `OLLAMA_BASE_URL` — default `http://localhost:11434`
- `OLLAMA_MODEL` — fallback model name (default: `llama3.2`)
- `OLLAMA_AGENT_MODEL` — overrides agent model specifically
- `OLLAMA_CODEGEN_MODEL` — overrides code-generation model specifically

**Web UI:**
- `CHAINLIT_PASSWORD` — web UI password (default: `ironclaw`)
- `CHAINLIT_AUTH_SECRET` — session encryption secret for Chainlit

## Architecture

The system is built around a two-phase HITL (Human-in-the-Loop) execution model:

**Phase 1 — Planning:** `run_system_task(task)` calls the Gemini API directly via `google-genai` SDK to generate code blocks. It returns a `CodeExecutionRequest` Pydantic model (never executes code). The Pydantic AI agent surfaces this as a structured output to the UI.

**Phase 2 — Execution:** After the user approves, `confirm_execution()` calls `interpreter.computer.run()` using the configured Docker-backed language classes. Output is streamed back via an `on_output` callback.

**Key design point:** Open Interpreter (`interpreter`) is used only as an execution engine — its own HITL loop is disabled (`interpreter.auto_run = True`). The HITL is enforced at the Pydantic AI layer via `CodeExecutionRequest`.

### Module Map

| Module | Purpose |
|--------|---------|
| `src/agent/core.py` | Pydantic AI agent definition; tool registration; model selection from env |
| `src/agent/provider.py` | Provider config resolution; Ollama health check; `ProviderConfig` dataclass |
| `src/agent/prompts.py` | System prompt |
| `src/agent/tools/sandbox.py` | `SandboxedTool` class: code generation + execution; `CodeExecutionRequest` / `CodeBlock` models |
| `src/agent/tools/workspace.py` | Workspace file listing; snapshot/diff utilities for detecting file changes |
| `src/sandbox/manager.py` | Docker container lifecycle (`ironclaw-agent` image) |
| `src/sandbox/languages.py` | `DockerPython` and `DockerShell` — Open Interpreter language classes that exec inside the container |
| `src/database/manager.py` | Async SQLite via SQLAlchemy; stores `ModelMessage` JSON blobs per session |
| `src/database/models.py` | `ChatSession` and `ChatMessage` ORM models |
| `src/main.py` | CLI entry point; session loading; interactive approval loop |
| `src/web_ui.py` | Chainlit UI; streaming; file upload/download; code approval actions |

### Data Flow (Web UI)

1. User message → `on_message()` in `web_ui.py`
2. `ironclaw_agent.run_stream()` → may produce `CodeExecutionRequest` or plain `str`
3. If `CodeExecutionRequest`: show code + `AskActionMessage` approval buttons
4. On approve: second `ironclaw_agent.run_stream("Confirm the execution.")` triggers `confirm_execution` tool
5. Execution output streamed via `cl.Step("Docker Execution")`
6. `send_file_diff()` checks workspace for new/modified files and offers downloads

### Singleton Pattern

`SandboxedTool` is a module-level singleton (`_sandbox_tool` in `sandbox.py`). It manages a single Docker container and `pending_blocks` state between the planning and execution calls. This means concurrent requests sharing a process would conflict — the current design assumes one active user at a time per process.

## GSD Workflow

This repo uses a `get-shit-done` skill system. Use `gsd-*` commands (e.g. `/gsd-execute-phase`) to trigger workflows; skill files live in `.github/skills/gsd-*/SKILL.md`. Do not apply GSD workflows unless explicitly asked.

## Python 3.14 Compatibility

`src/web_ui.py` contains a `nest_asyncio` / `asyncio.current_task` patch at the top of the file. This is required for Python 3.14 where `asyncio.current_task()` reads C-level storage that `nest_asyncio` doesn't update. Do not remove it.
