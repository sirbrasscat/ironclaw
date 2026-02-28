import pytest
from unittest.mock import MagicMock, patch
from src.agent.tools.sandbox import get_sandbox_tool, CodeExecutionRequest, CodeBlock

@pytest.fixture
def sandbox_tool():
    tool = get_sandbox_tool()
    tool.pending_blocks = [] # Reset
    return tool

def test_confirm_execution_with_callback(sandbox_tool):
    # Setup some pending blocks
    sandbox_tool.pending_blocks = [
        CodeBlock(code="echo hello", language="shell"),
        CodeBlock(code="echo world", language="shell")
    ]
    
    # Mock interpreter.computer.run
    with patch('src.agent.tools.sandbox.interpreter') as mock_interpreter:
        # Mocking the generator returned by interpreter.computer.run
        mock_interpreter.computer.run.side_effect = [
            [{"type": "console", "content": "hello\n"}],
            [{"type": "console", "content": "world\n"}]
        ]
        
        output_chunks = []
        def on_output(content):
            output_chunks.append(content)
        
        result = sandbox_tool.confirm_execution(on_output=on_output)
        
        assert "hello" in result
        assert "world" in result
        assert output_chunks == ["hello\n", "world\n"]
        assert len(sandbox_tool.pending_blocks) == 0

def test_confirm_execution_without_callback(sandbox_tool):
    sandbox_tool.pending_blocks = [
        CodeBlock(code="echo hello", language="shell")
    ]
    
    with patch('src.agent.tools.sandbox.interpreter') as mock_interpreter:
        mock_interpreter.computer.run.return_value = [{"type": "console", "content": "hello\n"}]
        
        result = sandbox_tool.confirm_execution()
        assert "hello" in result
        assert len(sandbox_tool.pending_blocks) == 0
