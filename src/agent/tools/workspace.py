import os
from typing import List, Dict, Set

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

def get_workspace_snapshot() -> Dict[str, float]:
    """
    Returns a dictionary of filenames and their modification times in the ./workspace directory.
    """
    workspace_path = "./workspace"
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)
        return {}
    
    snapshot = {}
    for f in os.listdir(workspace_path):
        path = os.path.join(workspace_path, f)
        if os.path.isfile(path):
            snapshot[f] = os.path.getmtime(path)
    return snapshot

def get_workspace_diff(old_snapshot: Dict[str, float], new_snapshot: Dict[str, float]) -> Set[str]:
    """
    Returns a set of files that were added or modified between two snapshots.
    """
    diff = set()
    for f, mtime in new_snapshot.items():
        if f not in old_snapshot or mtime > old_snapshot[f]:
            diff.add(f)
    return diff
