import os
from typing import List

def list_workspace_files() -> List[str]:
    """
    Returns a list of all files in the ./workspace directory.
    If the directory does not exist, it creates it and returns an empty list.
    """
    workspace_path = "./workspace"
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)
        return []
    
    # List all files (not directories)
    files = [f for f in os.listdir(workspace_path) if os.path.isfile(os.path.join(workspace_path, f))]
    return files
