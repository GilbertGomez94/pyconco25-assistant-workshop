from datetime import datetime, date, timedelta
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Numeric, func
from pgvector.sqlalchemy import Vector

from smart_assistant.db import Base


# ----------- Memoria conversacional -------------
class Interaction(Base):
    __tablename__ = "interactions"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_input  = Column(Text,    nullable=False)
    tool_name   = Column(String,  nullable=False)
    tool_output = Column(Text,    nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    embedding   = Column(Vector(dim=1536), nullable=True)  # pgvector

# ----------- Plan financiero -------------
class FinancialPlan(Base):
    __tablename__ = "financial_plans"

    id                       = Column(Integer, primary_key=True, autoincrement=True)
    monthly_spend_average    = Column(Numeric(14, 2), nullable=False)
    monthly_earnings_average = Column(Numeric(14, 2), nullable=False)
    monthly_plan             = Column(Text, nullable=False)

    last_transaction_date    = Column(Date, nullable=False)
    first_revision           = Column(Date, nullable=False)
    goal                     = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

# ---------- util para fecha de primera revisión --------------------------- #
def first_revision_date() -> datetime.date:
    return (datetime.utcnow() + timedelta(days=7)).date()
