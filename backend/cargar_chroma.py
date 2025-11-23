"""
Script simple para cargar textos en Chroma usando embeddings de Ollama
"""
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from procesar_json import procesar_malla_curricular

# 1. Procesar el JSON y obtener textos estructurados
print("📖 Procesando JSON...")
textos = procesar_malla_curricular("data/documents/malla_curricular_administracion_sistemas_informaticos (1).json")
print(f"✅ {len(textos)} materias procesadas\n")

# 2. Crear embeddings usando mxbai-embed-large
print("🔗 Creando embeddings con mxbai-embed-large...")
embeddings = OllamaEmbeddings(
    model="mxbai-embed-large",
    base_url="http://localhost:11434"
)

# 3. Crear o cargar Chroma vector store
print("💾 Creando vector store en Chroma...")
vectorstore = Chroma.from_texts(
    texts=textos,
    embedding=embeddings,
    persist_directory="data/vectorstore"
)

print(f"✅ {len(textos)} documentos cargados en Chroma")
print(f"📁 Vector store guardado en: data/vectorstore")

# 4. Probar una búsqueda simple
print("\n🔍 Probando búsqueda...")
resultados = vectorstore.similarity_search("Cálculo", k=3)

print(f"\nEncontrados {len(resultados)} resultados para 'Cálculo':")
for i, doc in enumerate(resultados, 1):
    print(f"\n{i}. {doc.page_content[:200]}...")

