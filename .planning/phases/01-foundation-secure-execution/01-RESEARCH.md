<user_constraints>
## User Constraints (from CONTEXT.md)

### Implementation Decisions

#### Core Engine & Orchestration
- **Decision:** Use **Pydantic AI** as the primary orchestrator for its type-safety and structured output capabilities.
- **Decision:** Use **Open Interpreter's Computer API** for low-level system interaction.
- **Decision:** Implement a modular "Bridge-Agnostic" protocol to allow future interface expansions.

#### Security & Sandboxing
- **Decision:** **Mandatory Docker Sandboxing** from day one. All agent-generated code must run inside a container.
- **Decision:** Use a **Debian-based Docker image** for the agent workspace to ensure all common build tools and utilities are available.

#### Human-in-the-loop (HITL)
- **Decision:** Prompt for user approval on all shell commands and Python execution initially.
- **Decision:** Specific destructive commands (rm, chmod, etc.) will have enhanced warning prompts.

### Claude's Discretion
- Selection of specific Docker image versions.
- Internal error handling and retry logic for the Pydantic AI agent loop.

### Deferred Ideas (OUT OF SCOPE)
- Cross-platform session sync (Phase 4).
- Persistent long-term memory via Vector DB (Phase 4).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ENG-01 | Integrate Pydantic AI with Open Interpreter | Confirmed pattern: Wrap Open Interpreter as a Pydantic AI `tool`. |
| ENG-02 | Execute shell/Python code via agent | Validated: Use Open Interpreter's `computer.run` with a custom Docker-backed Language class. |
| SEC-01 | Mandatory HITL approval | Pattern identified: "Staged Execution" where tool returns a pending status requiring user confirmation. |
| SEC-04 | Basic Docker sandboxing | Solution: Use `docker-py` to manage a persistent Debian container and route interpreter commands via `docker exec`. |
</phase_requirements>

# Phase 1: Foundation & Secure Execution - Research

**Researched:** 2026-02-23
**Domain:** Core Agent Orchestration & Sandboxing
**Confidence:** HIGH

## Summary

Phase 1 establishes the "Brain" and "Hands" of IronClaw. The research confirms that **Pydantic AI** can effectively orchestrate **Open Interpreter**, but the default behavior of Open Interpreter (running locally) must be overridden to enforce the **Docker Sandboxing** constraint.

The critical architectural finding is the need for a **Custom Language Interface** within Open Interpreter. Instead of using the default local execution, we will define a `DockerLanguage` class that routes all Python and Shell commands to a persistent Docker container via the `docker-py` library. This ensures that even if the agent attempts risky operations, they are confined to the sandbox.

For Human-in-the-loop (HITL), we recommend a **"Staged Execution"** pattern. The agent's tool will not execute code immediately but will return a "Pending Approval" object. The Orchestrator will then pause and request user confirmation via the Bridge (CLI/Web). Only upon receiving a signed confirmation will the tool proceed to execution.

**Primary recommendation:** Build a `SandboxedInterpreter` class that wraps `Open Interpreter` and overrides `interpreter.computer.languages` with custom Docker-executing implementations.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pydantic-ai` | 0.0.18+ | Agent Orchestration | Native Pydantic integration, strong typing, newer streamlined API. |
| `open-interpreter` | 0.3.x+ | Code Execution | Industry standard for LLM code execution with self-healing capabilities. |
| `docker` (docker-py) | 7.x+ | Container Management | Official Python client for managing Docker lifecycles. |
| `sqlalchemy` | 2.0+ | Persistence | Modern async ORM for session/history tracking. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `aiosqlite` | Latest | Async DB Driver | Required for async SQLAlchemy with SQLite. |
| `pydantic-settings` | 2.x | Configuration | Type-safe environment variable management. |

**Installation:**
```bash
npm install (skip - python project)
pip install pydantic-ai open-interpreter docker sqlalchemy aiosqlite pydantic-settings
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── agent/
│   ├── core.py              # Pydantic AI Agent definition
│   ├── tools/
│   │   └── sandbox.py       # Open Interpreter wrapper tool
│   └── prompts.py           # System prompts
├── sandbox/
│   ├── manager.py           # Docker container lifecycle (start/stop)
│   └── languages.py         # Custom Open Interpreter Language classes
├── db/
│   ├── session.py           # SQLAlchemy setup
│   └── models.py            # User, Session, History models
└── main.py                  # Entry point
```

### Pattern 1: Docker-Backed Open Interpreter
**What:** Overriding Open Interpreter's default local execution with `docker exec`.
**When to use:** ALWAYS for this project.
**Example:**
```python
# Source: Adapted from Open Interpreter custom language docs
class DockerPython:
    name = "python"
    
    def __init__(self, container):
        self.container = container

    def run(self, code):
        # Naive example; real impl needs to handle state/streams
        exec_result = self.container.exec_run(
            cmd=["python3", "-c", code],
            workdir="/workspace"
        )
        yield {"type": "console", "format": "output", "content": exec_result.output.decode()}
