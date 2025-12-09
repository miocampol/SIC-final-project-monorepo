"""
Script para cargar textos en Chroma usando embeddings de OpenAI con metadata
Soporta múltiples formatos: JSON, PDF y CSV
"""
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from procesar_json import procesar_malla_curricular
from procesar_pdf import procesar_pdf_materias
from procesar_csv import procesar_csv_horarios
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

# 1. Procesar documentos (JSON y/o PDF)
todos_textos = []
todas_metadatas = []

# Procesar JSON si existe
json_path = "data/documents/malla_curricular_administracion_sistemas_informaticos.json"
if Path(json_path).exists():
    print("📖 Procesando JSON...")
    textos_json, metadatas_json = procesar_malla_curricular(json_path)
    todos_textos.extend(textos_json)
    todas_metadatas.extend(metadatas_json)
    print(f"✅ {len(textos_json)} materias del JSON procesadas\n")
else:
    print(f"⚠️  JSON no encontrado en: {json_path}\n")

# Procesar PDF si existe
pdf_path = "data/documents/Contenido_de_las_asignaturas.pdf"
if Path(pdf_path).exists():
    print("📄 Procesando PDF...")
    textos_pdf, metadatas_pdf = procesar_pdf_materias(pdf_path)
    todos_textos.extend(textos_pdf)
    todas_metadatas.extend(metadatas_pdf)
    print(f"✅ {len(textos_pdf)} materias del PDF procesadas\n")
else:
    print(f"⚠️  PDF no encontrado en: {pdf_path}")
    print("   Si tienes un PDF, colócalo en esa ruta para procesarlo.\n")

# Procesar CSV si existe
csv_path = "data/documents/asignaturas_formato.csv"
if Path(csv_path).exists():
    print("📊 Procesando CSV...")
    textos_csv, metadatas_csv = procesar_csv_horarios(csv_path)
    todos_textos.extend(textos_csv)
    todas_metadatas.extend(metadatas_csv)
    print(f"✅ {len(textos_csv)} grupos del CSV procesados\n")
else:
    print(f"⚠️  CSV no encontrado en: {csv_path}")
    print("   Si tienes un CSV, colócalo en esa ruta para procesarlo.\n")

if not todos_textos:
    print("❌ Error: No se encontraron documentos para procesar.")
    print("   Asegúrate de tener al menos un JSON o PDF en data/documents/")
    exit(1)

print(f"📊 Total de documentos a cargar: {len(todos_textos)}")
print(f"   - JSON: {len([m for m in todas_metadatas if m.get('fuente') not in ['pdf', 'csv']])}")
print(f"   - PDF: {len([m for m in todas_metadatas if m.get('fuente') == 'pdf'])}")
print(f"   - CSV: {len([m for m in todas_metadatas if m.get('fuente') == 'csv'])}\n")

# 2. Crear embeddings usando text-embedding-3-small de OpenAI
print("🔗 Creando embeddings con text-embedding-3-small (OpenAI)...")
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# 3. Crear Chroma vector store con metadata
print("💾 Creando vector store en Chroma con metadata...")
vectorstore = Chroma.from_texts(
    texts=todos_textos,
    metadatas=todas_metadatas,
    embedding=embeddings,
    persist_directory="data/vectorstore"
)

print(f"✅ {len(todos_textos)} documentos cargados en Chroma con metadata")
print(f"📁 Vector store guardado en: data/vectorstore")
print("\n✅ ¡Listo! El vectorstore está actualizado y listo para usar.")

