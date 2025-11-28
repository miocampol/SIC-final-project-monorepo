"""
Script para cargar textos en Chroma usando embeddings de OpenAI con metadata
"""
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from procesar_json import procesar_malla_curricular
import shutil
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# 0. Eliminar vectorstore anterior si existe (para re-cargar con metadata)
vectorstore_path = Path("data/vectorstore")
if vectorstore_path.exists():
    print("🗑️  Eliminando vectorstore anterior para re-cargar con metadata...")
    shutil.rmtree(vectorstore_path)

# 1. Procesar el JSON y obtener textos estructurados con metadata
print("📖 Procesando JSON...")
textos, metadatas = procesar_malla_curricular("data/documents/malla_curricular_administracion_sistemas_informaticos.json")
print(f"✅ {len(textos)} materias procesadas\n")

# 2. Crear embeddings usando text-embedding-3-small de OpenAI
print("🔗 Creando embeddings con text-embedding-3-small (OpenAI)...")
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# 3. Crear Chroma vector store con metadata
print("💾 Creando vector store en Chroma con metadata...")
vectorstore = Chroma.from_texts(
    texts=textos,
    metadatas=metadatas,
    embedding=embeddings,
    persist_directory="data/vectorstore"
)

print(f"✅ {len(textos)} documentos cargados en Chroma con metadata")
print(f"📁 Vector store guardado en: data/vectorstore")
print("\n✅ ¡Listo! El vectorstore está actualizado y listo para usar.")

