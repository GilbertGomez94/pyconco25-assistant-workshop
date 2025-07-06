"""
Busca titulares con Tavily y envía un resumen por correo.
"""
from datetime import date
from typing import List

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from tavily import TavilyClient  # 📦  pip install tavily-python
from smart_assistant.deps import get_settings
from smart_assistant.services.emailer_service import send_email


def _fetch_headlines(topics: List[str], max_results: int = 10) -> List[dict]:
    cfg = get_settings()
    client = TavilyClient(api_key=cfg.tavily_api_key)

    combined_query = " OR ".join(topics)
    # El SDK devuelve una lista de dicts con title, url y content :contentReference[oaicite:1]{index=1}
    response = client.search(
        query=combined_query,
        num_results=max_results,
        search_depth="medium",
        include_domains=None,
        include_answer=False,
    )
    return response["results"]  # type: ignore[attr-defined]


def build_and_send_summary(
    topics: List[str],
    to_email: str,
    llm_model: str = "gpt-4o",
    max_results: int = 10,
) -> None:
    articles = _fetch_headlines(topics, max_results)

    bullet_list = "\n".join(f"- {a['title']} ({a['url']})" for a in articles)

    llm = ChatOpenAI(model=llm_model, temperature=0.3)
    summary = llm.invoke(
        [
            SystemMessage(
                content=(
                    "Hoy es " + str(date.today()) + ". "
                    "Resume en español, máx. 200 palabras, los siguientes titulares:\n\n"
                    + bullet_list
                )
            )
        ]
    ).content

    body = f"Hola,\n\nAquí tienes tu resumen de noticias:\n\n{summary}\n\n— Tu asistente"
    send_email(to_email, subject="🗞 Tu resumen de noticias", body=body)
