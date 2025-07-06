from __future__ import annotations

import io
from datetime import datetime
from typing import Any

import pandas as pd
from langchain.output_parsers import PydanticOutputParser

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from sqlalchemy.orm import Session

from smart_assistant.models.expenses import FinancialPlanLLM
from smart_assistant.models.data import FinancialPlan, first_revision_date


# ---------- helpers -------------------------------------------------------- #
LATEST_MONTH = 6   # June 2025
LATEST_YEAR  = 2025


def _clean_dataframe(file: io.BytesIO) -> pd.DataFrame:
    df = pd.read_csv(file, parse_dates=["Date"], dayfirst=True)
    # filter to Mar–May–Jun 2025
    mask = (df["Date"].dt.year == LATEST_YEAR) & (df["Date"].dt.month >= LATEST_MONTH - 2)
    return df.loc[mask].copy()


def _calc_monthly_averages(df: pd.DataFrame) -> tuple[float, float]:
    df["month"] = df["Date"].dt.to_period("M")
    spend = df[df["Amount"] < 0].groupby("month")["Amount"].sum().abs().mean()
    earn  = df[df["Amount"] > 0].groupby("month")["Amount"].sum().mean()
    return round(spend or 0, 2), round(earn or 0, 2)


def _top_expense_categories(df: pd.DataFrame, top_n: int = 3) -> list[str]:
    """
    Return the top N expense categories by total absolute spend.
    """
    # sum negative amounts per description, take absolute, sort descending
    top = (
        df[df["Amount"] < 0]
        .groupby("Description")["Amount"]
        .sum()
        .abs()
        .nlargest(top_n)
        .index
        .tolist()
    )
    return top


# ---------- core ----------------------------------------------------------- #
def build_financial_plan(
    csv_file: io.BytesIO | bytes,
    goal: str,
    db: Session,
    llm_model: str = "gpt-4o-mini",
) -> dict[str, Any]:
    # if bytes, wrap in BytesIO
    if isinstance(csv_file, (bytes, bytearray)):
        csv_file = io.BytesIO(csv_file)

    df = _clean_dataframe(csv_file)

    # compute monthly averages
    m_spend, m_earn = _calc_monthly_averages(df)

    # compute top 3 expense categories
    top_expenses = _top_expense_categories(df, top_n=8)
    # e.g. ["Rent Payment", "POS Purchase", "Utility Payment"]

    # latest transaction date
    last_tx_date = df["Date"].max().date()

    # prepare the LLM structured parser
    parser = PydanticOutputParser(pydantic_object=FinancialPlanLLM)
    format_instructions = parser.get_format_instructions()

    system = SystemMessage(
        content=(
            "You are a financial advisor. You will receive:\n"
            "1) A personal financial goal.\n"
            "2) Monthly averages of spend and earnings.\n"
            "3) The top expense categories.\n"
            "You need to use the **Top expense categories** to respond the user monthly plan too, you need to tell the user the bad expenses he have"
            "Return ONLY a JSON with keys:\n"
            "monthly_spend_average, monthly_earnings_average, monthly_plan.\n"
            f"{format_instructions}"
        )
    )

    # include the descriptions of the top expense categories in the human prompt
    human = HumanMessage(
        content=(
            f"Goal: {goal}\n"
            f"Monthly spend average: ${m_spend:,.2f}\n"
            f"Monthly earnings average: ${m_earn:,.2f}\n"
            f"Top expense categories: {', '.join(top_expenses)}"
        )
    )

    # call the LLM
    llm = ChatOpenAI(model=llm_model, temperature=0.4)
    raw_out = llm.invoke([system, human]).content
    parsed: FinancialPlanLLM = parser.parse(raw_out)
    print("The goal ", goal)
    # persist the plan in Postgres
    plan = FinancialPlan(
        monthly_spend_average=parsed.monthly_spend_average,
        monthly_earnings_average=parsed.monthly_earnings_average,
        monthly_plan=parsed.monthly_plan,
        last_transaction_date=last_tx_date,
        first_revision=first_revision_date(),
        goal=goal,
    )
    db.add(plan)

    return parsed.model_dump()
