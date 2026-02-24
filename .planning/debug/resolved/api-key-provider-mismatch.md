---
status: investigating
trigger: "Investigate issue: api-key-provider-mismatch"
created: 2024-12-16T12:00:00Z
updated: 2024-12-16T12:00:00Z
---

## Current Focus

hypothesis: ModuleNotFoundError is caused by incorrect PYTHONPATH or execution method.
test: Try running with python -m src.main from root or setting PYTHONPATH.
expecting: main.py to start (though it might fail later due to API key issues).
next_action: Verify PYTHONPATH and execution method.

## Symptoms

expected: User should be able to provide a prompt and have the agent reason using the Gemini API key.
actual: Immediate ModuleNotFoundError: No module named 'src' followed by concerns about API key mismatch.
errors: ironclaw master  ? ✗ ./venv/bin/python3 src/main.py
Traceback (most recent call last):
  File "/home/brassy/github/ironclaw/src/main.py", line 4, in <module>
    from src.agent.core import ironclaw_agent, CodeExecutionRequest
ModuleNotFoundError: No module named 'src'
reproduction: ./venv/bin/python3 src/main.py
started: Started after implementing Phase 1 and providing the API key.

## Eliminated

## Evidence

- timestamp: 2024-12-16T12:05:00Z
  checked: PYTHONPATH and execution method.
  found: Running `./venv/bin/python3 src/main.py` from the root directory causes `ModuleNotFoundError: No module named 'src'` because `src/` is added to `sys.path`, not the parent of `src/`. Running with `./venv/bin/python3 -m src.main` resolves this but reveals an API key issue.
  implication: The script should be executed as a module or PYTHONPATH must be set.

- timestamp: 2024-12-16T12:10:00Z
  checked: `src/main.py` import order.
  found: `src/main.py` imports `src.agent.core` before calling `load_dotenv()`. Since `src.agent.core` instantiates an `Agent` with a default model, it may trigger API key validation at import time.
  implication: `load_dotenv()` must be called before importing modules that rely on environment variables.

- timestamp: 2024-12-16T12:12:00Z
  checked: Default model in `src/agent/core.py`.
  found: It uses `'openai:gpt-4o'` as a default, but only `GEMINI_API_KEY` is present.
  implication: The default model should probably be more flexible or the initialization should be deferred.

## Resolution

root_cause:
fix:
verification:
files_changed: []
