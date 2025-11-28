"""
Módulo simple para RAG: búsqueda en Chroma + generación con OpenAI
Enfoque híbrido: extracción programática para consultas estructuradas + LLM para razonamiento
"""
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
import openai
import os
import re
from typing import List, Dict, Optional, Tuple, Any
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def obtener_vectorstore():
    """Carga el vector store de Chroma"""
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    vectorstore = Chroma(
        persist_directory="data/vectorstore",
        embedding_function=embeddings
    )
    
    return vectorstore


def construir_filtro_metadata(pregunta: str) -> Optional[Dict[str, Any]]:
    """
    Analiza la pregunta y construye filtros de metadata dinámicamente.
    """
    query = pregunta.lower()
    condiciones = []
    
    # Detectar tipo de tipología (OBLIGATORIA, OPTATIVA)
    if any(palabra in query for palabra in ["obligatoria", "obligatorias", "obligatorio", "obligatorios"]):
        condiciones.append({"tipologia_tipo": "OBLIGATORIA"})
    elif any(palabra in query for palabra in ["optativa", "optativas", "optativo", "optativos", "electiva", "electivas"]):
        condiciones.append({"tipologia_tipo": "OPTATIVA"})
    
    # Detectar categoría de tipología (FUNDAMENTAL, DISCIPLINAR)
    if any(palabra in query for palabra in ["fundamental", "fundamentales", "fund.", "fundamentación"]):
        condiciones.append({"tipologia_categoria": "FUNDAMENTAL"})
    elif any(palabra in query for palabra in ["disciplinar", "disciplinares", "disciplina"]):
        condiciones.append({"tipologia_categoria": "DISCIPLINAR"})
    
    # Detectar semestre
    semestre_buscado = None
    semestres_texto = {
        "primer": 1, "primero": 1, "1er": 1, "1ro": 1,
        "segundo": 2, "segunda": 2, "2do": 2, "2da": 2,
        "tercer": 3, "tercero": 3, "3er": 3, "3ro": 3,
        "cuarto": 4, "4to": 4,
        "quinto": 5, "5to": 5,
        "sexto": 6, "6to": 6,
        "séptimo": 7, "septimo": 7, "7mo": 7,
        "octavo": 8, "8vo": 8,
        "noveno": 9, "9no": 9,
        "décimo": 10, "decimo": 10, "10mo": 10
    }
    
    for palabra, num in semestres_texto.items():
        if palabra in query:
            semestre_buscado = num
            break
    
    if semestre_buscado is None:
        match = re.search(r'semestre\s+(\d+)', query)
        if match:
            semestre_buscado = int(match.group(1))
    
    if semestre_buscado is not None:
        condiciones.append({"semestre": str(semestre_buscado)})
    
    # Construir el filtro según el número de condiciones
    if len(condiciones) == 0:
        return None
    elif len(condiciones) == 1:
        return condiciones[0]
    else:
        return {"$and": condiciones}


def buscar_contexto(pregunta: str, k: int = 100):
    """
    Busca documentos relevantes en Chroma usando filtros de metadata cuando sea posible.
    """
    vectorstore = obtener_vectorstore()
    
    # Construir filtros de metadata dinámicamente
    filtro_metadata = construir_filtro_metadata(pregunta)
    
    # Si hay filtros de metadata, usarlos
    if filtro_metadata:
        try:
            # Obtener documentos filtrados por metadata
            docs_filtrados = vectorstore.get(where=filtro_metadata)
            
            if docs_filtrados and docs_filtrados.get('ids') and len(docs_filtrados['ids']) > 0:
                # Si hay documentos filtrados, obtener sus textos
                documentos_filtrados = docs_filtrados.get('documents', [])
                metadatas_filtradas = docs_filtrados.get('metadatas', [])
                
                # Crear documentos LangChain
                from langchain_core.documents import Document
                resultados = [
                    Document(page_content=doc, metadata=meta if meta else {})
                    for doc, meta in zip(documentos_filtrados, metadatas_filtradas)
                ]
            else:
                # Si no hay documentos, usar búsqueda semántica como fallback
                resultados = vectorstore.similarity_search(pregunta, k=k)
        except Exception as e:
            # Si hay error, usar búsqueda semántica como fallback
            resultados = vectorstore.similarity_search(pregunta, k=k)
    else:
        # Si no hay filtros, usar búsqueda semántica normal
        resultados = vectorstore.similarity_search(pregunta, k=k)
    
    # Combinar los resultados en un solo contexto
    contexto = "\n\n".join([doc.page_content for doc in resultados])
    return contexto


