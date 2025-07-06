from fastapi import APIRouter
from smart_assistant.models.research import ResearchRequest, ResearchResponse
from smart_assistant.services.research_service import literature_search

router = APIRouter(prefix="/research", tags=["research"])


@router.post("/search", response_model=ResearchResponse)
async def research(payload: ResearchRequest):
    print(payload)
    summary = literature_search(payload.query, payload.max_results)
    return ResearchResponse(executive_summary=summary)
