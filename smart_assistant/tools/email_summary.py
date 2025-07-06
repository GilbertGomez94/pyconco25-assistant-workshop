from datetime import date
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from smart_assistant.services.emailer_service import send_email

_llm_summary = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


@tool(
    "EmailSummaryTool",
    description=(
        "Envía por correo un resumen (≤800 palabras) de los resultados de Tavily.\n"
        "Params:\n  user_email: str\n  raw_results: str"
    ),
)
def email_summary_tool(user_email: str, raw_results: str) -> str:
    try:
        summary = _llm_summary.invoke(
            f"Hoy es {date.today()}. Resume en español (máx. 200 palabras):\n\n{raw_results}"
        ).content
        send_email(
            to_email=user_email,
            subject="🗞 Tu resumen de noticias",
            body=f"Hola,\n\nAquí tienes tu resumen:\n\n{summary}\n\n— Tu asistente",
        )
        return "📧 Correo enviado."
    except Exception as exc:      # pragma: no cover
        return f"❌ Error enviando correo: {exc}"
