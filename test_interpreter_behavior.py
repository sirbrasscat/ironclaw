from interpreter import interpreter
from src.sandbox.manager import SandboxManager
from src.sandbox.languages import DockerPython, DockerShell
import os

# Mock container for testing
manager = SandboxManager()
container = manager.get_or_create_container()

interpreter.computer.languages = [
    DockerPython(container),
    DockerShell(container)
]
interpreter.auto_run = False
interpreter.offline = True # Don't actually call LLM if possible, or use a mock

messages = interpreter.chat("echo 'hello'")
print(messages)
