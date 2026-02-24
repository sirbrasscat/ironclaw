import os
import sys
from typing import Union

# Ensure project root is in sys.path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import chainlit as cl
from dotenv import load_dotenv
from pydantic import TypeAdapter
from pydantic_ai.messages import ModelMessage

from src.agent.core import ironclaw_agent, AgentDeps
from src.agent.tools.sandbox import CodeExecutionRequest
from src.database.manager import DatabaseManager

load_dotenv()

# Chainlit Auth
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    env_password = os.environ.get("CHAINLIT_PASSWORD", "ironclaw")
    if password == env_password:
        return cl.User(name=username)
    return None

# DB Manager
db = DatabaseManager()
adapter = TypeAdapter(list[ModelMessage])

@cl.on_chat_start
async def on_chat_start():
    # Ensure workspace directory exists
    if not os.path.exists("./workspace"):
        os.makedirs("./workspace")
    
    await db.initialize_db()
    
    user = cl.user_session.get("user")
    username = user.name if user else "default"
    
    # Persistence: Use a username-based session ID
    session_id = f"web-{username}"
    cl.user_session.set("session_id", session_id)
    
    await db.get_or_create_session(session_id)
    
    # Load history
    history_dicts = await db.get_messages(session_id)
    history = adapter.validate_python(history_dicts) if history_dicts else []
    cl.user_session.set("history", history)
    
    await cl.Message(content=f"Welcome {username}! IronClaw is ready.").send()

@cl.on_files
async def on_files(files: list[cl.File]):
    workspace_path = "./workspace"
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)

    for file in files:
        target_path = os.path.join(workspace_path, file.name)
        
        # Write the file content to the workspace
        with open(target_path, "wb") as f:
            if file.content:
                f.write(file.content)
            else:
                # If content is not pre-loaded, we might need to read it if it's on disk
                # In most cases for small files in Chainlit it's in .content
                pass
        
        # Notify the user
        await cl.Message(content=f"Uploaded `{file.name}` to `/workspace/{file.name}`").send()
        
        # Update agent history with the upload notification
        history = cl.user_session.get("history", [])
        from pydantic_ai.messages import ModelRequest, UserPromptPart
        import datetime
        
        upload_notification = ModelRequest(parts=[
            UserPromptPart(
                content=f"[SYSTEM NOTIFICATION] User uploaded a file: {file.name}. It is now available at /workspace/{file.name}",
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
        ])
        history.append(upload_notification)
        cl.user_session.set("history", history)
        
        # Persistence: Save the notification to DB
        session_id = cl.user_session.get("session_id")
        new_msgs = adapter.dump_python([upload_notification], mode='json')
        await db.save_messages(session_id, new_msgs)

@cl.on_message
async def on_message(message: cl.Message):
    session_id = cl.user_session.get("session_id")
    history = cl.user_session.get("history", [])
    
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
            # Stream the text as it arrives
            async for text in result.stream_text(debounce_by=0.01):
                await msg.stream_token(text)
            
            if msg.content:
                await msg.send()
            
            # Wait for the full data to be ready (could be CodeExecutionRequest)
            response = await result.output
            
            # Save new messages
            new_msgs = adapter.dump_python(result.new_messages(), mode='json')
            await db.save_messages(session_id, new_msgs)
            
            # Update local history
            history = result.all_messages()
            cl.user_session.set("history", history)
            
            if isinstance(response, CodeExecutionRequest):
                await handle_code_approval(response, msg, history, session_id)
            elif not msg.content:
                # If nothing was streamed but we have data, send it now
                msg.content = str(response)
                await msg.send()
            
    except Exception as e:
        if not msg.content:
            msg.content = f"Error: {str(e)}"
            await msg.send()
        else:
            await cl.Message(content=f"\n\nError: {str(e)}").send()

async def handle_code_approval(request: CodeExecutionRequest, original_msg: cl.Message, history, session_id):
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
                async for text in result.stream_text(debounce_by=0.01):
                    await response_msg.stream_token(text)
                
                if response_msg.content:
                    await response_msg.send()
                
                # After streaming is done, get full data
                confirm_result_data = await result.output
                
                # Save confirmation messages
                confirm_new_msgs = adapter.dump_python(result.new_messages(), mode='json')
                await db.save_messages(session_id, confirm_new_msgs)
                
                # Update history
                history = result.all_messages()
                cl.user_session.set("history", history)
                
                if not response_msg.content:
                    response_msg.content = f"**Execution Result:**\n{confirm_result_data}"
                    await response_msg.send()
    else:
        await cl.Message(content="Execution cancelled by user.").send()
