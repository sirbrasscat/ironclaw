# Deferred Items — Phase 05

## Pre-existing test failure (out of scope for 05-04)

**Discovered during:** 05-04 overall verification
**Test:** `tests/test_hitl.py::test_run_system_task_generates_request`
**Status:** Failing before 05-04 changes (confirmed by stash + retest)

**Root cause:** The test patches `genai.Client` (Gemini path) but does not mock the Ollama branch (`ollama_lib.generate`). When a live Ollama instance is running and PROVIDER=ollama is set in the environment, `SandboxedTool.run_system_task()` takes the Ollama branch, bypasses the mock, makes a real Ollama call, and returns 2 code blocks instead of 1.

**Introduced in:** 05-02 (when Ollama branch was added to `SandboxedTool.run_system_task`)
**Fix needed:** Add `@patch('src.agent.tools.sandbox.ollama_lib')` to the test, or patch `get_provider_config()` to force the Gemini branch during tests.
**Priority:** Medium — tests pass in environments without Ollama running.
