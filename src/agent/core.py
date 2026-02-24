import os
from dataclasses import dataclass
from typing import Union, Optional, Callable
from pydantic_ai import Agent, RunContext
from src.agent.prompts import IRONCLAW_SYSTEM_PROMPT
from src.agent.tools.sandbox import (
    run_system_task as _run_system_task,
    confirm_execution as _confirm_execution,
    CodeExecutionRequest
)
from src.agent.tools.workspace import list_workspace_files as _list_workspace_files

# Choose default model based on environment
if os.environ.get("GEMINI_API_KEY"):
    default_model = 'google-gla:gemini-2.5-flash'
elif os.environ.get("ANTHROPIC_API_KEY"):
    default_model = 'anthropic:claude-3-5-sonnet-latest'
else:
    default_model = 'openai:gpt-4o'

@dataclass
class AgentDeps:
    on_output: Optional[Callable[[str], None]] = None

# Define the agent with support for structured HITL requests
ironclaw_agent = Agent(
    default_model, 
    system_prompt=IRONCLAW_SYSTEM_PROMPT,
    deps_type=AgentDeps,
    output_type=Union[CodeExecutionRequest, str]
)

# Register the tools
@ironclaw_agent.tool_plain
def run_system_task(task: str) -> Union[CodeExecutionRequest, str]:
    """
    Plans a natural language task in the sandboxed environment and generates code.
    Use this for any system operations. It will return a request for approval.
    """
    return _run_system_task(task)

@ironclaw_agent.tool
def confirm_execution(ctx: RunContext[AgentDeps]) -> str:
    """
    Executes the pending code blocks that were previously generated and approved.
    """
    on_output = ctx.deps.on_output if ctx.deps else None
    return _confirm_execution(on_output=on_output)

@ironclaw_agent.tool_plain
def list_workspace_files() -> str:
    """
    Returns a list of all files in the current workspace.
    """
    files = _list_workspace_files()
    if not files:
        return "Workspace is empty."
    return f"Files in workspace: {', '.join(files)}"
