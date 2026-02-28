# Roadmap: IronClaw Agent System

## Phases

- [x] **Phase 1: Foundation & Secure Execution** - Establish safe, sandboxed core engine with Pydantic AI and Open Interpreter. (completed 2026-02-24)
- [x] **Phase 2: Persistence & History** - Implement SQLAlchemy/SQLite persistence for sessions and conversations. (completed 2026-02-24)
- [x] **Phase 3: Web Dashboard & Security** - Build the primary Chainlit interface with password authentication. (completed 2026-02-24)
- [x] **Phase 4: Workspace & File Management** - Add file upload/download and UI-based file management capabilities. (completed 2026-02-24)
- [x] **Phase 5: Local Model Support via Ollama** - Allow running IronClaw with a locally-hosted Ollama model. (in progress) (completed 2026-02-28)
- [ ] **Phase 6: Phase 4 Workspace Verification** - Formally verify Phase 4 workspace features via UAT and create VERIFICATION.md. (gap closure)
- [ ] **Phase 7: Ollama CLI Streaming Fix** - Enable progressive token streaming in CLI mode and clean up hardcoded model string. (gap closure)

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
| 5. Local Model Support via Ollama | 4/4 | Complete   | 2026-02-28 |
| 6. Phase 4 Workspace Verification | 1/1 | Complete | 2026-02-28 |
| 7. Ollama CLI Streaming Fix | 0/1 | Not started | - |


### Phase 5: Local model support via Ollama

**Goal:** Allow users to run IronClaw with a locally-hosted Ollama model instead of cloud APIs.
**Requirements**: ENG-05
**Depends on:** Phase 4
**Plans:** 4/4 plans complete

Plans:
- [x] 05-01-PLAN.md — Provider config module (ProviderConfig, health check, model resolution)
- [x] 05-02-PLAN.md — Agent core integration (wire ProviderConfig into core.py and sandbox.py)
- [x] 05-03-PLAN.md — Startup integration (provider_banner, health check display, error handling in main.py/web_ui.py)
- [x] 05-04-PLAN.md — Gap closure: wire on_output streaming callback into run_system_task; update ENG-05 traceability

### Phase 6: Phase 4 Workspace Verification
**Goal:** Formally verify Phase 4 workspace file management features via UAT (5 tests) and create 04-VERIFICATION.md to close the formal verification gap.
**Depends on:** Phase 4
**Requirements**: ENG-03, WEB-03
**Gap Closure:** Closes ENG-03 and WEB-03 partial status from v1.0 audit (missing VERIFICATION.md, 0/5 UAT tests run)
**Success Criteria** (what must be TRUE):
  1. All 5 UAT tests in 04-UAT.md have results (pass/fail, not pending).
  2. 04-VERIFICATION.md exists with formal sign-off on ENG-03 and WEB-03.
**Plans**:
- [x] 06-01-PLAN.md — Run Phase 4 UAT and create VERIFICATION.md.

### Phase 7: Ollama CLI Streaming Fix
**Goal:** Enable progressive token streaming for Ollama in CLI mode and remove the hardcoded cloud model string from SandboxedTool.
**Depends on:** Phase 5
**Requirements**: ENG-05
**Gap Closure:** Closes GAP-01 (main.py missing deps=AgentDeps()) and GAP-02 (hardcoded interpreter.llm.model) from v1.0 audit
**Success Criteria** (what must be TRUE):
  1. Running `python3 src/main.py` with PROVIDER=ollama streams tokens progressively as they are generated.
  2. SandboxedTool.__init__ no longer hardcodes interpreter.llm.model to a cloud model string.
**Plans**:
- [ ] 07-01-PLAN.md — Pass AgentDeps to ironclaw_agent.run() in main.py; clean up hardcoded model string.
