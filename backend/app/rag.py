"""
Módulo simple para RAG: búsqueda en Chroma + generación con Ollama
Enfoque híbrido: extracción programática para consultas estructuradas + LLM para razonamiento
"""
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import Chroma
import ollama
import re
from typing import List, Dict, Optional, Tuple


def obtener_vectorstore():
    """Carga el vector store de Chroma"""
    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large",
        base_url="http://localhost:11434"
    )
    
    vectorstore = Chroma(
        persist_directory="data/vectorstore",
        embedding_function=embeddings
    )
    
    return vectorstore


def buscar_contexto(pregunta: str, k: int = 15):
    """Busca documentos relevantes en Chroma"""
    import re
    vectorstore = obtener_vectorstore()
    
    # Detectar si pregunta por un semestre específico
    query = pregunta.lower()
    semestre_buscado = None
    
    # Mapeo de palabras a números
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
    
    # Buscar número de semestre en la pregunta
    for palabra, num in semestres_texto.items():
        if palabra in query:
            semestre_buscado = num
            break
    
    # Si no encontró palabra, buscar "semestre X" donde X es un número
    if semestre_buscado is None:
        match = re.search(r'semestre\s+(\d+)', query)
        if match:
            semestre_buscado = int(match.group(1))
    
    # Si pregunta por un semestre específico, filtrar por ese semestre
    if semestre_buscado is not None:
        # Obtener TODOS los documentos del vectorstore (hay 59 materias)
        todos_resultados = vectorstore.similarity_search("materia", k=59)
        
        # Filtrar solo los que tienen exactamente "Semestre: X"
        resultados_filtrados = []
        for doc in todos_resultados:
            contenido = doc.page_content
            # Buscar "Semestre: X" donde X es exactamente el semestre buscado
            # Usar regex para evitar coincidencias con "Semestre: 10" cuando busco "Semestre: 1"
            patron = rf'Semestre: {semestre_buscado}(\s|$)'
            if re.search(patron, contenido):
                # Verificar que NO tenga otros semestres (si busco 1, no debe tener 10, 11, etc.)
                if semestre_buscado < 10:
                    # Si busco semestre 1-9, verificar que no tenga 10-99
                    tiene_otro_semestre = re.search(rf'Semestre: ([1-9][0-9]|[2-9][0-9])(\s|$)', contenido)
                    if not tiene_otro_semestre:
                        resultados_filtrados.append(doc)
                else:
                    # Si busco semestre 10+, solo verificar que coincida exactamente
                    resultados_filtrados.append(doc)
        
        # Si encontramos materias del semestre, usarlas
        if resultados_filtrados:
            resultados = resultados_filtrados
        else:
            # Si no encontramos con el filtro, usar búsqueda normal
            resultados = vectorstore.similarity_search(pregunta, k=k)
    else:
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
    # 1. Buscar contexto relevante
    contexto = buscar_contexto(pregunta, k=5)
    
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
    
    # 3. Para consultas complejas o si la extracción falló, usar LLM
    prompt = f"""Eres un asistente académico universitario. El contexto contiene información sobre materias de una carrera universitaria.

CONTEXTO:
{contexto}

PREGUNTA: {pregunta}

INSTRUCCIONES:
- Responde de manera clara y precisa usando la información del contexto
- Si la pregunta es sobre listar materias, incluye TODAS las que encuentres en el contexto
- Para cada materia menciona: código, nombre, créditos y tipología
- Si no encuentras información en el contexto, di claramente que no está disponible

RESPUESTA:"""
    
    respuesta = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    return respuesta['message']['content']

