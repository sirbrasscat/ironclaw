# IronClaw Agent System

A Python-based, self-hosted AI agent system for system control and multi-platform chat.

## Vision

To create a powerful, self-hosted agent system that leverages `open-interpreter` for deep system control while providing accessible interfaces via web and messaging platforms.

## Core Value

Empowering users with a proactive, system-aware AI assistant that can be controlled from anywhere.

## Stack

- **Language:** Python 3.11+
- **Core Engine:** `open-interpreter`
- **Web UI:** `Chainlit`
- **Messaging:** `pyTelegramBotAPI` (Telegram), `discord.py` (Discord)

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Core Engine: Initialize Python environment and configure `open-interpreter`.
- [ ] System Control: Execute shell commands and manage files via the agent.
- [ ] Web Dashboard: Build a Chainlit interface for local control.
- [ ] Log Streaming: Stream interpreter logs and code execution to the UI.
- [ ] File Management: Add upload/download capabilities to the web UI.
- [ ] Telegram Bridge: Implement a Telegram bot interface.
- [ ] Discord Bridge: Implement a Discord bot interface.
- [ ] Proactive Messaging: Agent-initiated messaging via Telegram.
- [ ] Session Management: Handle separate or synced contexts across platforms.
- [ ] Authentication: Simple authentication for the Web UI.
- [ ] Security: Setup environment variables for API keys and optional Docker sandboxing.

### Out of Scope

- [ ] Advanced Multi-user: (Deferred) Complex multi-user permission systems beyond simple auth.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Open Interpreter | Best-in-class for system control and code execution | Decided |
| Chainlit | Fast development for Python-native interactive UIs | Decided |

---
*Last updated: 2026-02-23 after initialization*
