"""
Chainlit UI (≥ 2.5.5) para la Smart Assistant API.

* Ejecuta:  chainlit run chainlit_app.py
* La API FastAPI debe estar levantada en http://localhost:9000
"""
from __future__ import annotations

import io, httpx, chainlit as cl

API_URL = "http://localhost:9000/v1"

# --------------------------------------------------------------------- #
async def post_form(endpoint: str, data: dict, files: dict | None = None):
    async with httpx.AsyncClient(timeout=90) as client:
        res = await client.post(f"{API_URL}{endpoint}", data=data, files=files)
        res.raise_for_status()
        return res.json()

async def post_json(endpoint: str, data: dict):
    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.post(f"{API_URL}{endpoint}", json=data)
        res.raise_for_status()
        return res.json()

# --------------------------------------------------------------------- #
COMMANDS = [
    {"id": "gastos",    "icon": "wallet",    "description": "Analizar CSV de gastos"},
    {"id": "noticias",  "icon": "newspaper", "description": "Resumen diario de noticias"},
    {"id": "papers",    "icon": "book-open", "description": "Buscar artículos académicos"},
    {"id": "correo",    "icon": "mail",      "description": "Configurar correo"},
]

# --------------------------------------------------------------------- #
@cl.on_chat_start
async def start():
    await cl.context.emitter.set_commands(COMMANDS)
    # Estado inicial de la sesión
    cl.user_session.set("mode", None)         # puede ser 'assistant' o None
    cl.user_session.set("user_email", None)
    await cl.Message(
        "👋 Selecciona un comando con los botones o escribe su nombre.\n"
        "Puedes configurar tu correo en cualquier momento con el comando **correo**."
    ).send()

# --------------------------------------------------------------------- #
async def _require_email() -> str:
    """Devuelve el e‑mail de sesión; si no existe, lo solicita al usuario."""
    if not cl.user_session.get("user_email"):
        email_msg = await cl.AskUserMessage("📧 Escribe tu correo:").send()
        cl.user_session.set("user_email", email_msg["output"])
    return cl.user_session.get("user_email")

# --------------------------------------------------------------------- #
@cl.on_message
async def main(msg: cl.Message):
    cmd = msg.command or msg.content.strip().lower()
    mode = cl.user_session.get("mode")

    # -------------------- COMANDOS EXPLÍCITOS -------------------------- #
    # 1) Cambiar correo
    if cmd == "correo":
        email_msg = await cl.AskUserMessage("✉️ Nuevo correo:").send()
        cl.user_session.set("user_email", email_msg["output"])
        await cl.Message("✅ Correo actualizado.").send()
        return

    
    # 3) GASTOS --------------------------------------------------------- #
    if cmd == "gastos":
        file_msg = await cl.AskFileMessage(
            prompt="📂 Sube el CSV de transacciones",
            accept=["text/csv"],
            max_size_mb=2,
        ).send()
        goal_msg = await cl.AskUserMessage("🏁 ¿Cuál es tu meta financiera?").send()

        resp = await post_form(
            "/expenses/plan",
            data={"goal": goal_msg["output"]},
            files={"file": ("tx.csv", io.BytesIO(file_msg["files"][0].content), "text/csv")},
        )
        await cl.Message(
            f"💡 **Plan mensual**\n\n{resp['monthly_plan']}\n\n"
            f"**Gasto promedio:** ${resp['monthly_spend_average']:,.2f}\n"
            f"**Ingreso promedio:** ${resp['monthly_earnings_average']:,.2f}"
        ).send()
        return

    # 4) NOTICIAS ------------------------------------------------------- #
    if cmd == "noticias":
        topics_msg = await cl.AskUserMessage("📝 Temas (separa con comas):").send()
        user_email = await _require_email()
        await post_json(
            "/news/summary",
            {"topics": [t.strip() for t in topics_msg["output"].split(",")], "email": user_email},
        )
        await cl.Message("✅ Resumen enviado. ¡Revisa tu bandeja!").send()
        return

    # 5) PAPERS --------------------------------------------------------- #
    if cmd == "papers":
        query_msg = await cl.AskUserMessage("🔍 Consulta académica:").send()
        data = await post_json("/research/search", {"query": query_msg["output"], "max_results": 5})
        await cl.Message(data["executive_summary"]).send()
        return


    # -------------------- Fallback ------------------------------------ #
    await cl.Message(
        "❓ Comando no reconocido. Usa los botones o escribe uno de: "
        "`asistente`, `gastos`, `noticias`, `papers`, `correo`."
    ).send()
