---
phase: 02-persistence-history
plan: 02
subsystem: database
tags: [persistence, sqlite, sqlalchemy, pydantic-ai, cli, session-management]

requires:
  - phase: 02-01
    provides: database-persistence

provides:
  - cli-history-loading
  - session-continuity
  - cross-restart-context

affects: [web-ui, agent-core]

tech-stack:
  added: []
  patterns: [message-history-threading, session-based-persistence, new-messages-incremental-save]

key-files:
  created: []
  modified: [src/main.py, src/database/manager.py]

key-decisions:
  - "Using result.new_messages() for incremental save (not all_messages()) to avoid duplicates on every turn"
  - "Falling back to 'kind' field when 'role' absent in Pydantic AI ModelMessage dicts for correct message type tagging"
  - "History loaded from DB as dicts then validated through TypeAdapter[list[ModelMessage]] for type safety"

patterns-established:
  - "Incremental save pattern: save new_messages() after each turn, update local history from all_messages()"
  - "Confirmation flow persistence: save both planning and execution turn messages separately"

requirements-completed: [SEC-03]

duration: 1min
completed: "2026-02-28"
---

# Phase 02 Plan 02: CLI History Persistence Summary

**SQLite-backed cross-session context continuity in the CLI: history loads on startup, every turn (including tool calls and approvals) is incrementally saved via Pydantic AI's new_messages().**

## Performance

- **Duration:** ~1 min (code was previously written; verified and committed)
- **Started:** 2026-02-28T03:07:08Z
- **Completed:** 2026-02-28T03:08:26Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- CLI now initializes DatabaseManager on startup and calls `get_or_create_session(session_id)` before entering the interaction loop
- Previous messages are loaded and displayed as "Loaded X previous messages" count on resume
- All turns (user prompt, model response, tool call, tool output, confirmation) are saved using `result.new_messages()` to avoid duplicates
- Named session support via `--session <id>` CLI flag
- Pydantic AI `kind` field fallback added to `save_messages()` so all message types persist with correct role labels

## Task Commits

Each task was committed atomically:

1. **Task 1: Update src/main.py to manage history** - `06c8b5a` (feat)
2. **Task 2: Automatic session persistence and recovery** - `4086336` (fix)

**Plan metadata:** (final docs commit - TBD)

## Files Created/Modified
- `src/main.py` - Added DatabaseManager init, history loading, `message_history=history` threading, incremental save via `new_messages()`, `--session` argparse flag, `db.close()` on exit
- `src/database/manager.py` - Fixed `save_messages()` to fall back to `msg_data.get('kind', 'unknown')` when `role` key is absent (Pydantic AI uses `kind` not `role`)

## Decisions Made
- Used `result.new_messages()` instead of `result.all_messages()` for each incremental save to the DB. This avoids re-saving previously persisted messages and ensures idempotent appends.
- The history TypeAdapter (`TypeAdapter(list[ModelMessage])`) is created once per session and reused for both serialization (`dump_python`) and deserialization (`validate_python`), keeping the conversion efficient.
- Confirmation turn ("Confirm the execution.") messages are saved separately after the approval flow to ensure tool call + tool output messages are also persisted.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed Pydantic AI ModelMessage role extraction in save_messages**
- **Found during:** Task 2 (session persistence review)
- **Issue:** Pydantic AI `ModelMessage` serializes with a `kind` field (`request`/`response`) rather than `role`. The original `save_messages()` code only looked for `role`, so messages from agent runs were saved with role `unknown`.
- **Fix:** Changed `msg_data.get('role', 'unknown')` to `msg_data.get('role', msg_data.get('kind', 'unknown'))` so messages get correctly labeled as `request`/`response` in the DB.
- **Files modified:** `src/database/manager.py`
- **Verification:** `tests/test_persistence.py` passes (3/3); messages with `kind` field now persist correctly.
- **Committed in:** `4086336`

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug)
**Impact on plan:** Fix was necessary for correct message type labeling. No scope creep.

## Issues Encountered
None beyond the auto-fixed role/kind field issue.

## User Setup Required
None - no external service configuration required. The SQLite database (`ironclaw.db`) is created automatically on first run.

## Next Phase Readiness
- CLI persistence is complete. The web UI (Phase 3) already uses the same `DatabaseManager` API.
- Cross-session context continuity is now available to both the CLI and web UI layers.
- No blockers for subsequent phases.

## Self-Check: PASSED
- [x] `src/main.py` modified with history loading/saving
- [x] `src/database/manager.py` updated with kind-field fallback
- [x] `tests/test_persistence.py` passes (3/3 tests)
- [x] `python3 -c "from src.main import main; print('main loop loadable')"` succeeds

---
*Phase: 02-persistence-history*
*Completed: 2026-02-28*
