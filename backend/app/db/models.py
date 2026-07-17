"""
db/models.py
────────────
SQLAlchemy ORM models for PostgreSQL.
All 9 tables: Users, Sessions, Uploads, Chats, ChatMessages,
AgentLogs, EvaluationRuns, EvaluationResults, Feedback.

create_all() is called on app startup — no Alembic for hackathon.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, JSON, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


# ──────────────────────────────────────────────────────────────
#  Users
# ──────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id          = Column(String, primary_key=True, default=_uuid)
    email       = Column(String, unique=True, nullable=False, index=True)
    role        = Column(String, nullable=False, default="viewer")   # viewer | analyst | admin
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime(timezone=True), default=_utcnow)

    sessions    = relationship("Session", back_populates="user")
    chats       = relationship("Chat", back_populates="user")
    feedback    = relationship("Feedback", back_populates="user")


# ──────────────────────────────────────────────────────────────
#  Sessions
# ──────────────────────────────────────────────────────────────

class Session(Base):
    __tablename__ = "sessions"

    id          = Column(String, primary_key=True, default=_uuid)
    user_id     = Column(String, ForeignKey("users.id"), nullable=False)
    token       = Column(String, unique=True, nullable=False)
    expires_at  = Column(DateTime(timezone=True), nullable=False)
    created_at  = Column(DateTime(timezone=True), default=_utcnow)

    user        = relationship("User", back_populates="sessions")


# ──────────────────────────────────────────────────────────────
#  Uploads  (document ingestion tracking)
# ──────────────────────────────────────────────────────────────

class Upload(Base):
    __tablename__ = "uploads"

    id                  = Column(String, primary_key=True, default=_uuid)
    job_id              = Column(String, unique=True, nullable=False, index=True)
    doc_id              = Column(String, unique=True, nullable=False, index=True)
    filename            = Column(String, nullable=False)
    doc_type            = Column(String, nullable=False)
    status              = Column(String, nullable=False, default="queued")
    pipeline_stage      = Column(String, nullable=True)
    entities_extracted  = Column(Integer, nullable=True)
    nodes_created       = Column(Integer, nullable=True)
    chunks_embedded     = Column(Integer, nullable=True)
    parse_confidence    = Column(Float, nullable=True)
    error_message       = Column(Text, nullable=True)
    created_at          = Column(DateTime(timezone=True), default=_utcnow)
    completed_at        = Column(DateTime(timezone=True), nullable=True)


# ──────────────────────────────────────────────────────────────
#  Chats
# ──────────────────────────────────────────────────────────────

class Chat(Base):
    __tablename__ = "chats"

    id          = Column(String, primary_key=True, default=_uuid)
    user_id     = Column(String, ForeignKey("users.id"), nullable=True)
    title       = Column(String, nullable=True)
    created_at  = Column(DateTime(timezone=True), default=_utcnow)

    user        = relationship("User", back_populates="chats")
    messages    = relationship("ChatMessage", back_populates="chat")


# ──────────────────────────────────────────────────────────────
#  Chat Messages
# ──────────────────────────────────────────────────────────────

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id              = Column(String, primary_key=True, default=_uuid)
    chat_id         = Column(String, ForeignKey("chats.id"), nullable=False)
    role            = Column(String, nullable=False)   # "user" | "assistant"
    content         = Column(Text, nullable=False)
    confidence      = Column(Float, nullable=True)
    citations_json  = Column(JSON, nullable=True)      # list of Citation dicts
    graph_paths_json = Column(JSON, nullable=True)     # list of GraphPath dicts
    response_ms     = Column(Float, nullable=True)
    created_at      = Column(DateTime(timezone=True), default=_utcnow)

    chat            = relationship("Chat", back_populates="messages")
    feedback        = relationship("Feedback", back_populates="message")


# ──────────────────────────────────────────────────────────────
#  Agent Logs
# ──────────────────────────────────────────────────────────────

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id              = Column(String, primary_key=True, default=_uuid)
    agent_type      = Column(String, nullable=False)   # rca | compliance | lessons
    input_json      = Column(JSON, nullable=False)
    output_json     = Column(JSON, nullable=True)
    duration_ms     = Column(Float, nullable=True)
    error_message   = Column(Text, nullable=True)
    llm_model       = Column(String, nullable=True)
    created_at      = Column(DateTime(timezone=True), default=_utcnow)


# ──────────────────────────────────────────────────────────────
#  Evaluation Runs
# ──────────────────────────────────────────────────────────────

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id              = Column(String, primary_key=True, default=_uuid)
    run_at          = Column(DateTime(timezone=True), default=_utcnow)
    question_count  = Column(Integer, nullable=False)
    llm_provider    = Column(String, nullable=True)
    llm_model       = Column(String, nullable=True)
    summary_json    = Column(JSON, nullable=True)   # aggregate metrics

    results         = relationship("EvaluationResult", back_populates="run")


# ──────────────────────────────────────────────────────────────
#  Evaluation Results  (per-question)
# ──────────────────────────────────────────────────────────────

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id              = Column(String, primary_key=True, default=_uuid)
    run_id          = Column(String, ForeignKey("evaluation_runs.id"), nullable=False)
    question_id     = Column(String, nullable=False)
    question        = Column(Text, nullable=False)
    answer          = Column(Text, nullable=True)
    is_correct      = Column(Boolean, nullable=True)
    metrics_json    = Column(JSON, nullable=True)   # per-question metric values
    response_ms     = Column(Float, nullable=True)
    created_at      = Column(DateTime(timezone=True), default=_utcnow)

    run             = relationship("EvaluationRun", back_populates="results")


# ──────────────────────────────────────────────────────────────
#  Feedback
# ──────────────────────────────────────────────────────────────

class Feedback(Base):
    __tablename__ = "feedback"

    id          = Column(String, primary_key=True, default=_uuid)
    message_id  = Column(String, ForeignKey("chat_messages.id"), nullable=False)
    user_id     = Column(String, ForeignKey("users.id"), nullable=True)
    rating      = Column(Integer, nullable=False)   # 1–5
    comment     = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), default=_utcnow)

    message     = relationship("ChatMessage", back_populates="feedback")
    user        = relationship("User", back_populates="feedback")
