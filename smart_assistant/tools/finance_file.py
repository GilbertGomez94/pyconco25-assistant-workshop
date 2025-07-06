from langchain_core.tools import tool
import pandas as pd

_FINANCE_DF: pd.DataFrame | None = None
FINANCE_KEYWORDS = {
    "gasto", "gastos", "ingreso", "ingresos", "balance", "ahorro", "finanzas",
    "plan", "presupuesto", "earnings", "spend"
}


def set_finance_df(df: pd.DataFrame) -> None:
    global _FINANCE_DF
    _FINANCE_DF = df


def is_finance_question(text: str) -> bool:
    return any(k in text.lower() for k in FINANCE_KEYWORDS)


@tool("FinanceCSVTool", description="Consulta los datos financieros subidos en CSV.")
def finance_tool(query: str) -> str:
    if _FINANCE_DF is None:
        return "No se ha subido ningún CSV financiero."
    try:
        result = _FINANCE_DF.query(query)
        return result.to_string(index=False) if not result.empty else "Sin filas que coincidan."
    except Exception as exc:      # pragma: no cover
        return f"Error al procesar la consulta: {exc}"
