import os
import sys
from typing import Union

# Ensure project root is in sys.path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Python 3.14 + nest_asyncio compatibility fix.
# nest_asyncio replaces asyncio.Task (C impl) with _PyTask (Python impl), but
# Python 3.14's asyncio.current_task() still reads C-level storage, so it
# returns None inside patched loops. This patch makes current_task() also
# check _PyTask._current_tasks so that anyio/sniffio can detect asyncio.
if sys.version_info >= (3, 14):
    import asyncio as _asyncio
    _orig_current_task = _asyncio.current_task
    def _patched_current_task(loop=None):
        t = _orig_current_task(loop)
        if t is None:
            try:
                running_loop = _asyncio.get_event_loop()
                t = _asyncio.tasks._current_tasks.get(running_loop)
            except RuntimeError:
                pass
        return t
    _asyncio.current_task = _asyncio.tasks.current_task = _patched_current_task

import chainlit as cl
from dotenv import load_dotenv
from pydantic import TypeAdapter
from pydantic_ai.messages import ModelMessage

from src.agent.core import ironclaw_agent, AgentDeps
from src.agent.tools.sandbox import CodeExecutionRequest
from src.agent.tools.workspace import (
    list_workspace_files,
    get_workspace_snapshot,
    get_workspace_diff
)
from src.agent.provider import get_provider_config, check_ollama_health, get_missing_models, provider_banner
from src.database.manager import DatabaseManager

load_dotenv()

# Chainlit Auth
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    env_password = os.environ.get("CHAINLIT_PASSWORD", "ironclaw")
    if password == env_password:
        return cl.User(identifier=username)
    return None

# DB Manager
db = DatabaseManager()
adapter = TypeAdapter(list[ModelMessage])

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="List workspace files",
            message="/files",
            icon="https://cdn-icons-png.flaticon.com/512/3767/3767084.png",
        ),
    ]

@cl.on_chat_start
async def on_chat_start():
    # Ensure workspace directory exists
    if not os.path.exists("./workspace"):
        os.makedirs("./workspace")
    
    await db.initialize_db()
    
    user = cl.user_session.get("user")
    username = user.identifier if user else "default"
    
    # Persistence: Use a username-based session ID
    session_id = f"web-{username}"
    cl.user_session.set("session_id", session_id)
    
    await db.get_or_create_session(session_id)
    
    # Load history
    history_dicts = await db.get_messages(session_id)
    history = adapter.validate_python(history_dicts) if history_dicts else []
    cl.user_session.set("history", history)
    
    _cfg = get_provider_config()
    _banner = provider_banner(_cfg)
    await cl.Message(content=f"Welcome {username}! IronClaw is ready.\n\n{_banner}").send()

    if _cfg.provider == "ollama":
        reachable, pulled_models = await check_ollama_health(_cfg)
        if not reachable:
            action_res = await cl.AskActionMessage(
                content=(
                    f"Ollama is unreachable at {_cfg.ollama_base_url}. "
                    "Fall back to a cloud provider, or abort?"
                ),
                actions=[
                    cl.Action(name="fallback", label="Fall back to cloud", payload={"choice": "fallback"}),
                    cl.Action(name="abort", label="Abort session", payload={"choice": "abort"}),
                ],
            ).send()
            choice = (action_res.get("payload", {}) if action_res else {}).get("choice", "abort")
            if choice == "fallback":
                import os as _os
                _os.environ.pop("PROVIDER", None)
                _cfg = get_provider_config()
                await cl.Message(content=f"Switched provider. {provider_banner(_cfg)}").send()
            else:
                await cl.Message(content="Session aborted. Start Ollama and refresh.").send()
                return
        else:
            missing = get_missing_models(_cfg, pulled_models)
            if missing:
                pull_cmds = "\n".join(f"  ollama pull {m}" for m in missing)
                await cl.Message(
                    content=f"Required models not pulled. Run:\n```\n{pull_cmds}\n```\nThen refresh."
                ).send()
                return


