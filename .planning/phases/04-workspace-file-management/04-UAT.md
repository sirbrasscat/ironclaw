---
status: resolved
phase: 04-workspace-file-management
source: [04-01-SUMMARY.md, 04-02-SUMMARY.md]
started: 2026-02-27T20:00:00Z
updated: 2026-02-28T10:00:00Z
---

## Current Test
<!-- OVERWRITE each test - shows where we are -->

number: 5
name: Auto-discovery of agent-created files
expected: |
  Ask the agent to create a file (e.g. "create a file called output.txt with the text hello world").
  After the agent runs the code, the UI should automatically display a download link for output.txt
  without you having to type /files.
awaiting: complete

## Tests

### 1. Upload a file via the web UI
expected: In the Chainlit web UI, attach a file (drag-and-drop or paperclip icon). After uploading, the file should appear in the ./workspace directory on disk and a confirmation message should appear in the chat.
result: [pass]

### 2. Agent can list workspace files
expected: Ask the agent "what files are in my workspace?" (or similar). The agent should call its list_workspace_files tool and respond with the names of files currently in ./workspace (including any you just uploaded).
result: [pass]

### 3. Uploaded files are accessible inside the Docker sandbox
expected: Ask the agent to read or process a file you uploaded (e.g. "read the contents of myfile.txt"). The agent should be able to access it at /workspace/myfile.txt inside the container and return its contents.
result: [fail: Agent generated code using ~/.bash_history which inside the Docker container resolves to /.bash_history (not /workspace/.bash_history). The file was not found. The system prompt does not tell the agent to look in /workspace/ for uploaded files; the agent used a home-directory path instead.]

### 4. /files command shows workspace contents
expected: Type /files in the chat. The UI should respond with a list of files currently in the workspace, each as a clickable download link.
result: [pass]

### 5. Auto-discovery of agent-created files
expected: Ask the agent to create a file (e.g. "create a file called output.txt with the text hello world"). After the agent runs the code, the UI should automatically display a download link for output.txt without you having to type /files.
result: [pass]

## Summary

total: 5
passed: 4
issues: 1
pending: 0
skipped: 0

## Gaps

### Gap 1 — Agent does not know to look in /workspace/ for uploaded files

**Affected test:** Test 3 — Uploaded files accessible inside Docker sandbox

**Observed behavior:** The agent generated code referencing `~/.bash_history`, which inside the Docker container resolves to `/.bash_history` rather than `/workspace/.bash_history`. The file was not found.

**Root cause:** The system prompt (`src/agent/prompts.py`) does not instruct the agent that uploaded files are placed in `/workspace/` inside the container. Without this guidance, the agent falls back to default shell conventions (e.g., home directory paths) rather than consulting the mounted workspace volume.

**Impact on requirements:**
- ENG-03 is partially satisfied: the workspace bind-mount works correctly (tests 1, 2, 4, 5 all pass), but the agent's knowledge of where to find uploaded files is incomplete.

**Suggested fix:** Add a line to the system prompt explaining that all user-uploaded files are available at `/workspace/<filename>` inside the Docker container, and that the workspace is mounted at `./workspace` on the host.
