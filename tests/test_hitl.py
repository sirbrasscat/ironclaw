import pytest
from unittest.mock import MagicMock, patch
from src.agent.tools.sandbox import get_sandbox_tool, CodeExecutionRequest

@pytest.fixture
def sandbox_tool():
    tool = get_sandbox_tool()
    # Reset pending blocks before each test
    tool.pending_blocks = []
    return tool

@patch('src.agent.tools.sandbox.interpreter')
def test_run_system_task_generates_request(mock_interpreter, sandbox_tool):
    # Setup mock response from interpreter.chat
    mock_interpreter.chat.return_value = [
        {"role": "assistant", "type": "message", "content": "I will list files."},
        {"role": "assistant", "type": "code", "language": "shell", "code": "ls -la"}
    ]
    
    result = sandbox_tool.run_system_task("list files")
    
    assert isinstance(result, CodeExecutionRequest)
    assert result.status == "PENDING_APPROVAL"
    assert len(result.blocks) == 1
    assert result.blocks[0].code == "ls -la"
    assert result.blocks[0].language == "shell"
    assert "I will list files" in result.reasoning
    assert len(sandbox_tool.pending_blocks) == 1

@patch('src.agent.tools.sandbox.interpreter')
def test_confirm_execution_calls_computer_run(mock_interpreter, sandbox_tool):
    # Manually set pending blocks
    from src.agent.tools.sandbox import CodeBlock
    sandbox_tool.pending_blocks = [CodeBlock(code="echo hello", language="shell")]
    
    # Setup mock for interpreter.computer.run
    mock_interpreter.computer.run.return_value = [
        {"type": "console", "content": "hello\n"}
    ]
    
    result = sandbox_tool.confirm_execution()
    
    mock_interpreter.computer.run.assert_called_once_with("shell", "echo hello")
    assert "hello" in result
    assert len(sandbox_tool.pending_blocks) == 0

def test_confirm_execution_no_pending(sandbox_tool):
    result = sandbox_tool.confirm_execution()
    assert result == "No pending code to execute."
