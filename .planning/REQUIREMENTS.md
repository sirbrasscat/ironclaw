# Requirements: IronClaw Agent System

## v1 Requirements (MVP)

### Core Engine (ENG)
- [ ] **ENG-01**: Integrate Pydantic AI with Open Interpreter for core orchestration and agent lifecycle.
- [ ] **ENG-02**: Execute shell commands and Python code via the agent with real-time output capture.
- [ ] **ENG-03**: Support workspace file management (upload/download/read/write) for the agent.

### Web Dashboard (WEB)
- [ ] **WEB-01**: Implement a Chainlit-based web interface for primary interactive chat and control.
- [ ] **WEB-02**: Stream real-time execution logs and code blocks to the Web UI.
- [ ] **WEB-03**: Provide a UI-based file manager for interacting with the agent's workspace.

### Messaging Bridges (MSG)
- [ ] **MSG-01**: Implement a Telegram bridge using Aiogram for remote agent interaction.
- [ ] **MSG-02**: Implement message buffering and batching for Telegram to prevent API rate-limiting during verbose output.

### Security & Persistence (SEC)
- [ ] **SEC-01**: Implement mandatory Human-in-the-loop (HITL) approval for destructive or high-risk system commands.
- [ ] **SEC-02**: Secure the Web UI with simple password-based authentication.
- [ ] **SEC-03**: Use SQLAlchemy and SQLite to persist conversation history and basic session state.
- [ ] **SEC-04**: Implement basic Docker sandboxing for the agent execution environment to protect the host system.

## v2 Requirements (Deferred)

- **MSG-03**: Implement a Discord bridge using Discord.py.
- **MSG-04**: Support proactive messaging (agent-initiated notifications for task completion or system alerts).
- **SEC-05**: Cross-platform session synchronization (switching between Web and Telegram mid-task).
- **ENG-04**: Long-term memory (Vector DB/RAG) for historical context across all sessions.
- **ENG-05**: Local model support (Ollama/LocalAI integration) for 100% private execution.

## Out of Scope

- **Public Multi-tenancy**: The system is designed for a single user or a small, trusted team.
- **Native Mobile Apps**: Use Telegram/Discord bridges as the mobile interface.
- **Visual Workflow Builder**: Focus is on code-first and natural language control.

## Traceability

| Req ID | Phase | Plan | Status |
|--------|-------|------|--------|
| ENG-01 | Phase 1 | — | Pending |
| ENG-02 | Phase 1 | — | Pending |
| ENG-03 | Phase 4 | — | Pending |
| WEB-01 | Phase 3 | — | Pending |
| WEB-02 | Phase 3 | — | Pending |
| WEB-03 | Phase 4 | — | Pending |
| MSG-01 | Phase 5 | — | Pending |
| MSG-02 | Phase 5 | — | Pending |
| SEC-01 | Phase 1 | — | Pending |
| SEC-02 | Phase 3 | — | Pending |
| SEC-03 | Phase 2 | — | Pending |
| SEC-04 | Phase 1 | — | Pending |

---
*Last updated: 2026-02-23*
