from typing import Generator
from interpreter.core.computer.terminal.base_language import BaseLanguage

class DockerLanguage(BaseLanguage):
    def __init__(self, container):
        self.container = container

    def stop(self):
        pass

    def terminate(self):
        pass

class DockerPython(DockerLanguage):
    name = "python"
    file_extension = "py"
    aliases = ["python3", "py"]

    def run(self, code: str) -> Generator[dict, None, None]:
        result = self.container.exec_run(["python3", "-c", code])
        yield {"type": "console", "format": "output", "content": result.output.decode("utf-8")}

class DockerShell(DockerLanguage):
    name = "shell"
    file_extension = "sh"
    aliases = ["bash", "sh", "zsh"]

    def run(self, code: str) -> Generator[dict, None, None]:
        result = self.container.exec_run(["/bin/bash", "-c", code])
        yield {"type": "console", "format": "output", "content": result.output.decode("utf-8")}
