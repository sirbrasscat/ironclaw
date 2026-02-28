# Phase 7: Ollama CLI Streaming Fix - Context

**Gathered:** 2026-02-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire `AgentDeps` into `main.py`'s CLI loop so Ollama tokens print progressively to the terminal during code generation. Remove the vestigial hardcoded LLM config (`interpreter.llm.model`, `interpreter.llm.api_key`) from `SandboxedTool.__init__` since OI is used only as an execution engine. Closes GAP-01 and GAP-02 from v1.0 audit.

</domain>

<decisions>
## Implementation Decisions

### Token display style
- Print tokens inline as they arrive: `print(token, end='', flush=True)`
- No prefix line or header before streaming begins — tokens appear directly
- Always print a trailing newline after streaming ends so the approval prompt starts on its own line
- Non-Ollama paths (Gemini, OpenAI, Anthropic) are unaffected — existing behavior unchanged

### Confirmation call streaming
- Wire `deps=AgentDeps()` to **both** `ironclaw_agent.run()` calls in `main.py` — the planning call and the confirmation call
- Reuse the same `on_output` callback for both calls (no special-casing for confirmation)

### Hardcoded model cleanup
- Remove `interpreter.llm.model = "gemini/gemini-2.5-flash"` entirely
- Remove `interpreter.llm.api_key = ...` entirely
- Remove the comment block that introduced those lines ("# Configure Open Interpreter's LLM...") entirely
- Add a single one-liner comment after the language setup explaining the intent: `# OI used as execution engine only — LLM config not needed`
- Change `interpreter.offline = False` to `interpreter.offline = True` (always True — since OI's LLM is never invoked, this is safe and avoids any accidental outbound LLM calls)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `AgentDeps` dataclass (`core.py:38`) — already has `on_output: Optional[Callable[[str], None]] = None`. Just needs to be instantiated with a callback and passed as `deps=` to `ironclaw_agent.run()`
- `core.py:56` — tool handlers already do `ctx.deps.on_output if ctx.deps else None`. No changes needed in core.py.
- `sandbox.py` — `run_system_task` already calls `on_output(token)` per chunk in the Ollama branch (`sandbox.py:127`). Already correct — just needs the callback to be non-None.

### Established Patterns
- Two `ironclaw_agent.run()` calls in `main.py:79` and `main.py:103` — both need `deps=AgentDeps(on_output=callback)`
- `get_provider_config()` already imported in `sandbox.py` — no new imports needed for the cleanup

### Integration Points
- `main.py` → `ironclaw_agent.run()` → tool layer → `sandbox.py` `run_system_task` → `on_output` callback
- The callback function lives in `main.py` and is passed down through `AgentDeps`

</code_context>

<specifics>
## Specific Ideas

- The on_output callback in main.py should be a simple lambda or local function: `lambda token: print(token, end='', flush=True)` — nothing more
- A `print()` (bare newline) after the streaming loop completes ensures clean separation before `"Approve execution? (y/n):"`

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 07-ollama-cli-streaming-fix*
*Context gathered: 2026-02-28*