async def handle_file_uploads(message: cl.Message):
    """Process any files attached to a message, saving them to the workspace."""
    from pydantic_ai.messages import ModelRequest, UserPromptPart
    import datetime

    elements = message.elements or []
    file_elements = [e for e in elements if isinstance(e, cl.File)]
    if not file_elements:
        return

    workspace_path = "./workspace"
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)

    history = cl.user_session.get("history", [])
    session_id = cl.user_session.get("session_id")

    for file in file_elements:
        target_path = os.path.join(workspace_path, file.name)
        if file.path and os.path.exists(file.path):
            import shutil
            shutil.copy2(file.path, target_path)
        elif file.content:
            with open(target_path, "wb") as f:
                f.write(file.content)

        await cl.Message(content=f"Uploaded `{file.name}` to `/workspace/{file.name}`").send()

        upload_notification = ModelRequest(parts=[
            UserPromptPart(
                content=f"[SYSTEM NOTIFICATION] User uploaded a file: {file.name}. It is now available at /workspace/{file.name}",
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
        ])
        history.append(upload_notification)
        new_msgs = adapter.dump_python([upload_notification], mode='json')
        await db.save_messages(session_id, new_msgs)

    cl.user_session.set("history", history)

async def send_file_diff(old_snapshot):
    new_snapshot = get_workspace_snapshot()
    diff = get_workspace_diff(old_snapshot, new_snapshot)
    if diff:
        elements = [
            cl.File(name=f, path=f"./workspace/{f}", display="inline")
            for f in sorted(list(diff))
        ]
        await cl.Message(content="Files created or modified:", elements=elements).send()

@cl.on_message
async def on_message(message: cl.Message):
    await handle_file_uploads(message)

    if message.content == "/files":
        files = list_workspace_files()
        if not files:
            await cl.Message(content="No files in workspace.").send()
            return
        
        elements = [
            cl.File(name=f, path=f"./workspace/{f}", display="inline")
            for f in sorted(files)
        ]
        await cl.Message(content="Current workspace files:", elements=elements).send()
        return

    session_id = cl.user_session.get("session_id")
    history = cl.user_session.get("history", [])
    
    # Take a snapshot before execution
    old_snapshot = get_workspace_snapshot()
    
    # Create an empty message to stream content into
    msg = cl.Message(content="")
    
    try:
        # Use AgentDeps even if not strictly needed here for the first call
        deps = AgentDeps()
        
        async with ironclaw_agent.run_stream(
            message.content,
            message_history=history,
            deps=deps
        ) as result:
            # Stream text tokens if the response is plain text.
            # For structured outputs (CodeExecutionRequest) stream_text() raises,
            # so we catch and fall through to handle via result.output below.
            try:
                async for text in result.stream_text(debounce_by=0.01):
                    await msg.stream_token(text)
            except Exception:
                pass  # structured output — handled via result.output below
            
            if msg.content:
                await msg.send()
            
            # Wait for the full data to be ready (could be CodeExecutionRequest)
            response = await result.get_output()
            
            # Save new messages
            new_msgs = adapter.dump_python(result.new_messages(), mode='json')
            await db.save_messages(session_id, new_msgs)
            
            # Update local history
            history = result.all_messages()
            cl.user_session.set("history", history)
            
            if isinstance(response, CodeExecutionRequest):
                await handle_code_approval(response, msg, history, session_id, old_snapshot)
            else:
                if not msg.content:
                    # If nothing was streamed but we have data, send it now
                    msg.content = str(response)
                    await msg.send()
                
                # Check for file changes if no code approval was needed
                await send_file_diff(old_snapshot)
            
    except Exception as e:
        if not msg.content:
            msg.content = f"Error: {str(e)}"
            await msg.send()
        else:
            await cl.Message(content=f"\n\nError: {str(e)}").send()

async def handle_code_approval(request: CodeExecutionRequest, original_msg: cl.Message, history, session_id, old_snapshot=None):
    # Display reasoning
    # If original_msg already has content from streaming, we might want to append or use a new message
    content = f"""**Agent Logic:** {request.reasoning}

**Proposed Code:**"""
    
    if original_msg.content:
        approval_msg = cl.Message(content=content)
        await approval_msg.send()
    else:
        original_msg.content = content
        await original_msg.send()
        approval_msg = original_msg
    
    # Show code blocks as separate messages or combined
    code_content = ""
    for block in request.blocks:
        code_content += f"""```{block.language}
{block.code}
```
"""
    
    await cl.Message(content=code_content, parent_id=approval_msg.id).send()
    
    # Ask for approval via actions
    res = await cl.AskActionMessage(
        content="Approve execution in the sandboxed environment?",
        actions=[
            cl.Action(name="approve", value="yes", label="✅ Approve"),
            cl.Action(name="reject", value="no", label="❌ Reject", button_variant="danger"),
        ],
    ).send()

    if res and res.get("value") == "yes":
        # Create a step for execution logs
        async with cl.Step(name="Docker Execution") as step:
            def on_output(content: str):
                cl.run_sync(step.stream_token(content))

            deps = AgentDeps(on_output=on_output)
            
            async with ironclaw_agent.run_stream(
                "Confirm the execution.",
                message_history=history,
                deps=deps
            ) as result:
                # Stream the final response (likely the same output or a summary)
                response_msg = cl.Message(content="")
                try:
                    async for text in result.stream_text(debounce_by=0.01):
                        await response_msg.stream_token(text)
                except Exception:
                    pass
                
                if response_msg.content:
                    await response_msg.send()
                
                # After streaming is done, get full data
                confirm_result_data = await result.get_output()
                
                # Save confirmation messages
                confirm_new_msgs = adapter.dump_python(result.new_messages(), mode='json')
                await db.save_messages(session_id, confirm_new_msgs)
                
                # Update history
                history = result.all_messages()
                cl.user_session.set("history", history)
                
                if not response_msg.content:
                    response_msg.content = f"**Execution Result:**\n{confirm_result_data}"
                    await response_msg.send()
                
                # Check for file changes after execution
                if old_snapshot:
                    await send_file_diff(old_snapshot)
    else:
        await cl.Message(content="Execution cancelled by user.").send()
