"""
Módulo simple para RAG: búsqueda en Chroma + generación con OpenAI
Enfoque híbrido: extracción programática para consultas estructuradas + LLM para razonamiento
"""
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
import openai
import os
import re
import logging
from typing import List, Dict, Optional, Tuple, Any
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Caché global del vectorstore para evitar recrearlo en cada llamada
_vectorstore_cache = None


def obtener_vectorstore():
    """Carga el vector store de Chroma (con caché)"""
    global _vectorstore_cache
    
    if _vectorstore_cache is None:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        
        _vectorstore_cache = Chroma(
            persist_directory="data/vectorstore",
            embedding_function=embeddings
        )
    
    return _vectorstore_cache


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


def es_consulta_especifica_materia(pregunta: str) -> bool:
    """
    Detecta si la pregunta es sobre una materia específica (código, créditos, etc.)
    """
    query = pregunta.lower()
    palabras_especificas = [
        "código", "codigo", "cuántos créditos", "cuantos creditos",
        "qué créditos", "que creditos", "cuántos creditos", "cuantos creditos",
        "semestre de", "tipología de", "tipologia de", "prerequisito de", "prerequisitos de"
    ]
    return any(palabra in query for palabra in palabras_especificas)


def extraer_nombre_materia_de_pregunta(pregunta: str) -> Optional[str]:
    """
    Intenta extraer el nombre de una materia de la pregunta.
    Busca patrones como "código de X", "créditos de X", etc.
    """
    # Patrones comunes: "código de [MATERIA]", "créditos de [MATERIA]", etc.
    patrones = [
        r'(?:código|codigo|créditos|creditos|semestre|tipología|tipologia|prerequisito|prerequisitos)\s+(?:de|del|de la|del la)\s+(.+?)(?:\?|$|\.)',
        r'(?:cuál|cuál es|que|qué es)\s+(?:el|la)\s+(?:código|codigo|créditos|creditos)\s+(?:de|del|de la)\s+(.+?)(?:\?|$|\.)',
    ]
    
    for patron in patrones:
        match = re.search(patron, pregunta, re.IGNORECASE)
        if match:
            nombre = match.group(1).strip()
            # Limpiar el nombre (quitar palabras comunes al final)
            nombre = re.sub(r'\s+(materia|asignatura|curso)$', '', nombre, flags=re.IGNORECASE)
            if len(nombre) > 3:  # Asegurar que tiene sentido
                return nombre
    
    return None


def extraer_info_especifica_del_contexto(contexto: str, pregunta: str) -> Optional[str]:
    """
    Extrae información específica (código, créditos) del contexto sin usar LLM.
    Retorna None si no puede extraer programáticamente.
    """
    query = pregunta.lower()
    
    # Extraer materias del contexto
    materias = extraer_materias_del_contexto(contexto)
    logger.info(f"📝 Materias extraídas del contexto: {len(materias)}")
    
    if not materias:
        logger.warning("⚠️ No se pudieron extraer materias del contexto")
        return None
    
    # Si hay solo una materia, usar esa
    if len(materias) == 1:
        materia = materias[0]
    else:
        # Intentar encontrar la materia por nombre
        nombre_buscado = extraer_nombre_materia_de_pregunta(pregunta)
        if nombre_buscado:
            # Buscar materia que coincida con el nombre
            for m in materias:
                if nombre_buscado.lower() in m['nombre'].lower() or m['nombre'].lower() in nombre_buscado.lower():
                    materia = m
                    break
            else:
                # Si no se encuentra, usar la primera
                materia = materias[0]
        else:
            materia = materias[0]
    
    # Extraer la información solicitada
    if "código" in query or "codigo" in query:
        codigo = materia.get('codigo', 'No disponible')
        logger.info(f"✅ Código extraído: {codigo} de materia: {materia.get('nombre', 'N/A')}")
        return codigo
    elif "créditos" in query or "creditos" in query:
        creditos = materia.get('creditos', 'No disponible')
        logger.info(f"✅ Créditos extraídos: {creditos} de materia: {materia.get('nombre', 'N/A')}")
        return creditos
    elif "semestre" in query:
        semestre = materia.get('semestre', 'No disponible')
        logger.info(f"✅ Semestre extraído: {semestre} de materia: {materia.get('nombre', 'N/A')}")
        return semestre
    elif "tipología" in query or "tipologia" in query:
        tipologia = materia.get('tipologia', 'No disponible')
        logger.info(f"✅ Tipología extraída: {tipologia} de materia: {materia.get('nombre', 'N/A')}")
        return tipologia
    elif "prerequisito" in query:
        prerequisitos = materia.get('prerequisitos', 'Ninguno')
        logger.info(f"✅ Prerequisitos extraídos: {prerequisitos} de materia: {materia.get('nombre', 'N/A')}")
        return prerequisitos
    
    logger.warning("⚠️ No se pudo determinar qué información extraer de la pregunta")
    return None


