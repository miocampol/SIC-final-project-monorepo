"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
from pydantic import BaseModel
from app.rag import responder_con_rag

app = FastAPI(
    title="Asistente Académico Universitario",
    description="Chatbot universitario especializado con RAG",
    version="0.1.0"
)


class Pregunta(BaseModel):
    pregunta: str


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


@app.post("/chat")
async def chat(pregunta: Pregunta):
    """Endpoint para hacer preguntas usando RAG"""
    try:
        respuesta = responder_con_rag(pregunta.pregunta)
        return {
            "pregunta": pregunta.pregunta,
            "respuesta": respuesta
        }
    except Exception as e:
        return {
            "error": str(e),
            "mensaje": "Error procesando la pregunta"
        }
