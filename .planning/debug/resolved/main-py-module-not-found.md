---
status: resolved
trigger: "Investigate issue: main-py-module-not-found. ModuleNotFoundError: No module named 'src' when running src/main.py."
created: 2025-02-17T10:00:00Z
updated: 2025-02-17T11:30:00Z
---

## Current Focus

hypothesis: CONFIRMED AND FIXED
test: Plain `./venv/bin/python3 src/main.py` — verified working.
expecting: n/a
next_action: archived

## Symptoms

expected: src/main.py should run and start the CLI bridge.
actual: ModuleNotFoundError: No module named 'src'
errors: Traceback (most recent call last): File "/home/brassy/github/ironclaw/src/main.py", line 4, in <module> from src.agent.core import ironclaw_agent, CodeExecutionRequest ModuleNotFoundError: No module named 'src'
reproduction: ./venv/bin/python3 src/main.py (and reportedly with PYTHONPATH=. as well)
started: Occurred immediately after completing Phase 1 implementation.

## Eliminated

- hypothesis: PYTHONPATH=. doesn't work either (something deeper is broken)
  evidence: Tested PYTHONPATH=. ./venv/bin/python3 src/main.py — works perfectly, banner printed, CLI started.
  timestamp: 2025-02-17T11:00:00Z

## Evidence

- timestamp: 2025-02-17T11:00:00Z
  checked: src/main.py imports
  found: `from src.agent.core import ironclaw_agent, CodeExecutionRequest` — uses absolute `src.` path
  implication: Requires project root (not src/) in sys.path

- timestamp: 2025-02-17T11:00:00Z
  checked: All src/ files for `from src.` imports
  found: src/main.py, src/agent/core.py, src/agent/tools/sandbox.py all use absolute `from src.X` imports
  implication: All files share the same dependency on project root being in sys.path

- timestamp: 2025-02-17T11:00:00Z
  checked: `PYTHONPATH=. ./venv/bin/python3 src/main.py`
  found: Works — CLI starts and shows banner
  implication: No code logic issues; purely a sys.path issue at invocation time

- timestamp: 2025-02-17T11:00:00Z
  checked: src/__init__.py presence
  found: Does NOT exist
  implication: Can't use `python3 -m src.main` without it; sys.path injection in main.py is cleanest fix

## Resolution

root_cause: When running `python3 src/main.py`, Python adds `src/` to sys.path (not the project root). All src/ files use absolute `from src.X` imports, which require the project root in sys.path. No sys.path manipulation existed to compensate.
fix: Added sys.path.insert(0, project_root) block at the top of src/main.py, computing project root as dirname(dirname(abspath(__file__))). This makes plain `python3 src/main.py` work without requiring PYTHONPATH to be set externally.
verification: `echo quit | ./venv/bin/python3 src/main.py` — CLI banner printed, exited cleanly. Also verified `PYTHONPATH=. ./venv/bin/python3 src/main.py` still works.
files_changed: [src/main.py]
