from typing import List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from src.database.models import Base, ChatSession, ChatMessage
from datetime import datetime, timezone

class DatabaseManager:
    def __init__(self, db_url: str = "sqlite+aiosqlite:///ironclaw.db"):
        self.engine = create_async_engine(db_url)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def initialize_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """
        Retrieves an existing session or creates a new one.
        Returns the session ID.
        """
        async with self.async_session() as session:
            if session_id:
                result = await session.execute(select(ChatSession).where(ChatSession.id == session_id))
                chat_session = result.scalar_one_or_none()
                if chat_session:
                    return chat_session.id
            
            # Create new session
            new_session = ChatSession(id=session_id) if session_id else ChatSession()
            session.add(new_session)
            await session.commit()
            await session.refresh(new_session)
            return new_session.id

    async def save_messages(self, session_id: str, messages: List[dict]):
        """
        Saves a list of messages (as dicts) to the database.
        """
        async with self.async_session() as session:
            for msg_data in messages:
                # Pydantic AI ModelMessage has a 'role' attribute or key
                role = msg_data.get('role', 'unknown')
                db_msg = ChatMessage(
                    session_id=session_id,
                    role=role,
                    content=msg_data,
                    timestamp=datetime.now(timezone.utc)
                )
                session.add(db_msg)
            await session.commit()

    async def get_messages(self, session_id: str) -> List[dict]:
        """
        Retrieves all messages for a session in chronological order.
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.timestamp)
            )
            messages = result.scalars().all()
            return [msg.content for msg in messages]

    async def close(self):
        await self.engine.dispose()