def extraer_materias_del_contexto(contexto: str) -> List[Dict[str, str]]:
    """
    Extrae programáticamente todas las materias del contexto estructurado.
    Esto es más confiable que depender del LLM para extraer información estructurada.
    
    Returns:
        Lista de diccionarios con información de cada materia
    """
    materias = []
    
    # Patrón para extraer cada materia completa
    # Busca bloques que empiecen con "Materia:" y capture todos los campos
    patron = r'Materia: ([^\n]+)\nCódigo: ([^\n]+)\nSemestre: ([^\n]+)\nCréditos: ([^\n]+)\nTipología: ([^\n]+)(?:\nPrerrequisitos: ([^\n]+))?'
    
    matches = re.finditer(patron, contexto)
    
    for match in matches:
        materia = {
            'nombre': match.group(1).strip(),
            'codigo': match.group(2).strip(),
            'semestre': match.group(3).strip(),
            'creditos': match.group(4).strip(),
            'tipologia': match.group(5).strip(),
            'prerequisitos': match.group(6).strip() if match.group(6) else 'Ninguno'
        }
        materias.append(materia)
    
    return materias


def formatear_lista_materias(materias: List[Dict[str, str]]) -> str:
    """
    Formatea una lista de materias en un texto legible.
    """
    if not materias:
        return "No se encontraron materias."
    
    respuesta = f"Se encontraron {len(materias)} materia(s):\n\n"
    
    for i, materia in enumerate(materias, 1):
        respuesta += f"{i}. Materia: {materia['nombre']}\n"
        respuesta += f"   Código: {materia['codigo']}\n"
        respuesta += f"   Créditos: {materia['creditos']}\n"
        respuesta += f"   Tipología: {materia['tipologia']}\n"
        if materia['prerequisitos'] != 'Ninguno':
            respuesta += f"   Prerrequisitos: {materia['prerequisitos']}\n"
        respuesta += "\n"
    
    return respuesta


def es_pregunta_academica(pregunta: str) -> bool:
    """
    Detecta si la pregunta es sobre temas académicos (materias, carrera, etc.)
    o es un saludo/pregunta general.
    """
    query = pregunta.lower().strip()
    
    # Saludos comunes
    saludos = ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas noches", 
               "buen día", "qué tal", "que tal", "cómo estás", "como estas"]
    
    if query in saludos or any(saludo in query for saludo in saludos if len(query) < 20):
        return False
    
    # Palabras clave que indican pregunta académica
    palabras_academicas = [
        "materia", "materias", "curso", "cursos", "asignatura", "asignaturas",
        "semestre", "semestres", "carrera", "malla", "curricular", "curriculum",
        "prerequisito", "prerequisitos", "requisito", "requisitos", "crédito", "créditos",
        "credito", "creditos", "tipología", "tipologia", "obligatoria", "optativa",
        "disciplinar", "fundamental", "código", "codigo"
    ]
    
    return any(palabra in query for palabra in palabras_academicas)


def es_consulta_de_listado(pregunta: str) -> Tuple[bool, Optional[int]]:
    """
    Detecta si la pregunta es una consulta simple de listado (ej: "materias del semestre X").
    
    Returns:
        Tupla (es_listado, semestre) donde semestre es None si no se detecta un semestre específico
    """
    query = pregunta.lower()
    
    # Palabras clave que indican listado
    palabras_listado = [
        "qué materias", "que materias", "cuáles materias", "cuales materias",
        "lista", "listar", "materias del", "materias de", "materias en",
        "materias que hay", "materias que tiene"
    ]
    
    es_listado = any(palabra in query for palabra in palabras_listado)
    
    # Detectar semestre
    semestre_buscado = None
    semestres_texto = {
        "primer": 1, "primero": 1, "1er": 1, "1ro": 1,
        "segundo": 2, "segunda": 2, "2do": 2, "2da": 2,
        "tercer": 3, "tercero": 3, "3er": 3, "3ro": 3,
        "cuarto": 4, "4to": 4,
        "quinto": 5, "5to": 5,
        "sexto": 6, "6to": 6,
        "séptimo": 7, "septimo": 7, "7mo": 7,
        "octavo": 8, "8vo": 8,
        "noveno": 9, "9no": 9,
        "décimo": 10, "decimo": 10, "10mo": 10
    }
    
    for palabra, num in semestres_texto.items():
        if palabra in query:
            semestre_buscado = num
            break
    
    if semestre_buscado is None:
        match = re.search(r'semestre\s+(\d+)', query)
        if match:
            semestre_buscado = int(match.group(1))
    
    return es_listado, semestre_buscado


