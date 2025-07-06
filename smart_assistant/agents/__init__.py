from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from smart_assistant.tools.finance_file import finance_tool, is_finance_question
from smart_assistant.tools.tavily_search import tavily_search_tool
from smart_assistant.tools.academic_search import academic_search_tool
from smart_assistant.tools.email_summary import email_summary_tool
from smart_assistant.tools.memory_tools import recall_memory_tool, financial_context_tool
from smart_assistant.tools.datastore import datastore_tool
from smart_assistant.deps import get_settings

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=get_settings().openai_api_key)

_SYSTEM_PROMPT = """
Eres un asistente que puede razonar paso a paso y actuar usando herramientas.

Reglas de memoria:
1. Si decides usar FinanceCSVTool o la pregunta del usuario es sobre finanzas,
   llama primero a FinancialContextTool para recuperar el plan financiero.
2. En todos los demás casos, primero llama a RecallMemoryTool con el texto de la
   pregunta para obtener antecedentes relevantes.
3. Después de usar *cualquier* herramienta que produzca una respuesta para el
   usuario debes llamar a DataStoreTool con:
      - user_input  : la pregunta original
      - tool_name   : el nombre literal de la tool que usaste
      - tool_output : la salida que devolvió la tool
4. Si usas TavilySearch, inmediatamente después llama a EmailSummaryTool con
   user_email (mensaje con nombre 'user_email') y raw_results = salida Tavily y 
   finalmente debes llamar a DataStoreTool con:
   - user_input  : la pregunta original
   - tool_name   : el nombre literal de la tool que usaste
   - tool_output : la salida que devolvió la tool.
5. Responde al usuario únicamente cuando hayas completado las llamadas que
   toque según estas reglas.
"""

_ALL_TOOLS = [
    finance_tool,
    tavily_search_tool,
    academic_search_tool,
    recall_memory_tool,
    financial_context_tool,
    email_summary_tool,
    datastore_tool,
]


def build_agent():
    return create_react_agent(
        model=_llm,
        tools=_ALL_TOOLS,
        prompt=_SYSTEM_PROMPT,
        debug=True,
        name="assistant",
    )
