# Phase 7: Ollama CLI Streaming Fix - Research

**Researched:** 2026-02-28
**Domain:** Pydantic AI agent dependency injection; Open Interpreter LLM config cleanup
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Token display style**
- Print tokens inline as they arrive: `print(token, end='', flush=True)`
- No prefix line or header before streaming begins — tokens appear directly
- Always print a trailing newline after streaming ends so the approval prompt starts on its own line
- Non-Ollama paths (Gemini, OpenAI, Anthropic) are unaffected — existing behavior unchanged

**Confirmation call streaming**
- Wire `deps=AgentDeps()` to BOTH `ironclaw_agent.run()` calls in `main.py` — the planning call and the confirmation call
- Reuse the same `on_output` callback for both calls (no special-casing for confirmation)

**Hardcoded model cleanup**
- Remove `interpreter.llm.model = "gemini/gemini-2.5-flash"` entirely
- Remove `interpreter.llm.api_key = ...` entirely
- Remove the comment block that introduced those lines ("# Configure Open Interpreter's LLM...") entirely
- Add a single one-liner comment after the language setup explaining the intent: `# OI used as execution engine only — LLM config not needed`
- Change `interpreter.offline = False` to `interpreter.offline = True` (always True — since OI's LLM is never invoked, this is safe and avoids any accidental outbound LLM calls)

### Claude's Discretion

None specified — all implementation choices are locked.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ENG-05 | Local model support (Ollama/LocalAI integration) for 100% private execution. | Phase 5 implemented the Ollama provider, code-gen streaming, and agent integration. Phase 7 closes the final gap: CLI mode does not pass `AgentDeps(on_output=...)` so tokens are silently dropped. Wiring the callback and cleaning up OI's hardcoded LLM config completes the Ollama story. |
</phase_requirements>

---

## Summary

Phase 7 is a minimal, surgical change to two files. The Ollama streaming infrastructure was fully implemented in Phase 5 — the token accumulation loop in `run_system_task` (sandbox.py:124-128) already calls `on_output(token)` per chunk. The gap is that `main.py` never constructs an `AgentDeps` with a callback and never passes `deps=` to either `ironclaw_agent.run()` call, so `ctx.deps` is always `None` in the tool layer, and `on_output` is therefore always `None`, silently discarding all streaming tokens.

The second change is a dead-code cleanup: `SandboxedTool.__init__` configures `interpreter.llm.model` and `interpreter.llm.api_key` even though Open Interpreter is used purely as an execution engine (its own LLM is never invoked). Setting `interpreter.offline = True` and removing those two lines eliminates the risk of an accidental outbound LLM call through OI if the plumbing ever changes.

No new libraries, no new files, no schema changes. The entire implementation is two small edits: one in `src/main.py` and one in `src/agent/tools/sandbox.py`.

**Primary recommendation:** Define a module-level `_on_output` lambda in `main.py`, construct `AgentDeps(on_output=_on_output)` once, pass it as `deps=` to both `ironclaw_agent.run()` calls, then strip the three dead OI-LLM lines from `SandboxedTool.__init__`.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic-ai | installed (project) | Agent orchestration + dep injection via `RunContext[AgentDeps]` | Already the agent framework; `deps=` parameter is its standard DI mechanism |
| pydantic | installed (project) | `AgentDeps` dataclass validation | Already used for all models in this project |

### Supporting

None required — all dependencies already present.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `deps=AgentDeps(on_output=callback)` | Thread-local or global callback | Global state would conflict with any future concurrency; `deps=` is the idiomatic pydantic-ai injection path already wired in `core.py` |

---

## Architecture Patterns

### Existing Data Flow (Already Correct Down to Tool Layer)

```
main.py
  └─ ironclaw_agent.run(user_input, deps=???)   ← GAP: no deps passed
        └─ core.py: run_system_task tool
              on_output = ctx.deps.on_output if ctx.deps else None   ← already correct
                  └─ sandbox.py: run_system_task()
                        for chunk in stream:
                            token = chunk.get("response", "")
                            if on_output:          ← on_output is None → tokens dropped
                                on_output(token)
```

After fix:

```
main.py
  _callback = lambda token: print(token, end='', flush=True)
  _deps = AgentDeps(on_output=_callback)
  └─ ironclaw_agent.run(user_input, deps=_deps)  ← both calls
        └─ core.py: run_system_task tool
              on_output = ctx.deps.on_output      ← now non-None for Ollama
                  └─ sandbox.py: run_system_task()
                        on_output(token)          ← printed inline
  print()   ← trailing newline after run completes
```

### Pattern 1: Pydantic AI `deps=` Injection

**What:** Pass a `deps` dataclass instance directly to `agent.run()`. The agent thread receives it via `ctx.deps` in every `@tool` and `@tool_plain` handler.

**When to use:** Any time tool handlers need ambient context that isn't part of the user message (callbacks, config, DB handles).

**Example (from core.py — already implemented):**

```python
# core.py lines 51-57 — already correct, no changes needed
@ironclaw_agent.tool
def run_system_task(ctx: RunContext[AgentDeps], task: str) -> Union[CodeExecutionRequest, str]:
    on_output = ctx.deps.on_output if ctx.deps else None
    return _run_system_task(task, on_output=on_output)
```

**Fix needed in main.py:**

```python
# Define callback once
_callback = lambda token: print(token, end='', flush=True)
_deps = AgentDeps(on_output=_callback)

# Planning call (line 79 area)
result = await ironclaw_agent.run(
    user_input,
    message_history=history,
    output_type=CodeExecutionRequest | str,
    deps=_deps,                          # ADD THIS
)
# Trailing newline after streaming (Ollama only, but harmless for others)
print()

# Confirmation call (line 103 area)
confirm_result = await ironclaw_agent.run(
    "Confirm the execution.",
    message_history=history,
    output_type=str,
    deps=_deps,                          # ADD THIS
)
```

### Pattern 2: OI Offline Mode When Not Using OI LLM

**What:** `interpreter.offline = True` prevents OI from attempting outbound LLM calls. Since OI is used only as an execution engine (`interpreter.computer.run()`), its LLM config is irrelevant.

**Fix needed in sandbox.py `SandboxedTool.__init__`:**

```python
# REMOVE these 3 lines:
interpreter.llm.model = "gemini/gemini-2.5-flash"
interpreter.llm.api_key = os.environ.get("GEMINI_API_KEY")
# (and the comment block above them: "# Configure Open Interpreter's LLM...")

# ADD this comment after language setup:
# OI used as execution engine only — LLM config not needed

# CHANGE:
interpreter.offline = False
# TO:
interpreter.offline = True
```

### Anti-Patterns to Avoid

- **Creating the callback inside the loop:** Define `_callback` and `_deps` once before the `while True:` loop, not inside it — avoids recreating objects on every iteration.
- **Conditionally passing deps only for Ollama:** The CONTEXT.md decision is to pass `deps=` unconditionally to both calls. Cloud providers ignore `on_output` naturally (the Gemini branch in `run_system_task` never calls it). No provider-conditional logic needed.
- **Adding a trailing newline only for Ollama:** A bare `print()` after the planning call is harmless for cloud providers (just adds one blank line). Simpler to add it unconditionally rather than checking provider.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Streaming token delivery to terminal | Custom async generator or queue | `print(token, end='', flush=True)` in the `on_output` callback | The callback is already called synchronously per token inside the sync streaming loop in `run_system_task`; no async plumbing needed |
| Dep injection across agent calls | Thread locals, globals | `deps=AgentDeps(...)` on `agent.run()` | Pydantic-AI's native DI — already wired in `core.py` |

**Key insight:** The streaming infrastructure is already complete. This phase is purely about connecting the existing wire (`on_output` callback) at the call site (`main.py`).

---

## Common Pitfalls

### Pitfall 1: Forgetting the Trailing Newline

**What goes wrong:** The streaming loop ends mid-line. The next `print()` from the approval prompt (`"Approve execution? (y/n):"`) appears on the same line as the last token.

**Why it happens:** `print(token, end='', flush=True)` suppresses newlines intentionally so tokens stream inline.

**How to avoid:** Add a bare `print()` immediately after the `ironclaw_agent.run()` planning call returns, before the approval prompt.

**Warning signs:** The approval prompt appears run-on with the last streamed token.

### Pitfall 2: Passing `deps=None` or Omitting `deps=`

**What goes wrong:** `ctx.deps` is `None` in `core.py` tool handlers. The `if ctx.deps else None` guard silently swallows the callback. No error, no streaming.

**Why it happens:** `ironclaw_agent.run()` accepts `deps` as an optional keyword argument — omitting it is silent.

**How to avoid:** Pass `deps=AgentDeps(on_output=callback)` explicitly to both `.run()` calls.

**Warning signs:** Running with `PROVIDER=ollama` shows no progressive output during code generation.

### Pitfall 3: Removing `interpreter.auto_run = True` or `interpreter.safe_mode = False`

**What goes wrong:** OI's internal HITL loop activates, blocking execution or prompting the user from within OI's own loop.

**Why it happens:** The cleanup of `interpreter.llm.*` lines is nearby — easy to accidentally also remove `auto_run` or `safe_mode`.

**How to avoid:** Only remove the three LLM-related lines (model, api_key, comment block). Leave `auto_run = True`, `safe_mode = False`, and flip `offline = False` to `offline = True`.

**Warning signs:** Execution hangs waiting for OI's internal approval, or raises an error about safe mode.

### Pitfall 4: Applying the Fix Only to the Planning Call

**What goes wrong:** The confirmation call (`"Confirm the execution."`) also invokes tools (specifically `confirm_execution`), which uses the same `on_output` callback path for execution output. Without `deps=`, the Docker execution output also fails to stream.

**Why it happens:** The confirmation flow is a second separate `agent.run()` call — easy to patch only the first one.

**How to avoid:** CONTEXT.md is explicit: wire `deps=AgentDeps(on_output=callback)` to BOTH calls.

---

## Code Examples

Verified patterns from the actual codebase:

### Current State — main.py Planning Call (lines 79-83)

```python
# src/main.py — BEFORE (GAP: no deps=)
result = await ironclaw_agent.run(
    user_input,
    message_history=history,
    output_type=CodeExecutionRequest | str
)
```

### Target State — main.py Both Calls

```python
# src/main.py — AFTER
# Define once before the while loop
_callback = lambda token: print(token, end='', flush=True)
_deps = AgentDeps(on_output=_callback)

# Planning call
result = await ironclaw_agent.run(
    user_input,
    message_history=history,
    output_type=CodeExecutionRequest | str,
    deps=_deps,
)
print()  # trailing newline after streaming

# ... approval logic ...

# Confirmation call
confirm_result = await ironclaw_agent.run(
    "Confirm the execution.",
    message_history=history,
    output_type=str,
    deps=_deps,
)
```

### Current State — sandbox.py SandboxedTool.__init__ (lines 52-61)

```python
# src/agent/tools/sandbox.py — BEFORE (dead OI LLM config)
interpreter.computer.languages = [BoundDockerPython, BoundDockerShell]

# Configure Open Interpreter's LLM to use Gemini via LiteLLM
interpreter.llm.model = "gemini/gemini-2.5-flash"
interpreter.llm.api_key = os.environ.get("GEMINI_API_KEY")

# Configure interpreter behavior
interpreter.auto_run = True
interpreter.offline = False
interpreter.safe_mode = False
```

### Target State — sandbox.py SandboxedTool.__init__

```python
# src/agent/tools/sandbox.py — AFTER (cleaned up)
interpreter.computer.languages = [BoundDockerPython, BoundDockerShell]
# OI used as execution engine only — LLM config not needed

# Configure interpreter behavior
interpreter.auto_run = True
interpreter.offline = True
interpreter.safe_mode = False
```

### Import Required in main.py

```python
# Already imported — verify AgentDeps is in the import from core
from src.agent.core import ironclaw_agent, CodeExecutionRequest
```

`AgentDeps` is defined in `core.py` — it must be added to the import line:

```python
from src.agent.core import ironclaw_agent, CodeExecutionRequest, AgentDeps
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pass no `deps=` to `agent.run()` | Pass `deps=AgentDeps(on_output=callback)` | Phase 7 | Enables progressive token streaming in CLI |
| `interpreter.offline = False` with hardcoded LLM config | `interpreter.offline = True`, no LLM config | Phase 7 | Prevents accidental OI-initiated LLM calls |

---

## Open Questions

1. **Does `AgentDeps` need to be imported in main.py?**
   - What we know: `AgentDeps` is defined in `core.py` line 38. Current `main.py` imports `ironclaw_agent` and `CodeExecutionRequest` from `core.py` but NOT `AgentDeps`.
   - What's unclear: Nothing — this is straightforward. `AgentDeps` must be added to the `from src.agent.core import ...` line.
   - Recommendation: Add `AgentDeps` to the existing import. No new import statement needed.

2. **Should the trailing `print()` be placed inside or outside the `isinstance(response, CodeExecutionRequest)` check?**
   - What we know: The streaming happens during `ironclaw_agent.run()`, before we inspect the response type. The trailing newline should follow the run call, not the response inspection.
   - Recommendation: Place the bare `print()` immediately after the planning `ironclaw_agent.run()` call returns, before the `isinstance` check.

---

## Sources

### Primary (HIGH confidence)

- Direct source code read: `/home/brassy/github/ironclaw/src/main.py` — confirmed both `ironclaw_agent.run()` calls at lines 79 and 103 lack `deps=`
- Direct source code read: `/home/brassy/github/ironclaw/src/agent/tools/sandbox.py` — confirmed hardcoded `interpreter.llm.model` at line 53, `interpreter.llm.api_key` at line 54, `interpreter.offline = False` at line 61
- Direct source code read: `/home/brassy/github/ironclaw/src/agent/core.py` — confirmed `AgentDeps` dataclass at line 38, tool handlers already correctly guard `ctx.deps` at lines 56 and 64
- CONTEXT.md: All implementation decisions locked by user discussion

### Secondary (MEDIUM confidence)

None needed — implementation is fully specified by locked decisions and confirmed by source inspection.

### Tertiary (LOW confidence)

None.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new libraries; all existing code read directly
- Architecture: HIGH — exact line numbers confirmed from source; data flow traced end-to-end
- Pitfalls: HIGH — derived from reading actual code paths and CONTEXT.md decisions

**Research date:** 2026-02-28
**Valid until:** 2026-03-30 (stable; no external dependencies changing)
