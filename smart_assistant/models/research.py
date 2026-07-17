from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=4, example="foundation models healthcare")
    max_results: int = Field(5, ge=1, le=20)


class ResearchResponse(BaseModel):
    executive_summary: str
