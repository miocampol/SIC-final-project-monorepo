"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.rag import responder_con_rag, responder_con_rag_stream
import json

app = FastAPI(
    title="Asistente Académico Universitario",
    description="Chatbot universitario especializado con RAG",
    version="0.1.0"
)

# Configurar CORS para permitir peticiones del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.post("/chat/stream")
async def chat_stream(pregunta: Pregunta):
    """Endpoint para hacer preguntas usando RAG con streaming (Server-Sent Events)"""
    def generate():
        try:
            for chunk in responder_con_rag_stream(pregunta.pregunta):
                # Formato SSE: data: {chunk}\n\n
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            # Señal de finalización
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            error_msg = json.dumps({'error': str(e), 'mensaje': 'Error procesando la pregunta'})
            yield f"data: {error_msg}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Deshabilitar buffering en nginx
        }
    )
