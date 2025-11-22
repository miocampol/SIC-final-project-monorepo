"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI

app = FastAPI(
    title="Asistente Académico Universitario",
    description="Chatbot universitario especializado con RAG",
    version="0.1.0"
)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Asistente Académico Universitario API",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}

