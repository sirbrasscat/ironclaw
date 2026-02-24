# Domain Pitfalls

**Domain:** Self-Hosted AI Agent System (IronClaw)
**Researched:** 2026-02-23

## Critical Pitfalls

Mistakes that cause rewrites, security breaches, or major system damage.

### Pitfall 1: The "God Mode" Sandbox Failure
**What goes wrong:** Running `open-interpreter` directly on the host machine without isolation (Docker/E2B), assuming "I'm just testing" or "I trust the LLM."
**Why it happens:** Setting up Docker is "friction." Developers want immediate access to local files for convenience.
**Consequences:** 
- **Accidental Destruction:** LLM hallucinating `rm -rf /` or modifying system configs (e.g., `.bashrc`, `ssh` keys).
- **Malicious Injection:** Prompt injection from external inputs (Telegram/Discord) executing arbitrary code on the host.
- **Privacy Leak:** Agent reading and sending sensitive local files (SSH keys, env vars) to external APIs.
**Prevention:** 
- **Mandatory Sandboxing:** Run the agent *only* inside a Docker container with mounted volumes for specific working directories.
- **`--safe_mode`:** Enable `open-interpreter`'s safe mode or confirmation prompts (though confirmation fatigue leads to "Yes to all").
- **Least Privilege:** Run the container as a non-root user.
**Detection:** Check if the process is running as `root` on the host. Check for access to sensitive directories (`~/.ssh`, `/etc`).

### Pitfall 2: State Fragmentation (The "Split Brain" Agent)
**What goes wrong:** Managing conversation state separately in Chainlit (memory) and Telegram/Discord (memory/local dicts).
**Why it happens:** Treating each interface as a standalone app rather than a view into a shared backend.
**Consequences:** 
- User context is lost when switching devices (start on Web, continue on Telegram -> Agent forgets).
- "Amnesia": Restarting the server wipes all context if using in-memory storage.
- Race conditions: Web and Telegram updating state simultaneously.
**Prevention:** 
- **Unified Backend:** Use a shared database (PostgreSQL/SQLite) or a persistent state framework (e.g., LangGraph with checkpoints) for *all* interfaces.
- **Session IDs:** Map Telegram Chat IDs and Discord User IDs to a unified `user_id` or `session_id` in the database.
**Detection:** Try starting a task on Telegram and asking for its status on the Web UI. If it fails, you have split brains.

### Pitfall 3: "ChainLeak" & Unsecured Web Sockets
**What goes wrong:** Exposing the Chainlit UI to the public internet without robust auth, or vulnerable versions (pre-2.9.4).
**Why it happens:** Defaulting to "local only" mental model but exposing via tunnel (ngrok) or port forwarding for remote access.
**Consequences:** 
- **Arbitrary File Read:** Vulnerabilities like CVE-2026-22218 allow attackers to read files via the UI.
- **SSRF:** Server-Side Request Forgery via the chat interface.
- **Session Hijacking:** IP-based session mixing behind reverse proxies/VPNs.
**Prevention:** 
- **Update Chainlit:** Ensure version >= 2.9.4.
- **Strict Auth:** Enable Chainlit's authentication callbacks immediately.
- **Session Config:** Use `context.session.id` explicitly; do not rely on global user session objects in async contexts.

## Moderate Pitfalls

### Pitfall 4: API Rate Limit Suicide (Log Streaming)
**What goes wrong:** Streaming `open-interpreter`'s verbose logs or code execution line-by-line to Telegram/Discord.
**Why it happens:** Trying to replicate the "Matrix code" effect from the CLI/Web UI in chat apps.
**Consequences:** 
- **Ban/Throttle:** Hitting Telegram's ~1 msg/sec limit or Discord's rate limits.
- **UX Nightmare:** User's phone buzzes 50 times for one command execution.
**Prevention:** 
- **Batching/Throttling:** Buffer logs and update a *single* message every 1-2 seconds (edit message).
- **Summary Mode:** Only send the *result* to chat, keep verbose logs in the Web UI.

### Pitfall 5: The "Infinite Loop" Cost Trap
**What goes wrong:** Agent gets stuck in a loop correcting its own code errors (running, failing, fixing, running, failing...), consuming infinite tokens.
**Why it happens:** `open-interpreter`'s auto-run loop lacking a "max retries" clamp.
**Consequences:** 
- **Bill Shock:** Draining OpenAI/Anthropic credits overnight.
- **Zombie Processes:** Leaving hundreds of orphaned Python processes or unclosed file handles.
**Prevention:** 
- **Budget Limits:** Set a hard cap on loops/turns per user request.
- **Cost Monitoring:** Middleware to track token usage per session.
- **Kill Switch:** A dedicated command (e.g., `/stop`) that forcibly kills the interpreter subprocess.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| **Core Engine** | Unsandboxed execution | Start with Docker *immediately*. Do not build "bare metal" first. |
| **Web Dashboard** | Session mixing | Test with 2 browsers/incognito windows to ensure state isolation. |
| **Messaging Bridges** | Rate limit bans | Implement a "MessageBuffer" class that edits messages instead of sending new ones. |
| **System Control** | `rm -rf` disasters | Blocklist dangerous commands (regex) even in the LLM prompt. |
| **Deployment** | Public exposure | Put behind a reverse proxy (Nginx/Caddy) with Basic Auth if Chainlit auth is disabled. |

## Sources

- [Open Interpreter Security Advisories](https://openinterpreter.com)
- [Chainlit Security (CVE-2026-22218)](https://chainlit.io/security)
- [Telegram Bot API Rate Limits](https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
