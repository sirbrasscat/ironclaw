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
from src.agent.core import ironclaw_agent, CodeExecutionRequest
from src.database.manager import DatabaseManager

import argparse

async def main(session_id: str = "default"):
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" IronClaw Agent System - Phase 2 Persistence")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Session: {session_id}")
    print("Type 'exit' or 'quit' to stop.")
    
    db = DatabaseManager()
    await db.initialize_db()
    
    await db.get_or_create_session(session_id)
    
    # Load history
    history_dicts = await db.get_messages(session_id)
    adapter = TypeAdapter(list[ModelMessage])
    history = adapter.validate_python(history_dicts) if history_dicts else []
    
    if history:
        print(f"[*] Loaded {len(history)} previous messages.")
    
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
                output_type=CodeExecutionRequest | str
            )
            
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
                        output_type=str
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
    if not any(os.environ.get(k) for k in ["GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]):
        print("Error: No API key found. Please set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in .env")
    else:
        parser = argparse.ArgumentParser(description="IronClaw Agent CLI")
        parser.add_argument("--session", type=str, default="default", help="Session ID to load/create")
        args = parser.parse_args()
        
        asyncio.run(main(args.session))
