import docker
import os
import time
from typing import Optional
from docker.models.containers import Container
from docker.errors import DockerException, ImageNotFound

class SandboxManager:
    def __init__(self, image: str = "ironclaw-agent", container_name: str = "ironclaw-sandbox"):
        try:
            self.client = docker.from_env()
        except DockerException as e:
            raise RuntimeError(f"Could not connect to Docker: {e}")
        
        self.image = image
        self.container_name = container_name
        self.workspace_path = os.path.abspath("workspace")
        os.makedirs(self.workspace_path, exist_ok=True)

    def get_or_create_container(self) -> Container:
        """
        Gets the existing container or creates a new one.
        The container runs a persistent 'tail -f /dev/null' command.
        """
        try:
            container = self.client.containers.get(self.container_name)
            if container.status != "running":
                container.start()
            return container
        except docker.errors.NotFound:
            # Ensure image exists
            try:
                self.client.images.get(self.image)
            except ImageNotFound:
                if self.image == "ironclaw-agent" and os.path.exists("Dockerfile"):
                    print(f"Building image {self.image} from Dockerfile...")
                    self.client.images.build(path=".", tag=self.image)
                else:
                    print(f"Pulling image {self.image}...")
                    self.client.images.pull(self.image)

            # Create container
            container = self.client.containers.run(
                self.image,
                command="tail -f /dev/null",
                name=self.container_name,
                detach=True,
                volumes={
                    self.workspace_path: {"bind": "/workspace", "mode": "rw"}
                },
                working_dir="/workspace",
                # Run as current user to avoid permission issues with volume mounts
                user=f"{os.getuid()}:{os.getgid()}" if hasattr(os, 'getuid') else None
            )
            return container

    def stop_container(self):
        """Stops and removes the container."""
        try:
            container = self.client.containers.get(self.container_name)
            container.stop()
            container.remove()
        except docker.errors.NotFound:
            pass
        except DockerException as e:
            print(f"Error stopping container: {e}")

if __name__ == "__main__":
    sm = SandboxManager()
    container = sm.get_or_create_container()
    print(f"Container {container.name} is {container.status}")
    sm.stop_container()
    print("Container stopped and removed.")
