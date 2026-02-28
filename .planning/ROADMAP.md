# Roadmap: IronClaw Agent System

## Phases

- [x] **Phase 1: Foundation & Secure Execution** - Establish safe, sandboxed core engine with Pydantic AI and Open Interpreter. (completed 2026-02-24)
- [x] **Phase 2: Persistence & History** - Implement SQLAlchemy/SQLite persistence for sessions and conversations. (completed 2026-02-24)
- [x] **Phase 3: Web Dashboard & Security** - Build the primary Chainlit interface with password authentication. (completed 2026-02-24)
- [x] **Phase 4: Workspace & File Management** - Add file upload/download and UI-based file management capabilities. (completed 2026-02-24)
- [ ] **Phase 5: Local Model Support via Ollama** - Allow running IronClaw with a locally-hosted Ollama model. (in progress)

## Phase Details

### Phase 1: Foundation & Secure Execution
**Goal**: Users can safely interact with the OS through a sandboxed AI agent.
**Depends on**: Nothing
**Requirements**: ENG-01, ENG-02, SEC-01, SEC-04
**Success Criteria** (what must be TRUE):
  1. User receives a response from the agent after asking it to run a shell command or Python snippet.
  2. Any code execution is verified to run inside a Docker sandbox (protecting the host).
  3. Agent prompts the user for approval before executing destructive or high-risk commands.
  4. Agent utilizes Pydantic AI for reasoning/orchestration before calling Open Interpreter.
**Plans**:
- [x] 01-01-PLAN.md — Establish Docker sandbox and language bridge.
- [x] 01-02-PLAN.md — Pydantic AI Agent integration and HITL approval.
- [x] 01-03-PLAN.md — Fix HITL architecture (gap closure).

### Phase 2: Persistence & History
**Goal**: Users can revisit past interactions and maintain session state across restarts.
**Depends on**: Phase 1
**Requirements**: SEC-03
**Success Criteria** (what must be TRUE):
  1. User sees their conversation history automatically reloaded upon starting a new session.
  2. Session metadata and chat logs are stored in a local SQLite database using SQLAlchemy.
**Plans**:
- [x] 02-01-PLAN.md — Foundation Persistence Layer (SQLAlchemy + SQLite).
- [x] 02-02-PLAN.md — CLI Loop Integration for automatic history recovery.

### Phase 3: Web Dashboard & Security
**Goal**: Users have a secure, interactive dashboard for primary control and real-time feedback.
**Depends on**: Phase 2
**Requirements**: WEB-01, WEB-02, SEC-02
**Success Criteria** (what must be TRUE):
  1. User is prompted for a password before accessing the web interface.
  2. User can chat with the agent via the web UI and see real-time streaming of code execution blocks.
  3. System and interpreter logs are visible within the UI as the agent works.
**Plans**:
- [x] 03-01-PLAN.md — Establish Chainlit environment with Auth.
- [x] 03-02-PLAN.md — Real-time Streaming & Execution Feedback.

### Phase 4: Workspace & File Management
**Goal**: Users can share, manage, and download files within the agent's workspace.
**Depends on**: Phase 3
**Requirements**: ENG-03, WEB-03
**Success Criteria** (what must be TRUE):
  1. User can upload a file via the UI and the agent can immediately interact with it.
  2. User can view a file list in the UI showing the current contents of the agent's workspace.
  3. User can download any files created or modified by the agent directly from the UI.
**Plans**: 2 plans
- [x] 04-01-PLAN.md — Workspace File Management & bidirectional sync.
- [x] 04-02-PLAN.md — UI File Explorer & Downloads.

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Secure Execution | 3/3 | Complete    | 2026-02-24 |
| 2. Persistence & History | 2/2 | Complete   | 2026-02-28 |
| 3. Web Dashboard & Security | 2/2 | Complete    | 2026-02-24 |
| 4. Workspace & File Management | 2/2 | Complete    | 2026-02-24 |
| 5. Local Model Support via Ollama | 1/3 | In Progress | —          |


### Phase 5: Local model support via Ollama

**Goal:** Allow users to run IronClaw with a locally-hosted Ollama model instead of cloud APIs.
**Requirements**: ENG-05
**Depends on:** Phase 4
**Plans:** 3 plans

Plans:
- [x] 05-01-PLAN.md — Provider config module (ProviderConfig, health check, model resolution)
- [ ] 05-02-PLAN.md — Agent core integration (wire ProviderConfig into core.py model selection)
- [ ] 05-03-PLAN.md — Sandbox codegen integration (wire ProviderConfig into sandbox.py codegen)