def buscar_contexto(pregunta: str, k: Optional[int] = None):
    """
    Busca documentos relevantes en Chroma usando filtros de metadata cuando sea posible.
    Optimizado para reducir tiempo de respuesta.
    """
    vectorstore = obtener_vectorstore()
    
    # Detectar si es una consulta de listado (necesita todos los resultados)
    es_listado, _ = es_consulta_de_listado(pregunta)
    
    # Determinar k óptimo según el tipo de consulta
    if k is None:
        if es_consulta_especifica_materia(pregunta):
            # Si hay un nombre de materia específico, usar k=1 o k=2
            nombre_materia = extraer_nombre_materia_de_pregunta(pregunta)
            if nombre_materia:
                k = 2  # Para consultas muy específicas con nombre de materia
                logger.info(f"🎯 Consulta específica detectada con materia '{nombre_materia}', usando k=2")
            else:
                k = 3  # Para consultas específicas sin nombre claro
                logger.info("🎯 Consulta específica detectada sin nombre claro, usando k=3")
        else:
            k = 10  # Para consultas generales, usar 10
            logger.info("📋 Consulta general detectada, usando k=10")
    
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
                
                # Si es una consulta de listado, devolver TODOS los documentos filtrados
                # Si no, limitar a k documentos
                if not es_listado and len(resultados) > k:
                    logger.info(f"📊 Limitando resultados de {len(resultados)} a {k} documentos (no es listado)")
                    resultados = resultados[:k]
                else:
                    logger.info(f"📊 Consulta de listado detectada: devolviendo TODOS los {len(resultados)} documentos filtrados")
            else:
                # Si no hay documentos, usar búsqueda semántica como fallback
                logger.warning("⚠️ No se encontraron documentos con el filtro de metadata, usando búsqueda semántica")
                resultados = vectorstore.similarity_search(pregunta, k=k)
        except Exception as e:
            logger.error(f"❌ Error al filtrar por metadata: {e}, usando búsqueda semántica")
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


def es_pregunta_sobre_identidad(pregunta: str) -> bool:
    """
    Detecta si la pregunta es sobre la identidad del chatbot.
    """
    query = pregunta.lower().strip()
    
    # Patrones que indican pregunta sobre identidad
    patrones_identidad = [
        "quién eres", "quien eres", "quien sos", "quién sos",
        "qué eres", "que eres", "que sos", "qué sos",
        "cuál es tu nombre", "cual es tu nombre",
        "de dónde eres", "de donde eres",
        "de qué universidad", "de que universidad",
        "qué universidad", "que universidad",
        "de qué sede", "de que sede",
        "qué sede", "que sede",
        "presentate", "preséntate",
        "dime quién eres", "dime quien eres"
    ]
    
    return any(patron in query for patron in patrones_identidad)


def es_pregunta_academica(pregunta: str) -> bool:
    """
    Detecta si la pregunta es sobre temas académicos (materias, carrera, etc.)
    o es un saludo/pregunta general.
    """
    query = pregunta.lower().strip()
    
    # Si es pregunta sobre identidad, no es académica
    if es_pregunta_sobre_identidad(pregunta):
        return False
    
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