def responder_con_rag(pregunta: str):
    """
    Genera respuesta usando RAG con enfoque híbrido:
    - Extracción programática para consultas estructuradas (más confiable)
    - LLM para consultas que requieren razonamiento
    """
    # Inicializar el cliente de OpenAI
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model_name = "gpt-5-mini"  # Modelo válido de OpenAI
    
    # 0. Detectar si es un saludo simple - si es así, no buscar contexto
    if not es_pregunta_academica(pregunta):
        # Para saludos, responder sin contexto de manera natural
        respuesta = client.chat.completions.create(
            model=model_name,
            messages=[{
                'role': 'system', 
                'content': 'Eres un asistente académico universitario amigable y profesional. Responde de manera natural y breve.'
            }, {
                'role': 'user', 
                'content': pregunta
            }]
        )
        return respuesta.choices[0].message.content
    
    # 1. Buscar contexto relevante usando filtros de metadata cuando sea posible
    # Si hay filtros, usar k más grande. Si no, usar k más pequeño para evitar contexto innecesario
    filtro_metadata = construir_filtro_metadata(pregunta)
    k = 100 if filtro_metadata else 20  # Menos contexto cuando no hay filtros específicos
    contexto = buscar_contexto(pregunta, k=k)
    
    # 2. Detectar si es una consulta de listado simple
    es_listado, semestre = es_consulta_de_listado(pregunta)
    
    if es_listado:
        # Extraer programáticamente las materias (más confiable que el LLM)
        materias = extraer_materias_del_contexto(contexto)
        
        if materias:
            # Si se detectó un semestre específico, filtrar por ese semestre
            if semestre is not None:
                materias_filtradas = [
                    m for m in materias 
                    if m['semestre'] == str(semestre)
                ]
                if materias_filtradas:
                    return formatear_lista_materias(materias_filtradas)
                else:
                    return f"No se encontraron materias para el semestre {semestre}."
            
            # Si no hay filtro de semestre, devolver todas las materias encontradas
            return formatear_lista_materias(materias)
        else:
            # Si no se pudieron extraer materias, usar LLM como fallback
            pass  # Continuar con el flujo del LLM
    
    # 3. Para consultas complejas o si la extracción falló, usar LLM con prompt simple
    template = """Eres un asistente académico experto especializado en responder preguntas sobre la malla curricular del programa de Administración de Sistemas Informáticos.

Aquí tienes información relevante sobre cursos de la malla curricular: {cursos}

Cada curso tiene metadatos que incluyen: código, nombre, semestre, créditos, prerequisitos, tipología.

Responde la siguiente pregunta basándote ÚNICAMENTE en la información proporcionada: {question}

INSTRUCCIONES CRÍTICAS:
- Responde SIEMPRE en español.
- Sé EXTREMADAMENTE CONCISO. Responde solo con la información solicitada, sin explicaciones adicionales.
- Si la pregunta NO es sobre materias, cursos o la malla curricular, responde de manera natural sin usar la información de cursos.
- FILTRADO POR SEMESTRE: Si la pregunta menciona un semestre específico (ej: "primer semestre", "semestre 1"), DEBES verificar el campo "semestre" en los metadatos de cada curso y SOLO incluir los cursos que tengan exactamente ese semestre. IGNORA completamente los cursos de otros semestres.
- FILTRADO POR TIPOLOGÍA: Si la pregunta menciona una tipología (ej: "disciplinares", "obligatorias"), verifica el campo "tipologia" en los metadatos y SOLO incluye los cursos que coincidan.
- MATERIAS CON EL MISMO NOMBRE: Si encuentras múltiples materias con el mismo nombre pero diferentes códigos, semestres o tipologías, DEBES mencionar TODAS las variantes con sus diferencias (semestre, tipología, prerrequisitos). NO elijas solo una, muestra todas las opciones.
- Si la pregunta menciona un curso específico (ej: "Cálculo Integral"), busca ese curso. Si hay múltiples versiones, muestra todas.
- Para preguntas sobre un curso específico, responde SOLO con la información de ese curso (o todos si hay múltiples versiones).
- Ejemplos de respuestas correctas:
  * Pregunta: "¿qué prerequisito tiene Cálculo Integral?" → Respuesta: "Cálculo Diferencial"
  * Pregunta: "¿cuántos créditos tiene Cálculo Diferencial?" → Respuesta: "4 créditos"
  * Pregunta: "¿cuáles materias son de primer semestre?" → Respuesta: Lista SOLO las materias con semestre=1
  * Pregunta: "¿cuál es el prerrequisito de Sistemas Inteligentes Computacionales?" → Si hay dos versiones, muestra ambas con sus prerrequisitos
- NO expliques el proceso, NO menciones códigos a menos que se pidan explícitamente, NO incluyas cursos que no cumplan los criterios de filtrado."""
    
    prompt_content = template.format(cursos=contexto, question=pregunta)
    
    respuesta = client.chat.completions.create(
        model=model_name,
        messages=[{'role': 'user', 'content': prompt_content}]
    )
    
    return respuesta.choices[0].message.content

