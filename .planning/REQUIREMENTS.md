# Requirements: IronClaw Agent System

## v1 Requirements (MVP)

### Core Engine (ENG)
- [x] **ENG-01**: Integrate Pydantic AI with Open Interpreter for core orchestration and agent lifecycle.
- [x] **ENG-02**: Execute shell commands and Python code via the agent with real-time output capture.
- [ ] **ENG-03**: Support workspace file management (upload/download/read/write) for the agent.

### Web Dashboard (WEB)
- [x] **WEB-01**: Implement a Chainlit-based web interface for primary interactive chat and control.
- [x] **WEB-02**: Stream real-time execution logs and code blocks to the Web UI.
- [ ] **WEB-03**: Provide a UI-based file manager for interacting with the agent's workspace.

### Security & Persistence (SEC)
- [x] **SEC-01**: Implement mandatory Human-in-the-loop (HITL) approval for destructive or high-risk system commands.
- [x] **SEC-02**: Secure the Web UI with simple password-based authentication.
- [x] **SEC-03**: Use SQLAlchemy and SQLite to persist conversation history and basic session state.
- [x] **SEC-04**: Implement basic Docker sandboxing for the agent execution environment to protect the host system.

## v2 Requirements (Deferred)

- **MSG-01**: Implement a Telegram bridge for remote agent interaction.
- **MSG-02**: Implement message buffering and batching for Telegram to prevent API rate-limiting during verbose output.
- **MSG-03**: Implement a Discord bridge using Discord.py.
- **MSG-04**: Support proactive messaging (agent-initiated notifications for task completion or system alerts).
- **SEC-05**: Cross-platform session synchronization (switching between Web and Telegram mid-task).
- **ENG-04**: Long-term memory (Vector DB/RAG) for historical context across all sessions.
- **ENG-05**: Local model support (Ollama/LocalAI integration) for 100% private execution.

## Out of Scope

- **Public Multi-tenancy**: The system is designed for a single user or a small, trusted team.
- **Native Mobile Apps**: Use Telegram/Discord bridges as the mobile interface (now deferred).
- **Visual Workflow Builder**: Focus is on code-first and natural language control.

## Traceability

| Req ID | Phase | Plan | Status |
|--------|-------|------|--------|
| ENG-01 | Phase 1 | 01-02 | Complete |
| ENG-02 | Phase 1 | 01-01 | Complete |
| ENG-03 | Phase 6 | 06-01 | Pending |
| WEB-01 | Phase 3 | 03-01 | Complete |
| WEB-02 | Phase 3 | 03-02 | Complete |
| WEB-03 | Phase 6 | 06-01 | Pending |
| SEC-01 | Phase 1 | 01-02 | Complete |
| SEC-02 | Phase 3 | 03-01 | Complete |
| SEC-03 | Phase 2 | 02-01 | Complete |
| SEC-04 | Phase 1 | 01-01 | Complete |
| ENG-05 | Phase 5, 7 | 05-01, 05-02, 05-03, 07-01 | Pending |

---
*Last updated: 2026-02-28*
