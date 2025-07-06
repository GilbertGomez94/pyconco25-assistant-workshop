# smart_assistant/routers/assistant.py
from __future__ import annotations

import io
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session

from smart_assistant.agents import build_agent
from smart_assistant.tools.finance_file import set_finance_df
from smart_assistant.db import get_db

router = APIRouter(prefix="/assistant", tags=["assistant"])

# ← Una única instancia del agente para todo el proceso
agent = build_agent()


@router.post(
    "",
    summary="Chat con el agente inteligente",
    status_code=200,
)
async def chat_with_agent(
    input: str = Form(..., description="Mensaje del usuario"),
    email: str = Form(..., description="Correo del usuario"),
    file: UploadFile | None = File(
        None,
        description="(Opcional) CSV con transacciones; se cargará en memoria.",
    ),
    db: Session = Depends(get_db),  # por coherencia con tu patrón, aunque no se usa aquí
):
    """
    End‑point central del asistente.  
    - Acepta un `input` libre.  
    - Requiere `email` (para EmailSummaryTool).  
    - Opcionalmente un CSV financiero; se carga a FinanceCSVTool.
    """
    if file:
        if file.content_type != "text/csv":
            raise HTTPException(status_code=415, detail="El archivo debe ser CSV")
        set_finance_df(pd.read_csv(io.BytesIO(await file.read())))

    # ------------ Construimos el prompt -------------
    chat_messages = [
        {"role": "system", "name": "user_email", "content": email},
        {"role": "user", "content": input},
    ]

    result = agent.invoke({"messages": chat_messages})
    last = result["messages"][-1] if result.get("messages") else {}
    return {"response": last.content}
