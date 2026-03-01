# IronClaw

A self-hosted AI agent system that gives an LLM controlled access to a Docker sandbox for system operations. All generated code is shown to the user for review before it runs — no code executes without explicit approval.

## How it works

1. You describe a task in plain English.
2. The agent generates the code required to complete it and shows you the plan.
3. You approve or reject. Only on approval does the code run inside an isolated Docker container.
4. Execution output streams back in real time.

## Interfaces

| Interface | Command |
|-----------|---------|
| CLI | `python3 src/main.py` |
| Web UI (Chainlit) | `chainlit run src/web_ui.py` |

The web UI adds file upload/download, approval buttons, and live execution steps. Both interfaces use the same agent and sandbox backend.

## Setup

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Build the Docker sandbox image**

```bash
docker build -t ironclaw-agent .
```

This image is the only thing that executes code. The host is never touched.

**3. Configure environment**

Create a `.env` file. You need at least one LLM provider:

```env
# Cloud providers (pick one, or set PROVIDER= explicitly)
GEMINI_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...

# Ollama (local, no API key needed)
PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434   # default
OLLAMA_MODEL=llama3.2                   # default fallback
OLLAMA_AGENT_MODEL=...                  # override agent model
OLLAMA_CODEGEN_MODEL=...                # override code-gen model

# Web UI
CHAINLIT_PASSWORD=ironclaw              # default
CHAINLIT_AUTH_SECRET=...
```

Provider auto-detection order (when `PROVIDER` is not set): `GEMINI_API_KEY` → `ANTHROPIC_API_KEY` → `OPENAI_API_KEY`.

## Providers

| Provider | Model | Set |
|----------|-------|-----|
| Gemini | gemini-2.5-flash | `GEMINI_API_KEY` |
| Anthropic | claude-3-5-sonnet-latest | `ANTHROPIC_API_KEY` |
| OpenAI | gpt-4o | `OPENAI_API_KEY` |
| Ollama | configurable | `PROVIDER=ollama` |

## Running

```bash
# CLI — default session
python3 src/main.py

# CLI — named session (persists conversation history)
python3 src/main.py --session my-session

# Web UI
chainlit run src/web_ui.py
```

The web UI is password-protected (`CHAINLIT_PASSWORD`, default: `ironclaw`).

## Architecture

**Two-phase execution model:**

- **Phase 1 (Plan):** The agent calls `run_system_task(task)`, which sends the task to the LLM and returns a `CodeExecutionRequest` — a structured list of code blocks with reasoning. No code runs at this stage.
- **Phase 2 (Execute):** After user approval, `confirm_execution()` passes those blocks to Open Interpreter, which runs them inside the Docker container via `DockerPython` / `DockerShell` language drivers.

Open Interpreter is used purely as an execution engine (`auto_run=True`, `offline=True`). Its own HITL loop is disabled — approval is enforced by the Pydantic AI layer.

**Sandbox:** A persistent Docker container (`ironclaw-agent` image) is managed by `SandboxManager`. Workspace files are mounted at `/workspace` inside the container.

**Persistence:** Conversation history is stored per-session in a local SQLite database via async SQLAlchemy. Sessions reload automatically on restart.

## Testing

```bash
pytest tests/
pytest tests/test_hitl.py
pytest tests/test_hitl.py::test_name -v
```
