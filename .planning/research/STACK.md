# Technology Stack

**Project:** IronClaw Agent System
**Researched:** 2025-02-23
**Status:** Prescriptive Recommendation for Greenfield Development

## Recommended Stack

### Core Framework & Orchestration
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Python** | 3.11.x | Programming Language | Optimal balance of performance, modern `asyncio` features, and broad library support. Avoid 3.13 early on due to potential library binary compatibility issues. |
| **Pydantic AI** | 1.0.0+ | Agent Orchestration | The "FastAPI for Agents". Provides type-safe, structured outputs and native support for Model Context Protocol (MCP). Replaces bloated alternatives like LangChain. |
| **Open Interpreter**| 0.2.5+ | System Control | Best-in-class for code execution and "Computer Use". Its modular `Computer` API allows the agent to interact with the OS while maintaining a clean abstraction. |

### Interfaces (Multi-platform)
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Chainlit** | 2.0.0+ | Web Dashboard | Python-native UI with first-class support for streaming, tool-call visualization, and file management. Integrates seamlessly with Pydantic AI. |
| **Aiogram** | 3.13.0+ | Telegram Bot | High-performance, fully asynchronous Telegram framework. Preferred over `pyTelegramBotAPI` for modern agentic loops and complex FSM (Finite State Machine) needs. |
| **Discord.py** | 2.4.0+ | Discord Bot | The industry standard for Python Discord bots. Reliable, well-documented, and handles large event volumes efficiently. |

### Data & Persistence
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **SQLAlchemy** | 2.0.x | ORM | Provides a robust, type-safe interface for database operations. Essential for managing session history and user preferences. |
| **SQLite** | 3.x | Database | Zero-configuration, file-based database. Perfect for self-hosted, single-user systems. High performance and easy to back up/migrate. |

### Infrastructure & Security
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Docker Compose** | Latest | Orchestration | Simplifies deployment and ensures environment consistency across different host systems. |
| **Docker Engine** | 27.x+ | Sandboxing | Critical for isolating `open-interpreter` execution. Prevents the agent from accidentally (or maliciously) damaging the host OS during code execution. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Orchestration | Pydantic AI | LangChain | LangChain has high abstraction overhead and "brittle" components. Pydantic AI is more Pythonic and robust for production logic. |
| System Control| Open Interpreter| Composio | Composio is excellent for SaaS tools but Open Interpreter is superior for raw OS-level control and local file manipulation. |
| UI | Chainlit | Streamlit | Streamlit is not designed for conversational state or long-running agent loops; Chainlit's event-driven model is built for it. |
| Database | SQLite | PostgreSQL | Postgres adds unnecessary maintenance overhead for a self-hosted single-user tool. SQLite handles IronClaw's scale with ease. |

## Installation

```bash
# Core Dependencies
pip install pydantic-ai open-interpreter chainlit aiogram discord.py sqlalchemy

# Optional: Performance & Security
pip install "open-interpreter[local]" # For local model support (Ollama/Llama.cpp)
```

## Implementation Strategy (2025 Patterns)

1.  **The "Unified Brain" Pattern:** Don't write three separate bots. Build one `Pydantic AI` Agent and create "Adapters" for Chainlit, Telegram, and Discord.
2.  **MCP First:** Use the Model Context Protocol (MCP) to define tools. This makes the tools usable not just by IronClaw, but any MCP-compliant client.
3.  **Strict Sandboxing:** Always run `interpreter.computer.run()` inside a Docker container with restricted network access unless explicitly granted.
4.  **Async Everything:** Ensure the entire stack (from DB to Bots) uses `async/await` to prevent blocking the agent's thought process during I/O.

## Sources

- **Pydantic AI Documentation:** https://ai.pydantic.dev/ (HIGH confidence)
- **Open Interpreter GitHub/Docs:** https://github.com/OpenInterpreter/open-interpreter (HIGH confidence)
- **Chainlit Official Docs:** https://docs.chainlit.io/ (MEDIUM confidence - version 2.0 features based on roadmap)
- **Aiogram 3.x Docs:** https://docs.aiogram.dev/ (HIGH confidence)
- **Ecosystem Research:** 2025 State of AI Agents (Web Search verified) (MEDIUM confidence)
