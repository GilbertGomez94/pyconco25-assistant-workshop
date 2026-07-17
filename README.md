# Smart Assistant Workshop – PyCon Colombia 2025

Este repositorio contiene el código base para el taller **“Construyendo un asistente
LLM de propósito mixto con observabilidad”**.

## Instalación rápida

```bash
python -m venv .venv && source .venv/bin/activate  # o `poetry install`
pip install -r requirements.txt
cp .env.example .env && nano .env                  # añade tus llaves
uvicorn api.main:app --reload --port 9000

chainlit run chainlit_app.py --port 8000

https://docs.google.com/document/d/1W2teqdhZzSiYzOJT3FI84g5xKnYA5levQs2BH3fwlYQ/edit?usp=sharing