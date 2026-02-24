# Roadmap: IronClaw Agent System

## Phases

- [ ] **Phase 1: Foundation & Secure Execution** - Establish safe, sandboxed core engine with Pydantic AI and Open Interpreter.
- [ ] **Phase 2: Persistence & History** - Implement SQLAlchemy/SQLite persistence for sessions and conversations.
- [ ] **Phase 3: Web Dashboard & Security** - Build the primary Chainlit interface with password authentication.
- [ ] **Phase 4: Workspace & File Management** - Add file upload/download and UI-based file management capabilities.
- [ ] **Phase 5: Telegram Bridge** - Implement remote access via Telegram with message buffering.

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
- [ ] 01-01-PLAN.md — Establish Docker sandbox and language bridge.
- [ ] 01-02-PLAN.md — Pydantic AI Agent integration and HITL approval.

### Phase 2: Persistence & History
**Goal**: Users can revisit past interactions and maintain session state across restarts.
**Depends on**: Phase 1
**Requirements**: SEC-03
**Success Criteria** (what must be TRUE):
  1. User sees their conversation history automatically reloaded upon starting a new session.
  2. Session metadata and chat logs are stored in a local SQLite database using SQLAlchemy.
**Plans**: TBD

### Phase 3: Web Dashboard & Security
**Goal**: Users have a secure, interactive dashboard for primary control and real-time feedback.
**Depends on**: Phase 2
**Requirements**: WEB-01, WEB-02, SEC-02
**Success Criteria** (what must be TRUE):
  1. User is prompted for a password before accessing the web interface.
  2. User can chat with the agent via the web UI and see real-time streaming of code execution blocks.
  3. System and interpreter logs are visible within the UI as the agent works.
**Plans**: TBD

### Phase 4: Workspace & File Management
**Goal**: Users can share, manage, and download files within the agent's workspace.
**Depends on**: Phase 3
**Requirements**: ENG-03, WEB-03
**Success Criteria** (what must be TRUE):
  1. User can upload a file via the UI and the agent can immediately interact with it.
  2. User can view a file list in the UI showing the current contents of the agent's workspace.
  3. User can download any files created or modified by the agent directly from the UI.
**Plans**: TBD

### Phase 5: Telegram Bridge
**Goal**: Users can control the agent remotely via Telegram with a smooth experience.
**Depends on**: Phase 2
**Requirements**: MSG-01, MSG-02
**Success Criteria** (what must be TRUE):
  1. User can initiate a chat and receive responses from the agent via a Telegram bot.
  2. Long or verbose outputs are automatically batched or edited to prevent API rate-limiting issues.
**Plans**: TBD

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Secure Execution | 0/2 | Not started | - |
| 2. Persistence & History | 0/0 | Not started | - |
| 3. Web Dashboard & Security | 0/0 | Not started | - |
| 4. Workspace & File Management | 0/0 | Not started | - |
| 5. Telegram Bridge | 0/0 | Not started | - |
