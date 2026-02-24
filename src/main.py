import os
import asyncio
from dotenv import load_dotenv
from src.agent.core import ironclaw_agent, CodeExecutionRequest

# Load API keys from .env
load_dotenv()

async def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" IronClaw Agent System - Phase 1 CLI Bridge")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Type 'exit' or 'quit' to stop.")
    
    # Check which model to use. Default to gemini-1.5-flash if GEMINI_API_KEY is set.
    model_name = "google-gla:gemini-1.5-flash" if os.environ.get("GEMINI_API_KEY") else "openai:gpt-4o"
    
    while True:
        try:
            user_input = input("
User: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                break
            
            # Run the agent
            result = await ironclaw_agent.run(user_input, model=model_name)
            
            # Handle the result
            response = result.data
            
            if isinstance(response, CodeExecutionRequest):
                print(f"
Agent Logic:
{response.reasoning}")
                print("
--- Proposed Code ---")
                for i, block in enumerate(response.blocks, 1):
                    print(f"[{i}] {block.language}:
{block.code}
")
                
                approval = input("Approve execution? (y/n): ").strip().lower()
                if approval in ["y", "yes"]:
                    print("Executing...")
                    # Tell the agent to confirm
                    confirm_result = await ironclaw_agent.run("Confirm the execution.", message_history=result.all_messages(), model=model_name)
                    print(f"
Result:
{confirm_result.data}")
                else:
                    print("Execution cancelled by user.")
            else:
                print(f"
Agent: {response}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: No API key found. Please set GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in .env")
    else:
        asyncio.run(main())
