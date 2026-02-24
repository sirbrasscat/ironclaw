import pytest
import pytest_asyncio
import os
import asyncio
from src.database.manager import DatabaseManager
from src.database.models import Base

@pytest_asyncio.fixture
async def db_manager():
    # Use a test database
    db_path = "test_ironclaw.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"
    manager = DatabaseManager(db_url)
    await manager.initialize_db()
    yield manager
    await manager.close()
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.mark.asyncio
async def test_session_creation(db_manager):
    session_id = await db_manager.get_or_create_session()
    assert session_id is not None
    assert isinstance(session_id, str)

    # Test retrieval
    retrieved_id = await db_manager.get_or_create_session(session_id)
    assert retrieved_id == session_id

@pytest.mark.asyncio
async def test_message_persistence(db_manager):
    session_id = await db_manager.get_or_create_session()
    
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "model", "content": "Hi there!"}
    ]
    
    await db_manager.save_messages(session_id, messages)
    
    retrieved_messages = await db_manager.get_messages(session_id)
    assert len(retrieved_messages) == 2
    assert retrieved_messages[0]["role"] == "user"
    assert retrieved_messages[1]["role"] == "model"
    assert retrieved_messages[0]["content"] == "Hello"

@pytest.mark.asyncio
async def test_multiple_sessions(db_manager):
    s1 = await db_manager.get_or_create_session()
    s2 = await db_manager.get_or_create_session()
    assert s1 != s2
    
    await db_manager.save_messages(s1, [{"role": "user", "content": "S1"}])
    await db_manager.save_messages(s2, [{"role": "user", "content": "S2"}])
    
    m1 = await db_manager.get_messages(s1)
    m2 = await db_manager.get_messages(s2)
    
    assert len(m1) == 1
    assert m1[0]["content"] == "S1"
    assert len(m2) == 1
    assert m2[0]["content"] == "S2"
