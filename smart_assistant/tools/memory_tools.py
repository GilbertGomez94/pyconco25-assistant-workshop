from langchain_core.tools import tool
from smart_assistant.services.memory_service import recall_history, get_financial_context


@tool(
    "RecallMemoryTool",
    description="Devuelve interacciones pasadas similares al texto de la consulta.",
)
def recall_memory_tool(query: str) -> str:
    msgs = recall_history(query)
    return "\n\n".join(msgs) if msgs else "No hay historial relevante."


@tool(
    "FinancialContextTool",
    description="Devuelve el plan financiero vigente si existe.",
)
def financial_context_tool() -> str:
    ctx = get_financial_context()
    return ctx if ctx else "No hay ningún plan financiero guardado."
