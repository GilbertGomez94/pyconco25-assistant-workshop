from smart_assistant.routers import expenses, news, research, assistant
from smart_assistant.agents import build_agent
from smart_assistant.tools.finance_file import set_finance_df

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd, io
from typing import Optional
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

app = FastAPI(title="LangGraph Reactive Agent API")



tracer_provider = register(
  project_name="news-agent", # Default is 'default'
  endpoint="http://localhost:6006/v1/traces"
)
LangChainInstrumentor(tracer_provider=tracer_provider).instrument(skip_dep_check=True)

agent = build_agent()  # crea una única instancia


app = FastAPI(
    title="Smart Assistant API",
    version="1.0.0",
    description="Servicios para gastos, noticias y búsqueda académica.",
)

# CORS – necesario para Chainlit (si corre en otro puerto/origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restringe en prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(expenses.router, prefix="/v1")
app.include_router(news.router, prefix="/v1")
app.include_router(research.router, prefix="/v1")
app.include_router(assistant.router,  prefix="/v1")   #  ← NUEVO