def es_consulta_sobre_cantidad(pregunta: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Detecta si la pregunta es sobre la cantidad de materias.
    Retorna (es_consulta_cantidad, filtros) donde filtros contiene el tipo de materias buscadas.
    """
    query = pregunta.lower()
    
    # Palabras clave que indican pregunta sobre cantidad
    palabras_cantidad = [
        "cuántas", "cuantas", "cuántos", "cuantos",
        "cuántas materias", "cuantas materias", "cuántos cursos", "cuantos cursos",
        "cuántas asignaturas", "cuantas asignaturas", "total de materias"
    ]
    
    es_cantidad = any(palabra in query for palabra in palabras_cantidad)
    
    if not es_cantidad:
        return False, None
    
    # Detectar filtros
    filtros = {}
    
    # Tipo de tipología
    if any(palabra in query for palabra in ["obligatoria", "obligatorias", "obligatorio", "obligatorios"]):
        filtros['tipo'] = "OBLIGATORIA"
    elif any(palabra in query for palabra in ["optativa", "optativas", "optativo", "optativos", "electiva", "electivas"]):
        filtros['tipo'] = "OPTATIVA"
    
    # Categoría de tipología
    if any(palabra in query for palabra in ["fundamental", "fundamentales", "fund.", "fundamentación"]):
        filtros['categoria'] = "FUNDAMENTAL"
    elif any(palabra in query for palabra in ["disciplinar", "disciplinares", "disciplina"]):
        filtros['categoria'] = "DISCIPLINAR"
    elif any(palabra in query for palabra in ["lengua extranjera", "lengua", "idioma"]):
        filtros['categoria'] = "LENGUA EXTRANJERA"
    elif any(palabra in query for palabra in ["trabajo de grado", "trabajo grado"]):
        filtros['categoria'] = "TRABAJO DE GRADO"
    
    return True, filtros


def responder_cantidad_materias(filtros: Dict[str, Any]) -> str:
    """
    Responde con la cantidad de materias según los filtros proporcionados.
    Usa números predefinidos para mayor precisión.
    """
    # Números predefinidos
    total_materias = 54  # Sin contar electivas (aunque esto incluye todo)
    fundamentales_obligatorias = 15
    fundamentales_optativas = 6
    disciplinares_obligatorias = 21
    disciplinares_optativas = 7
    lengua_extranjera = 4
    trabajo_grado = 1
    
    tipo = filtros.get('tipo')
    categoria = filtros.get('categoria')
    
    # Casos específicos
    if categoria == "FUNDAMENTAL" and tipo == "OBLIGATORIA":
        return f"Hay {fundamentales_obligatorias} materias fundamentales obligatorias."
    elif categoria == "FUNDAMENTAL" and tipo == "OPTATIVA":
        return f"Hay {fundamentales_optativas} materias fundamentales optativas."
    elif categoria == "DISCIPLINAR" and tipo == "OBLIGATORIA":
        return f"Hay {disciplinares_obligatorias} materias disciplinares obligatorias."
    elif categoria == "DISCIPLINAR" and tipo == "OPTATIVA":
        return f"Hay {disciplinares_optativas} materias disciplinares optativas."
    elif categoria == "LENGUA EXTRANJERA":
        return f"Hay {lengua_extranjera} materias de lengua extranjera."
    elif categoria == "TRABAJO DE GRADO":
        return f"Hay {trabajo_grado} materia de trabajo de grado."
    elif categoria == "FUNDAMENTAL":
        total = fundamentales_obligatorias + fundamentales_optativas
        return f"Hay {total} materias fundamentales en total ({fundamentales_obligatorias} obligatorias y {fundamentales_optativas} optativas)."
    elif categoria == "DISCIPLINAR":
        total = disciplinares_obligatorias + disciplinares_optativas
        return f"Hay {total} materias disciplinares en total ({disciplinares_obligatorias} obligatorias y {disciplinares_optativas} optativas)."
    elif tipo == "OBLIGATORIA":
        total = fundamentales_obligatorias + disciplinares_obligatorias
        return f"Hay {total} materias obligatorias en total ({fundamentales_obligatorias} fundamentales y {disciplinares_obligatorias} disciplinares)."
    elif tipo == "OPTATIVA":
        total = fundamentales_optativas + disciplinares_optativas
        return f"Hay {total} materias optativas en total ({fundamentales_optativas} fundamentales y {disciplinares_optativas} disciplinares)."
    else:
        # Total general (sin contar electivas según el usuario, pero el total es 54)
        return f"Hay {total_materias} materias en total en la malla curricular (sin contar electivas)."


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
        "cuáles son las materias", "cuales son las materias", "cuáles son", "cuales son",
        "lista", "listar", "materias del", "materias de", "materias en",
        "materias que hay", "materias que tiene", "materias que son"
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
    
    # 0. Detectar si es una pregunta sobre identidad
    if es_pregunta_sobre_identidad(pregunta):
        # Respuesta personalizada sobre la identidad del chatbot
        respuesta_identidad = """Soy un asistente académico virtual de la Universidad Nacional de Colombia, sede Manizales. 

Estoy aquí para ayudarte con información sobre la malla curricular, materias, semestres, créditos, prerrequisitos y cualquier otra consulta relacionada con los programas académicos de la universidad.

¿En qué puedo ayudarte hoy?"""
        return respuesta_identidad
    
    # 1. Detectar si es un saludo simple - si es así, no buscar contexto
    if not es_pregunta_academica(pregunta):
        # Para saludos, responder sin contexto de manera natural pero mencionando la universidad
        respuesta = client.chat.completions.create(
            model=model_name,
            messages=[{
                'role': 'system', 
                'content': 'Eres un asistente académico virtual de la Universidad Nacional de Colombia, sede Manizales. Eres amigable, profesional y estás aquí para ayudar con información sobre la malla curricular, programas académicos e información general de la universidad. Responde de manera natural y breve.'
            }, {
                'role': 'user', 
                'content': pregunta
            }]
        )
        return respuesta.choices[0].message.content
    
    # 1. Detectar si es una pregunta sobre cantidad de materias
    es_cantidad, filtros_cantidad = es_consulta_sobre_cantidad(pregunta)
    if es_cantidad and filtros_cantidad is not None:
        logger.info(f"🔢 Consulta sobre cantidad detectada con filtros: {filtros_cantidad}")
        respuesta = responder_cantidad_materias(filtros_cantidad)
        logger.info(f"✅ Respuesta predefinida: {respuesta}")
        return respuesta
    
    # 2. Buscar contexto relevante (k se calcula automáticamente según el tipo de consulta)
    contexto = buscar_contexto(pregunta)
    logger.info(f"📚 Contexto obtenido: {len(contexto)} caracteres")
    
    # 2.5. Intentar extracción programática directa para consultas específicas (evita LLM)
    if es_consulta_especifica_materia(pregunta):
        logger.info("🔍 Detectada consulta específica, intentando extracción programática...")
        info_extraida = extraer_info_especifica_del_contexto(contexto, pregunta)
        if info_extraida and info_extraida != 'No disponible':
            logger.info(f"✅ Extracción programática exitosa (sin LLM): {info_extraida}")
            return info_extraida
        else:
            logger.info("⚠️ Extracción programática falló, usando LLM como fallback")
    
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
    
    # 2. Para consultas complejas o si la extracción falló, usar LLM con prompt optimizado
    logger.info("🤖 Usando LLM para generar respuesta...")
    # Prompt más corto para reducir tokens y tiempo de procesamiento
    prompt_content = f"""Información: {contexto}

Pregunta: {pregunta}

Responde SOLO lo que se pregunta. Si preguntan por código, da solo el código. Si preguntan por créditos, da solo los créditos."""
    
    respuesta = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                'role': 'system',
                'content': 'Asistente académico. Responde SOLO lo que se pregunta. Sé conciso.'
            },
            {
                'role': 'user',
                'content': prompt_content
            }
        ]
    )
    
    return respuesta.choices[0].message.content


def responder_con_rag_stream(pregunta: str):
    """
    Genera respuesta usando RAG con streaming (generador).
    Retorna un generador que produce chunks de texto.
    """
    # Inicializar el cliente de OpenAI
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model_name = "gpt-5-mini"  # Modelo válido de OpenAI
    
    # 0. Detectar si es una pregunta sobre identidad
    if es_pregunta_sobre_identidad(pregunta):
        # Respuesta personalizada sobre la identidad del chatbot
        respuesta_identidad = """Soy un asistente académico virtual de la Universidad Nacional de Colombia, sede Manizales. 

Estoy aquí para ayudarte con información sobre la malla curricular, materias, semestres, créditos, prerrequisitos y cualquier otra consulta relacionada con los programas académicos de la universidad.

¿En qué puedo ayudarte hoy?"""
        # Simular streaming palabra por palabra para respuestas predefinidas
        palabras = respuesta_identidad.split(' ')
        for palabra in palabras:
            yield palabra + ' '
        return
    
    # 1. Detectar si es un saludo simple - si es así, no buscar contexto
    if not es_pregunta_academica(pregunta):
        # Para saludos, responder sin contexto de manera natural pero mencionando la universidad
        stream = client.chat.completions.create(
            model=model_name,
            messages=[{
                'role': 'system', 
                'content': 'Eres un asistente académico virtual de la Universidad Nacional de Colombia, sede Manizales. Eres amigable, profesional y estás aquí para ayudar con información sobre la malla curricular, programas académicos e información general de la universidad. Responde de manera natural y breve.'
            }, {
                'role': 'user', 
                'content': pregunta
            }],
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
        return
    
    # 1. Detectar si es una pregunta sobre cantidad de materias
    es_cantidad, filtros_cantidad = es_consulta_sobre_cantidad(pregunta)
    if es_cantidad and filtros_cantidad is not None:
        logger.info(f"🔢 Consulta sobre cantidad detectada con filtros: {filtros_cantidad}")
        respuesta = responder_cantidad_materias(filtros_cantidad)
        logger.info(f"✅ Respuesta predefinida: {respuesta}")
        # Simular streaming palabra por palabra
        palabras = respuesta.split(' ')
        for palabra in palabras:
            yield palabra + ' '
        return
    
    # 2. Buscar contexto relevante (k se calcula automáticamente según el tipo de consulta)
    contexto = buscar_contexto(pregunta)
    logger.info(f"📚 Contexto obtenido: {len(contexto)} caracteres")
    
    # 2.5. Intentar extracción programática directa para consultas específicas (evita LLM)
    if es_consulta_especifica_materia(pregunta):
        logger.info("🔍 Detectada consulta específica, intentando extracción programática...")
        info_extraida = extraer_info_especifica_del_contexto(contexto, pregunta)
        if info_extraida and info_extraida != 'No disponible':
            logger.info(f"✅ Extracción programática exitosa (sin LLM): {info_extraida}")
            # Simular streaming palabra por palabra
            palabras = info_extraida.split(' ')
            for palabra in palabras:
                yield palabra + ' '
            return
        else:
            logger.info("⚠️ Extracción programática falló, usando LLM como fallback")
    
    # 3. Detectar si es una consulta de listado simple
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
                    respuesta = formatear_lista_materias(materias_filtradas)
                    # Simular streaming palabra por palabra
                    palabras = respuesta.split(' ')
                    for palabra in palabras:
                        yield palabra + ' '
                    return
                else:
                    respuesta = f"No se encontraron materias para el semestre {semestre}."
                    palabras = respuesta.split(' ')
                    for palabra in palabras:
                        yield palabra + ' '
                    return
            
            # Si no hay filtro de semestre, devolver todas las materias encontradas
            respuesta = formatear_lista_materias(materias)
            palabras = respuesta.split(' ')
            for palabra in palabras:
                yield palabra + ' '
            return
    
    # 4. Para consultas complejas, usar LLM con streaming (prompt optimizado)
    logger.info("🤖 Usando LLM para generar respuesta (streaming)...")
    # Prompt más corto para reducir tokens y tiempo de procesamiento
    prompt_content = f"""Información: {contexto}

Pregunta: {pregunta}

Responde SOLO lo que se pregunta. Si preguntan por código, da solo el código. Si preguntan por créditos, da solo los créditos."""
    
    stream = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                'role': 'system',
                'content': 'Asistente académico. Responde SOLO lo que se pregunta. Sé conciso.'
            },
            {
                'role': 'user',
                'content': prompt_content
            }
        ],
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

