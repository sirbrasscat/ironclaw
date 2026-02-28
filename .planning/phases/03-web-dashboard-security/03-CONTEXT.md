# Phase 03: Web Dashboard & Security

## Goal
Build the primary Chainlit interface with password authentication.

## Success Criteria
1. User is prompted for a password before accessing the web interface.
2. User can chat with the agent via the web UI and see real-time streaming of code execution blocks.
3. System and interpreter logs are visible within the UI as the agent works.

## User Decisions
- Use Chainlit (from ROADMAP.md).
- Simple password-based authentication (SEC-02).
- Visibility of system and interpreter logs (WEB-02).

## Claude's Discretion
- Implementation of the Chainlit `on_chat_start` and `on_message` handlers.
- Choice of password storage (environment variable or database). Given SEC-02 says "simple password-based authentication", an env var `CHAINLIT_AUTH_SECRET` or similar might suffice, or a hardcoded password in a `.env` file. Chainlit has built-in password auth.
- How to stream logs: Use Chainlit's `Step` or `Message` to show internal tool-calling progress.
