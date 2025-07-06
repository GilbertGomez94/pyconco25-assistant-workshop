from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from smart_assistant.services.expenses_service import build_financial_plan
from smart_assistant.db import get_db

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post(
    "/plan",
    summary="Genera y guarda un plan financiero",
    status_code=200,
)
async def financial_plan(
    file: UploadFile = File(..., description="CSV con transacciones"),
    goal: str = Form(..., description="Meta del usuario"),
    db: Session = Depends(get_db),
):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=415, detail="El archivo debe ser CSV")

    plan_json = build_financial_plan(await file.read(), goal, db)
    return plan_json
