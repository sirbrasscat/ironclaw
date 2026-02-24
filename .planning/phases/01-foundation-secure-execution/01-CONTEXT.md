# Phase 1: Foundation & Secure Execution - Context

**Gathered:** 2026-02-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Establishing the core orchestrator (Pydantic AI + Open Interpreter) within a secure, Docker-sandboxed execution environment. This phase covers the foundational "safe-by-default" engine.

</domain>

<decisions>
## Implementation Decisions

### Core Engine & Orchestration
- **Decision:** Use **Pydantic AI** as the primary orchestrator for its type-safety and structured output capabilities.
- **Decision:** Use **Open Interpreter's Computer API** for low-level system interaction.
- **Decision:** Implement a modular "Bridge-Agnostic" protocol to allow future interface expansions.

### Security & Sandboxing
- **Decision:** **Mandatory Docker Sandboxing** from day one. All agent-generated code must run inside a container.
- **Decision:** Use a **Debian-based Docker image** for the agent workspace to ensure all common build tools and utilities are available.

### Human-in-the-loop (HITL)
- **Decision:** Prompt for user approval on all shell commands and Python execution initially.
- **Decision:** Specific destructive commands (rm, chmod, etc.) will have enhanced warning prompts.

### Claude's Discretion
- Selection of specific Docker image versions.
- Internal error handling and retry logic for the Pydantic AI agent loop.

</decisions>

<specifics>
## Specific Ideas
- The system should be "safe-by-default" - if the sandbox is not detected or fails to initialize, the agent must refuse to execute code.
</specifics>

<deferred>
## Deferred Ideas
- Cross-platform session sync (Phase 4).
- Persistent long-term memory via Vector DB (Phase 4).
</deferred>

---

*Phase: 01-foundation-secure-execution*
*Context gathered: 2026-02-23*
