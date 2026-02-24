import pytest
from src.sandbox.manager import SandboxManager
from src.sandbox.languages import DockerPython, DockerShell

@pytest.fixture(scope="module")
def sandbox_container():
    sm = SandboxManager()
    container = sm.get_or_create_container()
    yield container
    sm.stop_container()

def test_docker_shell(sandbox_container):
    shell = DockerShell(sandbox_container)
    results = list(shell.run('echo "hello"'))
    assert len(results) > 0
    assert "hello" in results[0]["output"]

def test_docker_python(sandbox_container):
    python = DockerPython(sandbox_container)
    results = list(python.run('print(1+1)'))
    assert len(results) > 0
    assert "2" in results[0]["output"]
