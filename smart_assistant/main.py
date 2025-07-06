from smart_assistant.routers import expenses, news
from fastapi.middleware.cors import CORSMiddleware
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

app = FastAPI(title="LangGraph Reactive Agent API")



tracer_provider = register(
  project_name="news-agent", # Default is 'default'
  endpoint="http://localhost:6006/v1/traces"
)
LangChainInstrumentor(tracer_provider=tracer_provider).instrument(skip_dep_check=True)


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
