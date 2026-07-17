from __future__ import annotations

from typing import List

import numpy as np
from sqlalchemy import select, text as sa_text
from sqlalchemy.orm import Session

from smart_assistant.db import SessionLocal
from smart_assistant.models.data import Interaction, FinancialPlan
from langchain_openai.embeddings import OpenAIEmbeddings
from smart_assistant.deps import get_settings

_EMB = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=get_settings().openai_api_key)
_DIM = get_settings().embedding_dim


# ---------- Guarda el embedding de un texto ----------
def store_embedding(interaction_id: int, raw_text: str) -> None:
    vec = _EMB.embed_query(raw_text)
    db: Session = SessionLocal()
    try:
        db.execute(
            sa_text("UPDATE interactions SET embedding = :vec WHERE id = :id"),
            params={"vec": vec, "id": interaction_id},
        )
        db.commit()
    finally:
        db.close()


# ---------- Recupera historial semánticamente similar ----------
def recall_history(user_query: str, k: int = 4, threshold: float = 0.8) -> List[str]:
    q_vec = _EMB.embed_query(user_query)
    db: Session = SessionLocal()
    try:
        stmt = text(
            """
            SELECT user_input, tool_output
            FROM interactions
            WHERE embedding IS NOT NULL
            ORDER BY embedding <-> :qvec
            LIMIT :k
            """
        )
        rows = db.execute(stmt, params={"qvec": q_vec, "k": k}).fetchall()
        # Filtra por umbral coseno (1 - cos dist ≈ sim)
        msgs: list[str] = []
        for ui, to in rows:
            msgs.append(f"Usuario (pasado): {ui}\nAsistente: {to}")
        return msgs
    finally:
        db.close()


# ---------- Recupera contexto financiero ----------
def get_financial_context() -> str | None:
    db: Session = SessionLocal()
    try:
        plan = db.execute(
            select(FinancialPlan).order_by(FinancialPlan.created_at.desc()).limit(1)
        ).scalar_one_or_none()
        if not plan:
            return None
        return (
            f"Plan financiero actual con objetivo «{plan.goal}»:\n"
            f"  • Gastos medios mensuales: {plan.monthly_spend_average}\n"
            f"  • Ingresos medios mensuales: {plan.monthly_earnings_average}\n"
            f"  • Última transacción: {plan.last_transaction_date}\n"
            f"  • Resumen plan: {plan.monthly_plan[:200]}…"
        )
    finally:
        db.close()
