from contextlib import contextmanager
from datetime import date, datetime, timedelta
from typing import Generator

from sqlalchemy import (
    create_engine,
    Column,
    Date,
    DateTime,
    Numeric,
    Text,
    func,
    String
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)
from decimal import Decimal


from smart_assistant.deps import get_settings

# ---------- engine & sesión ----------------------------------------------- #
cfg = get_settings()
engine = create_engine(cfg.postgres_database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()


# ---------- ORM ------------------------------------------------------------ #
class Base(DeclarativeBase): ...
