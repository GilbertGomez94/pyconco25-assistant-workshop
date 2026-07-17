from pydantic import BaseModel, Field, PositiveFloat


class ExpenseAnalysisResponse(BaseModel):
    summary_markdown: str = Field(..., description="Tabla + sugerencias en Markdown")



class FinancialPlanLLM(BaseModel):
    monthly_spend_average: PositiveFloat = Field(..., description="USD gastados al mes")
    monthly_earnings_average: PositiveFloat = Field(..., description="USD ingresados al mes")
    monthly_plan: str = Field(..., description="Consejos y plan de acción, debes ser congruente con el monthly_spend_average y el monthly_earnings_average, decir en cuanto tiempo aproximadamente lograría su meta con tus consejos")
