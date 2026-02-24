from typing import Generator

class DockerLanguage:
    def __init__(self, container):
        self.container = container

class DockerPython(DockerLanguage):
    def run(self, code: str) -> Generator[dict, None, None]:
        # Open Interpreter expects a generator of dictionaries
        result = self.container.exec_run(["python3", "-c", code])
        yield {"output": result.output.decode("utf-8")}

class DockerShell(DockerLanguage):
    def run(self, code: str) -> Generator[dict, None, None]:
        result = self.container.exec_run(["/bin/bash", "-c", code])
        yield {"output": result.output.decode("utf-8")}
