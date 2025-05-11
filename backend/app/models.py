from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, JSON,
    ForeignKey, Index, func
)
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

# --- Task Model ---
class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    model_used = Column(String, nullable=False)
    generated_code = Column(Text, nullable=True)

    status = Column(String, nullable=False, default="pending", index=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)

# --- Plugin Execution Model ---
class PluginExecution(Base):
    __tablename__ = "plugin_executions"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    plugin_name = Column(String, nullable=False, index=True)

    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)

    status = Column(String, nullable=False, default="pending", index=True)
    error_message = Column(Text, nullable=True)

    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)

# --- Memory Ledger Model ---
class MemoryLedger(Base):
    __tablename__ = "memory_ledger"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    context_type = Column(String, nullable=False, index=True)
    related_id = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)

    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

# --- Project Model ---
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    understanding = Column(Text, nullable=True)  # ✅ new column
    created_at = Column(DateTime, default=datetime.utcnow)

    chats = relationship(
        "Chat",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",  # ✅ optimized lazy loading for ORM joins
    )

# --- Chat Model ---
class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="chats")
    messages = relationship(
        "ChatMessage",
        back_populates="chat",
        cascade="all, delete-orphan",
        lazy="selectin",  # ✅ same pattern for nested chat→messages
    )

# --- Chat Message Model ---
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    role = Column(String, nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    chat = relationship("Chat", back_populates="messages")