"""
Script para cargar textos en Chroma usando embeddings de Ollama con metadata
"""
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from procesar_json import procesar_malla_curricular
import shutil
from pathlib import Path

# 0. Eliminar vectorstore anterior si existe (para re-cargar con metadata)
vectorstore_path = Path("data/vectorstore")
if vectorstore_path.exists():
    print("🗑️  Eliminando vectorstore anterior para re-cargar con metadata...")
    shutil.rmtree(vectorstore_path)

# 1. Procesar el JSON y obtener textos estructurados con metadata
print("📖 Procesando JSON...")
textos, metadatas = procesar_malla_curricular("data/documents/malla_curricular_administracion_sistemas_informaticos.json")
print(f"✅ {len(textos)} materias procesadas\n")

# 2. Crear embeddings usando mxbai-embed-large
print("🔗 Creando embeddings con mxbai-embed-large...")
embeddings = OllamaEmbeddings(
    model="mxbai-embed-large",
    base_url="http://localhost:11434"
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

