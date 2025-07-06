from fastapi import APIRouter, HTTPException
from smart_assistant.models.news import NewsSummaryRequest, NewsSummaryResponse
from smart_assistant.services.news_service import build_and_send_summary

router = APIRouter(prefix="/news", tags=["news"])


@router.post("/summary", response_model=NewsSummaryResponse, status_code=202)
async def news_summary(payload: NewsSummaryRequest):
    try:
        build_and_send_summary(payload.topics, payload.email)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return NewsSummaryResponse(message="Resumen en proceso de envío")
