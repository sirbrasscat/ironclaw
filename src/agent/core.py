from typing import Union
from pydantic_ai import Agent
from src.agent.prompts import IRONCLAW_SYSTEM_PROMPT
from src.agent.tools.sandbox import (
    run_system_task as _run_system_task,
    confirm_execution as _confirm_execution,
    CodeExecutionRequest
)

# Define the agent with a placeholder model. The actual model can be overridden in run().
ironclaw_agent = Agent(
    'openai:gpt-4o', 
    system_prompt=IRONCLAW_SYSTEM_PROMPT,
    result_type=Union[CodeExecutionRequest, str]
)

# Register the tools
@ironclaw_agent.tool_plain
def run_system_task(task: str) -> Union[CodeExecutionRequest, str]:
    """
    Plans a natural language task in the sandboxed environment and generates code.
    Use this for any system operations. It will return a request for approval.
    
    Args:
        task: A natural language description of the task to perform.
    """
    return _run_system_task(task)

@ironclaw_agent.tool_plain
def confirm_execution() -> str:
    """
    Executes the pending code blocks that were previously generated and approved.
    Call this ONLY after the user has explicitly approved the code shown in the CodeExecutionRequest.
    """
    return _confirm_execution()
