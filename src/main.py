import os
import sys

# Ensure project root is in sys.path so `from src.X` imports work
# regardless of how this script is invoked (e.g. `python3 src/main.py`)
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
# Load BEFORE importing src.agent.core
load_dotenv()

import asyncio
from pydantic import TypeAdapter
from pydantic_ai.messages import ModelMessage
from src.agent.core import ironclaw_agent, CodeExecutionRequest, AgentDeps
from src.agent.provider import get_provider_config, check_ollama_health, get_missing_models, provider_banner
from src.database.manager import DatabaseManager

import argparse

async def main(session_id: str = "default"):
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" IronClaw Agent System - Phase 2 Persistence")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Session: {session_id}")
    print("Type 'exit' or 'quit' to stop.")

    # Provider banner
    _cfg = get_provider_config()
    print(provider_banner(_cfg))

    # Ollama startup health check
    if _cfg.provider == "ollama":
        reachable, pulled_models = await check_ollama_health(_cfg)
        if not reachable:
            answer = input(
                f"Ollama unavailable at {_cfg.ollama_base_url}. Fall back to cloud? [y/N] "
            ).strip().lower()
            if answer not in ("y", "yes"):
                print("Aborting. Start Ollama and retry, or set PROVIDER to a cloud provider.")
                return
            else:
                # Re-resolve config without Ollama (unset PROVIDER, let fallback chain run)
                import os as _os
                _os.environ.pop("PROVIDER", None)
                _cfg = get_provider_config()
                print(provider_banner(_cfg))
        else:
            missing = get_missing_models(_cfg, pulled_models)
            if missing:
                for m in missing:
                    print(f"[!] Model not pulled: {m}. Run: ollama pull {m}")
                print("Aborting. Pull the required models and retry.")
                return

    db = DatabaseManager()
    await db.initialize_db()
    
    await db.get_or_create_session(session_id)
    
    # Load history
    history_dicts = await db.get_messages(session_id)
    adapter = TypeAdapter(list[ModelMessage])
    history = adapter.validate_python(history_dicts) if history_dicts else []
    
    if history:
        print(f"[*] Loaded {len(history)} previous messages.")
    
    _callback = lambda token: print(token, end='', flush=True)
    _deps = AgentDeps(on_output=_callback)

    while True:
        try:
            user_input = input("\nUser: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                break
            
            result = await ironclaw_agent.run(
                user_input,
                message_history=history,
                output_type=CodeExecutionRequest | str,
                deps=_deps,
            )
            print()  # trailing newline after streaming so approval prompt starts on its own line
            
            # Save new messages
            new_msgs = adapter.dump_python(result.new_messages(), mode='json')
            await db.save_messages(session_id, new_msgs)
            
            # Update local history
            history = result.all_messages()
            
            response = result.output
            
            if isinstance(response, CodeExecutionRequest):
                print(f"\nAgent Logic:\n{response.reasoning}")
                print("\n--- Proposed Code ---")
                for i, block in enumerate(response.blocks, 1):
                    print(f"[{i}] {block.language}:\n{block.code}\n")
                
                approval = input("Approve execution? (y/n): ").strip().lower()
                if approval in ["y", "yes"]:
                    print("Executing...")
                    confirm_result = await ironclaw_agent.run(
                        "Confirm the execution.",
                        message_history=history,
                        output_type=str,
                        deps=_deps,
                    )
                    
                    # Save confirmation messages
                    confirm_new_msgs = adapter.dump_python(confirm_result.new_messages(), mode='json')
                    await db.save_messages(session_id, confirm_new_msgs)
                    
                    # Update local history
                    history = confirm_result.all_messages()
                    
                    print(f"\nResult:\n{confirm_result.output}")
                else:
                    print("Execution cancelled by user.")
            else:
                print(f"\nAgent: {response}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    await db.close()

if __name__ == "__main__":
    _startup_cfg = get_provider_config()
    if _startup_cfg.provider != "ollama" and not any(
        os.environ.get(k) for k in ["GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    ):
        print("Error: No API key found. Set GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, or PROVIDER=ollama in .env")
    else:
        parser = argparse.ArgumentParser(description="IronClaw Agent CLI")
        parser.add_argument("--session", type=str, default="default", help="Session ID to load/create")
        args = parser.parse_args()
        asyncio.run(main(args.session))
