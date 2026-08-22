from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(100))
    profile_image_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class StudySession(Base):
    __tablename__ = "study_sessions"
    __table_args__ = (CheckConstraint("status IN ('created', 'processing', 'completed', 'failed')"), CheckConstraint("pass_status IN ('P', 'NP')"))
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lecture_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="created")
    pass_status: Mapped[str] = mapped_column(String(2), nullable=False, default="NP")
    hint_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class AudioFile(Base):
    __tablename__ = "audio_files"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("study_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer)
    duration_seconds: Mapped[float | None] = mapped_column(Numeric(10, 3))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Transcription(Base):
    __tablename__ = "transcriptions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("study_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    audio_file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("audio_files.id", ondelete="CASCADE"), unique=True, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_text: Mapped[str] = mapped_column(Text, nullable=False)
    stt_model: Mapped[str] = mapped_column(String(100), nullable=False)
    beam_size: Mapped[int] = mapped_column(Integer, nullable=False)
    correction_model: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Evaluation(Base):
    __tablename__ = "evaluations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("study_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    transcription_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transcriptions.id", ondelete="CASCADE"), unique=True, nullable=False)
    accuracy_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    coverage_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    structural_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    total_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    pass_status: Mapped[str] = mapped_column(String(2), nullable=False)
    evaluation_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
