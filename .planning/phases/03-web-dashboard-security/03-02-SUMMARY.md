---
phase: 03
plan: 02
subsystem: web_ui
tags: [streaming, chainlit, ux]
key-files: [src/web_ui.py, src/agent/core.py, src/agent/tools/sandbox.py]
---

# 03-02: Real-time Streaming of Reasoning and Execution Summary

Implemented real-time streaming for both agent reasoning/tool calls and sandboxed code execution output in the web dashboard.

## One-liner
Enhanced the web UI with asynchronous streaming support to provide immediate feedback during agent thinking and live execution logs during sandbox operations.

## Key Changes
- **Agent Core**: Added `AgentDeps` with `on_output` callback and updated `ironclaw_agent` to support streaming dependencies.
- **Sandbox Tool**: Updated `confirm_execution` to accept and use the `on_output` callback, streaming console chunks from the interpreter to the caller.
- **Web UI**: Refactored `on_message` and `handle_code_approval` to use `ironclaw_agent.run_stream`.
- **Live Logs**: Integrated `cl.Step` in Chainlit to display real-time output from the Docker sandbox during code execution.

## Verification Results
- **Streaming Logic**: Verified that `src/web_ui.py` uses `run_stream` and iterates over tokens.
- **Callback Integration**: Verified that `confirm_execution` tool correctly retrieves `on_output` from `RunContext` and passes it to the sandbox runner.
- **Code Validity**: Verified `src/web_ui.py` imports and basic structure via `python src/web_ui.py`.

## Deviations
None - the implementation followed the plan to enable full transparency of the agent's actions.

## Self-Check: PASSED
- [x] `src/agent/core.py` updated with `AgentDeps`.
- [x] `src/agent/tools/sandbox.py` streams output chunks.
- [x] `src/web_ui.py` implements streaming for both reasoning and execution.
- [x] All changes committed.
