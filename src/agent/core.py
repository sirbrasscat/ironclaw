import os
from typing import Union
from pydantic_ai import Agent
from src.agent.prompts import IRONCLAW_SYSTEM_PROMPT
from src.agent.tools.sandbox import (
    run_system_task as _run_system_task,
    confirm_execution as _confirm_execution,
    CodeExecutionRequest
)

# Choose default model based on environment
if os.environ.get("GEMINI_API_KEY"):
    default_model = 'google-gla:gemini-3-flash-preview'
elif os.environ.get("ANTHROPIC_API_KEY"):
    default_model = 'anthropic:claude-3-5-sonnet-latest'
else:
    default_model = 'openai:gpt-4o'

# Define the agent without result_type in constructor
ironclaw_agent = Agent(
    default_model, 
    system_prompt=IRONCLAW_SYSTEM_PROMPT,
)

# Register the tools
@ironclaw_agent.tool_plain
def run_system_task(task: str) -> Union[CodeExecutionRequest, str]:
    """
    Plans a natural language task in the sandboxed environment and generates code.
    Use this for any system operations. It will return a request for approval.
    """
    return _run_system_task(task)

@ironclaw_agent.tool_plain
def confirm_execution() -> str:
    """
    Executes the pending code blocks that were previously generated and approved.
    """
    return _confirm_execution()
