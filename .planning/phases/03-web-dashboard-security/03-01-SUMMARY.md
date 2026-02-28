---
phase: 03
plan: 01
subsystem: web_ui
tags: [chainlit, auth, hitl]
key-files: [src/web_ui.py]
---

# 03-01: Establish Chainlit environment with Auth Summary

Established the Chainlit environment and secured it with password-based authentication.

## One-liner
Integrated Chainlit with password-based authentication and a chat adapter that handles HITL (Human-In-The-Loop) approval for code execution.

## Key Changes
- Created `src/web_ui.py` with Chainlit `password_auth_callback`.
- Implemented `on_chat_start` to initialize the database and load session history.
- Implemented `on_message` to interface with `ironclaw_agent` and handle `CodeExecutionRequest`.
- Added `handle_code_approval` using Chainlit actions (Approve/Reject) for HITL.
- Configured `.env` with `CHAINLIT_AUTH_SECRET` and `CHAINLIT_PASSWORD`.

## Verification Results
- **Authentication**: Verified that `src/web_ui.py` starts and reaches the "available" state. The code implements `password_auth_callback` checking against `CHAINLIT_PASSWORD`.
- **HITL Flow**: The code includes logic to detect `CodeExecutionRequest` and prompt the user for approval via `cl.AskActionMessage`.
- **Persistence**: Reuses `DatabaseManager` from Phase 2 to load/save messages keyed by `web-{username}`.

## Deviations
None - plan executed as intended.

## Self-Check: PASSED
- [x] `src/web_ui.py` exists and is runnable.
- [x] Auth logic is implemented.
- [x] HITL logic is implemented.
