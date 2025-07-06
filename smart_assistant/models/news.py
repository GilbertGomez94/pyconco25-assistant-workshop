from pydantic import BaseModel, Field


class NewsSummaryRequest(BaseModel):
    topics: list[str] = Field(..., min_length=1)
    email: str = Field(..., pattern=r".+@.+\..+")


class NewsSummaryResponse(BaseModel):
    message: str = Field(..., example="Resumen enviado correctamente")
