import os
import json
from typing import List, Dict, Any, Union
from pydantic import BaseModel
from interpreter import interpreter
from src.sandbox.manager import SandboxManager
from src.sandbox.languages import DockerPython, DockerShell

class CodeBlock(BaseModel):
    code: str
    language: str

class CodeExecutionRequest(BaseModel):
    status: str = "PENDING_APPROVAL"
    blocks: List[CodeBlock]
    reasoning: str

class SandboxedTool:
    def __init__(self):
        self.manager = SandboxManager()
        self.container = self.manager.get_or_create_container()
        
        # Reset and configure interpreter
        interpreter.computer.languages = [
            DockerPython(self.container),
            DockerShell(self.container)
        ]
        
        # Configure interpreter behavior
        interpreter.auto_run = False  # Mandatory HITL
        interpreter.offline = False
        interpreter.safe_mode = False
        
        # To store the last generated blocks for confirmation
        self.pending_blocks: List[CodeBlock] = []

    def run_system_task(self, task: str) -> Union[CodeExecutionRequest, str]:
        """
        Generates code for a natural language task but does NOT execute it.
        Returns a CodeExecutionRequest for human approval.
        """
        # Clear previous pending blocks
        self.pending_blocks = []
        
        # We use chat to get the plan and code
        messages = interpreter.chat(task)
        
        code_blocks = []
        reasoning = ""
        
        for msg in messages:
            if msg.get("role") == "assistant":
                if msg.get("type") == "message":
                    reasoning += msg.get("content", "") + "\n"
                elif msg.get("type") == "code":
                    code_blocks.append(CodeBlock(
                        code=msg.get("code", ""),
                        language=msg.get("language", "")
                    ))
        
        if not code_blocks:
            return reasoning or "No code was generated for this task."

        self.pending_blocks = code_blocks
        return CodeExecutionRequest(
            blocks=code_blocks,
            reasoning=reasoning.strip()
        )

    def confirm_execution(self) -> str:
        """
        Executes the pending code blocks after human approval.
        """
        if not self.pending_blocks:
            return "No pending code to execute."
        
        results = []
        for block in self.pending_blocks:
            # Execute each block using the interpreter's computer
            # This ensures it uses the configured Docker languages
            output = interpreter.computer.run(block.language, block.code)
            
            # Format output
            result_str = ""
            for chunk in output:
                if chunk.get("type") == "console":
                    result_str += chunk.get("content", "")
            
            results.append(f"--- Output ({block.language}) ---\n{result_str}")
        
        self.pending_blocks = [] # Clear after execution
        return "\n".join(results)

# Instance to be used
_sandbox_tool = None

def get_sandbox_tool():
    global _sandbox_tool
    if _sandbox_tool is None:
        _sandbox_tool = SandboxedTool()
    return _sandbox_tool

def run_system_task(task: str) -> Union[CodeExecutionRequest, str]:
    """Plan a system task and request approval for code execution."""
    return get_sandbox_tool().run_system_task(task)

def confirm_execution() -> str:
    """Execute the previously planned and approved system task."""
    return get_sandbox_tool().confirm_execution()
