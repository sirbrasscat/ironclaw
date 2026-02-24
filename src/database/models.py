from datetime import datetime, timezone
import uuid
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.timestamp"
    )

    def __repr__(self) -> str:
        return f"ChatSession(id={self.id!r}, created_at={self.created_at!r})"

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"))
    role: Mapped[str] = mapped_column(String(20))  # 'user', 'model', 'system', 'tool'
    content: Mapped[dict] = mapped_column(JSON)  # Store Pydantic AI ModelMessage blobs
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"ChatMessage(id={self.id!r}, role={self.role!r}, timestamp={self.timestamp!r})"
