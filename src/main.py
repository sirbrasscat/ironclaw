import os
from dotenv import load_dotenv
# Load BEFORE importing src.agent.core
load_dotenv()

import asyncio
from src.agent.core import ironclaw_agent, CodeExecutionRequest

async def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" IronClaw Agent System - Phase 1 CLI Bridge")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            user_input = input("\nUser: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                break
            
            # Specify result_type during run
            result = await ironclaw_agent.run(
                user_input, 
                result_type=CodeExecutionRequest | str
            )
            
            response = result.data
            
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
                        message_history=result.all_messages(),
                        result_type=str
                    )
                    print(f"\nResult:\n{confirm_result.data}")
                else:
                    print("Execution cancelled by user.")
            else:
                print(f"\nAgent: {response}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if not any(os.environ.get(k) for k in ["GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]):
        print("Error: No API key found. Please set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in .env")
    else:
        asyncio.run(main())
