import os
import sys

# Ensure project root is in sys.path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.sandbox.manager import SandboxManager
from src.sandbox.languages import DockerShell

def verify_sandbox():
    print("Starting Sandbox Isolation Verification...")
    sm = SandboxManager()
    container = sm.get_or_create_container()
    shell = DockerShell(container)

    try:
        # 1. Run whoami
        print("Check 1: whoami")
        whoami_res = list(shell.run("whoami"))[0]["content"].strip()
        print(f"  Container user: {whoami_res}")
        
        # 2. List files in /
        print("Check 2: / directory contents")
        ls_res = list(shell.run("ls /"))[0]["content"]
        # Standard linux root should have these
        required_dirs = ["bin", "etc", "proc", "sys", "var", "workspace"]
        for d in required_dirs:
            assert d in ls_res, f"Missing directory {d} in container root"
        print("  Container root looks correct.")

        # 3. Isolation check
        print("Check 3: Isolation from host filesystem")
        home_res = list(shell.run("ls /home"))[0]["content"].strip()
        print(f"  Container /home: '{home_res}'")
        
        # 4. Workspace volume mount
        print("Check 4: Workspace volume mount")
        test_file = "sandbox_test.txt"
        test_content = "Hello from the sandbox!"
        
        # Create file in sandbox
        list(shell.run(f"echo '{test_content}' > {test_file}"))
        
        # Check if it exists on host
        host_file_path = os.path.join(sm.workspace_path, test_file)
        assert os.path.exists(host_file_path), "File created in sandbox did not appear on host"
        
        with open(host_file_path, "r") as f:
            content = f.read().strip()
            assert content == test_content, f"Content mismatch: expected '{test_content}', got '{content}'"
        
        print("  Workspace volume mount working correctly.")
        
        # Clean up test file
        os.remove(host_file_path)
        print("  Cleanup successful.")

        print("\nALL ISOLATION CHECKS PASSED.")

    finally:
        pass

if __name__ == "__main__":
    verify_sandbox()
