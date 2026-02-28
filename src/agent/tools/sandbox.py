import os
import re
from typing import List, Union, Optional, Callable
from pydantic import BaseModel
from google import genai
import ollama as ollama_lib
from interpreter import interpreter
from src.sandbox.manager import SandboxManager
from src.sandbox.languages import DockerPython, DockerShell
from src.agent.provider import get_provider_config, OllamaUnavailableError

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
        
        # Create language classes (not instances) with container baked in
        container = self.container
        
        class BoundDockerPython(DockerPython):
            def __init__(self):
                super().__init__(container)

        class BoundDockerShell(DockerShell):
            def __init__(self):
                super().__init__(container)

        interpreter.computer.languages = [BoundDockerPython, BoundDockerShell]

        # Configure Open Interpreter's LLM to use Gemini via LiteLLM
        interpreter.llm.model = "gemini/gemini-2.5-flash"
        interpreter.llm.api_key = os.environ.get("GEMINI_API_KEY")
        
        # Configure interpreter behavior
        # auto_run=True so OI's own HITL loop doesn't interfere when
        # confirm_execution() calls interpreter.computer.run() directly.
        # Our HITL is enforced at the Pydantic AI layer via CodeExecutionRequest.
        interpreter.auto_run = True
        interpreter.offline = False
        interpreter.safe_mode = False
        
        # To store the last generated blocks for confirmation
        self.pending_blocks: List[CodeBlock] = []

    def _parse_code_blocks(self, text: str) -> List[CodeBlock]:
        """Extract fenced code blocks from LLM response text.

        Parses ```lang\\n...\\n``` fences, normalises language identifiers to
        what Open Interpreter's computer understands ("shell" or "python"), and
        falls back to treating the whole response as shell if no fences found.
        """
        code_blocks: List[CodeBlock] = []
        pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
        for match in pattern.finditer(text):
            lang = match.group(1) or "shell"
            code = match.group(2).strip()
            # Normalise language identifiers to what OI's computer understands
            if lang in ("sh", "bash", "shell", "zsh"):
                lang = "shell"
            elif lang in ("py", "python"):
                lang = "python"
            if code:
                code_blocks.append(CodeBlock(code=code, language=lang))

        # Fallback: no fences found — treat entire response as shell code
        if not code_blocks and text.strip():
            code_blocks.append(CodeBlock(code=text.strip(), language="shell"))

        return code_blocks

    def run_system_task(
        self,
        task: str,
        on_output: Optional[Callable[[str], None]] = None,
    ) -> Union[CodeExecutionRequest, str]:
        """
        Generates code for a natural language task but does NOT execute it.
        Routes to Ollama (streaming) or Gemini based on provider config.
        Returns a CodeExecutionRequest for human approval.
        """
        self.pending_blocks = []

        config = get_provider_config()

        prompt = (
            f"Generate shell or Python code to accomplish the following task:\n\n"
            f"{task}\n\n"
            "Return ONLY the code blocks with proper language fences "
            "(e.g. ```python or ```bash), no explanations before or after."
        )

        if config.provider == "ollama":
            # Ollama branch: stream tokens progressively through on_output callback
            os.environ["OLLAMA_HOST"] = config.ollama_base_url
            try:
                stream = ollama_lib.generate(
                    model=config.ollama_codegen_model,
                    prompt=prompt,
                    stream=True,
                )
                text = ""
                for chunk in stream:
                    token = chunk.get("response", "")
                    text += token
                    if on_output:
                        on_output(token)
            except Exception as e:
                raise OllamaUnavailableError(
                    f"Ollama connection failed during code generation: {e}\n"
                    f"Check that Ollama is running at {config.ollama_base_url}"
                ) from e
        else:
            # Gemini branch (handles "gemini", "anthropic", "openai" — existing behaviour)
            api_key = os.environ.get("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            text = response.text or ""

        code_blocks = self._parse_code_blocks(text)

        if not code_blocks:
            return "No code was generated for this task."

        self.pending_blocks = code_blocks
        reasoning = f"To accomplish: {task}"
        return CodeExecutionRequest(
            blocks=code_blocks,
            reasoning=reasoning,
        )

    def confirm_execution(self, on_output: Optional[Callable[[str], None]] = None) -> str:
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
                    content = chunk.get("content", "")
                    result_str += content
                    if on_output and content:
                        on_output(content)
            
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

def confirm_execution(on_output: Optional[Callable[[str], None]] = None) -> str:
    """Execute the previously planned and approved system task."""
    return get_sandbox_tool().confirm_execution(on_output=on_output)
