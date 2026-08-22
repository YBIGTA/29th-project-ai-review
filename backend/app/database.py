from __future__ import annotations

import os
from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


def database_url() -> str | None:
    url = os.getenv("DATABASE_URL")
    if url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def get_engine():
    url = database_url()
    if not url:
        raise RuntimeError("DATABASE_URL이 설정되지 않았습니다.")
    return create_engine(url, pool_pre_ping=True)


@contextmanager
def get_session() -> Iterator[Session]:
    session = sessionmaker(bind=get_engine(), expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()


def create_tables() -> None:
    Base.metadata.create_all(get_engine())
