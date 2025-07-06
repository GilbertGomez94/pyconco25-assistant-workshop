from langchain_core.tools import tool
from smart_assistant.db import SessionLocal
from smart_assistant.models.data import Interaction
from smart_assistant.services.memory_service import store_embedding


@tool("DataStoreTool", description="Persiste input y output + embedding.")
def datastore_tool(user_input: str, tool_name: str, tool_output: str) -> str:
    db = SessionLocal()
    try:
        row = Interaction(user_input=user_input, tool_name=tool_name, tool_output=tool_output)
        db.add(row)
        db.commit()
        db.refresh(row)
        store_embedding(row.id, user_input)
        return f"✅ Guardado con id={row.id}"
    except Exception as exc:
        db.rollback()
        return f"❌ Error guardando: {exc}"
    finally:
        db.close()