```

### Pattern 2: Staged Execution (HITL)
**What:** Tools return a "Pending" state instead of executing immediately.
**When to use:** For any `SEC-01` sensitive operation (shell/python code).
**Example:**
```python
@tool
def execute_code(ctx: RunContext, code: str, confirm_token: str = None):
    if not confirm_token:
        # Stage the code
        token = generate_token()
        save_pending_action(ctx.session_id, token, code)
        return f"Code staged. Ask user to approve with token: {token}"
    
    # Verify and execute
    if verify_token(ctx.session_id, confirm_token, code):
        return run_in_sandbox(code)
    return "Invalid confirmation."
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| **Code Execution Loop** | Custom `subprocess.Popen` loop | **Open Interpreter** | Parsing output, handling errors, and maintaining context is incredibly hard to get right. |
| **Container API** | `subprocess.run(["docker", ...])` | **docker-py** | `docker-py` handles sockets, streams, and errors much more robustly than shell wrappers. |
| **Agent State** | Custom `dict` / `json` state | **Pydantic AI `RunContext`** | Built-in context injection is type-safe and testable. |

**Key insight:** Open Interpreter essentially "is" a robust REPL parser. Rebuilding it is a massive waste of time.

## Common Pitfalls

### Pitfall 1: Docker Volume Permissions
**What goes wrong:** The agent creates files in the mapped volume (workspace) as `root`, making them uneditable by the user on the host.
**Why it happens:** Docker containers run as root by default.
**How to avoid:** Set the Docker user to the host's UID/GID when starting the container.
**Warning signs:** `Permission denied` errors when opening agent-created files on the host.

### Pitfall 2: State Amnesia
**What goes wrong:** Variables defined in one Python block are lost in the next.
**Why it happens:** `docker exec` runs a *new* process each time. It does not persist memory.
**How to avoid:**
1.  **Preferred:** Use Open Interpreter's `subprocess` mode *inside* the container (requires running the interpreter *inside* or piping via `docker exec -i`).
2.  **Alternative:** Use a Jupyter Kernel inside the container (complex).
3.  **IronClaw Approach:** We will implement a persistent Python process inside Docker (using `docker exec -i` to pipe to a running `python -i` process) or accept that state is file-based only. **Research recommendation:** Start with file-based state for simplicity (write scripts, run them) or use Open Interpreter's native ability to connect to a remote kernel if available.

### Pitfall 3: The "Infinite Approval" Loop
**What goes wrong:** The agent asks for approval, user approves, agent gets confused and asks again.
**Why it happens:** Context window doesn't clearly show "User Approved X".
**How to avoid:** Inject a clear "System Message" into the chat history: `[SYSTEM] User approved execution of token XYZ`.

## Code Examples

### Initializing the Sandbox
```python
import docker

def get_or_create_sandbox(session_id: str):
    client = docker.from_env()
    container_name = f"ironclaw-sandbox-{session_id}"
    
    try:
        return client.containers.get(container_name)
    except docker.errors.NotFound:
        return client.containers.run(
            "python:3.11-bookworm",
            command="tail -f /dev/null", # Keep alive
            name=container_name,
            detach=True,
            volumes={f"/tmp/ironclaw/{session_id}": {'bind': '/workspace', 'mode': 'rw'}},
            working_dir="/workspace"
        )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Custom `subprocess` loops | **Pydantic AI + Tools** | 2024/2025 | Standardized agentic patterns, better type safety. |
| Running on Host | **Docker Containers** | 2023+ | Standard for AI Safety (Sandbox). |
| Hardcoded Prompts | **Structured Output (Pydantic)** | 2024 | Deterministic tool calling and parsing. |

## Open Questions

1. **Persistent Shell Session via `docker exec`**
   - What we know: `docker exec` is usually one-off.
   - What's unclear: Best way to keep a `python -i` session alive and pipe to it reliably from Python host.
   - Recommendation: Use `docker.APIClient().exec_create` + `exec_start` with socket attachments, or investigate `open-interpreter`'s built-in "server" mode running inside the container.

## Sources

### Primary (HIGH confidence)
- **Open Interpreter Docs** (Verified via search) - `interpreter.computer.languages` customization.
- **Pydantic AI Docs** (Verified via search) - Agent and Tool definitions.
- **Docker SDK for Python** (Official docs) - `exec_run` and container management.

### Secondary (MEDIUM confidence)
- **Web Search** - "Pydantic AI HITL patterns" (General consensus, no single official guide).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Core libraries are well-chosen.
- Architecture: HIGH - Bridge/Orchestrator pattern is solid.
- Pitfalls: MEDIUM - Docker permission issues are tricky but solvable.

**Research date:** 2026-02-23
**Valid until:** 30 days
