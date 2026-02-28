from src.agent.tools.workspace import list_workspace_files
files = list_workspace_files()
print(f"Files found: {files}")
if 'test_file.txt' in files:
    print("SUCCESS: test_file.txt found in workspace.")
else:
    print("FAILURE: test_file.txt NOT found in workspace.")
