"""
Procesador para documentos PDF de materias
Extrae información estructurada (código, nombre, descripción, contenido) de cada materia
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader


def procesar_pdf_materias(pdf_path: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Procesa un archivo PDF que contiene información de materias y lo convierte en textos estructurados y metadata.
    
    El PDF debe tener un formato donde cada materia tiene:
    - Código
    - Nombre
    - Descripción
    - Contenido
    
    Args:
        pdf_path: Ruta al archivo PDF
        
    Returns:
        Tupla con (textos, metadatas) donde:
        - textos: Lista de textos estructurados, uno por materia
        - metadatas: Lista de diccionarios con metadata de cada materia
    """
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")
    
    # Leer el PDF
    reader = PdfReader(pdf_file)
    texto_completo = ""
    
    print(f"📄 Leyendo PDF: {len(reader.pages)} páginas...")
    for page in reader.pages:
        texto_completo += page.extract_text() + "\n"
    
    # Extraer materias del texto
    materias = _extraer_materias_del_texto(texto_completo)
    
    textos = []
    metadatas = []
    
    for materia in materias:
        # Crear texto estructurado con toda la información disponible
        texto = f"""Materia: {materia['nombre']}
Código: {materia['codigo']}"""
        
        if materia.get('semestre'):
            texto += f"\nSemestre: {materia['semestre']}"
        
        if materia.get('descripcion'):
            texto += f"\nDescripción: {materia['descripcion']}"
        
        if materia.get('contenido'):
            texto += f"\nContenido: {materia['contenido']}"
        
        textos.append(texto)
        
        # Crear metadata
        metadata = {
            'codigo': materia['codigo'],
            'nombre': materia['nombre'],
            'fuente': 'pdf',  # Para distinguir del JSON
            'tiene_descripcion': bool(materia.get('descripcion')),
            'tiene_contenido': bool(materia.get('contenido'))
        }
        
        # Incluir semestre si está disponible (ya extraído del PDF o del código/nombre)
        if materia.get('semestre'):
            metadata['semestre'] = str(materia['semestre'])
        else:
            # Intentar extraer semestre si está en el código o nombre como fallback
            semestre = _extraer_semestre_de_materia(materia)
            if semestre:
                metadata['semestre'] = str(semestre)
        
        metadatas.append(metadata)
    
    return textos, metadatas


def _extraer_materias_del_texto(texto: str) -> List[Dict[str, Any]]:
    """
    Extrae información de materias del texto del PDF.
    
    Formato esperado:
    Primer semestre.
    Código:4200910
    Nombre: Fundamentos de Programación
    Descripción: [texto multilínea]
    Contenido: [texto multilínea]
    """
    materias = []
    
    # Diccionario para convertir texto de semestre a número
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
    
    # Patrón para encontrar bloques de semestre seguidos de materias
    # Busca: "Primer semestre." seguido de materias hasta el siguiente semestre
    patron_semestre = re.compile(
        r'(Primer|Segundo|Tercer|Cuarto|Quinto|Sexto|Séptimo|Septimo|Octavo|Noveno|Décimo|Decimo|Primero|Segunda|Tercero|Cuarta|Quinta|Sexta|Séptima|Septima|Octava|Novena|Décima|Decima|1er|1ro|2do|2da|3er|3ro|4to|5to|6to|7mo|8vo|9no|10mo)\s+semestre\.',
        re.IGNORECASE
    )
    
    # Encontrar todas las posiciones de semestres
    posiciones_semestres = []
    for match in patron_semestre.finditer(texto):
        semestre_texto = match.group(1).lower()
        semestre_num = semestres_texto.get(semestre_texto, None)
        posiciones_semestres.append((match.start(), match.end(), semestre_num))
    
    # Si no se encontraron semestres, intentar método alternativo
    if not posiciones_semestres:
        return _extraer_materias_alternativo(texto)
    
    # Procesar cada bloque de semestre
    for i, (inicio_semestre, fin_semestre, semestre_num) in enumerate(posiciones_semestres):
        # Determinar el final del bloque (siguiente semestre o fin del texto)
        if i + 1 < len(posiciones_semestres):
            fin_bloque = posiciones_semestres[i + 1][0]
        else:
            fin_bloque = len(texto)
        
        bloque_texto = texto[fin_semestre:fin_bloque]
        
        # Buscar todas las materias en este bloque
        # Patrón: Código:XXXXX seguido de Nombre, Descripción y Contenido
        # El contenido puede estar en la misma línea o en líneas siguientes
        # Nota: re.IGNORECASE hace que funcione con mayúsculas, minúsculas o cualquier combinación
        # Los dos puntos (:) son opcionales - funciona con "Código:4200910" o "Código 4200910"
        patron_materia = re.compile(
            r'Código\s*:?\s*([A-Z0-9\s\-]+?)\n'
            r'Nombre\s*:?\s*(.+?)\n'
            r'Descripción\s*:?\s*(.+?)(?=\n\s*Contenido\s*:?)'
            r'\n\s*Contenido\s*:?\s*(.*?)(?=\n\s*Código\s*:?|$)',
            re.IGNORECASE | re.DOTALL
        )
        
        matches = patron_materia.finditer(bloque_texto)
        
        for match in matches:
            codigo = match.group(1).strip()
            nombre = match.group(2).strip() if match.group(2) else ""
            descripcion = match.group(3).strip() if match.group(3) else ""
            contenido = match.group(4).strip() if match.group(4) else ""
            
            if codigo and nombre:
                materia = {
                    'codigo': codigo,
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'contenido': contenido,
                    'semestre': semestre_num
                }
                materias.append(materia)
    
    # Si no se encontraron materias, intentar método alternativo
    if not materias:
        materias = _extraer_materias_alternativo(texto)
    
    return materias


def _extraer_materias_alternativo(texto: str) -> List[Dict[str, Any]]:
    """
    Método alternativo para extraer materias si el patrón principal no funciona.
    Busca líneas que contengan códigos de materias (formato común: números o letras-números).
    """
    materias = []
    lineas = texto.split('\n')
    
    i = 0
    while i < len(lineas):
        linea = lineas[i].strip()
        
        # Buscar líneas que parezcan códigos de materias
        # Ajusta este patrón según el formato de tus códigos
        codigo_match = re.search(r'([A-Z]{2,}\s*\d{4,}|\d{6,})', linea)
        
        if codigo_match:
            codigo = codigo_match.group(1).strip()
            nombre = ""
            descripcion = ""
            contenido = ""
            
            # Buscar nombre en las siguientes líneas
            j = i + 1
            while j < min(i + 5, len(lineas)) and not nombre:
                siguiente_linea = lineas[j].strip()
                if siguiente_linea and len(siguiente_linea) > 5:
                    nombre = siguiente_linea
                j += 1
            
            # Buscar descripción y contenido en bloques siguientes
            # (ajusta según el formato de tu PDF)
            
            if codigo and nombre:
                materias.append({
                    'codigo': codigo,
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'contenido': contenido
                })
        
        i += 1
    
    return materias


def _extraer_semestre_de_materia(materia: Dict[str, Any]) -> int | None:
    """
    Intenta extraer el semestre de una materia basándose en su código o nombre.
    Retorna None si no se puede determinar.
    """
    # Buscar números de semestre en el código o nombre
    texto_busqueda = f"{materia['codigo']} {materia['nombre']}"
    
    # Buscar patrones como "Semestre 1", "1er semestre", etc.
    match = re.search(r'(?:semestre|sem\.?)\s*(\d+)', texto_busqueda, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Buscar números al inicio que podrían ser semestres
    match = re.search(r'\b([1-9]|10)\b', texto_busqueda)
    if match:
        semestre = int(match.group(1))
        if 1 <= semestre <= 10:
            return semestre
    
    return None


if __name__ == "__main__":
    # Ejemplo de uso
    pdf_path = "data/documents/Contenido_de_las_asignaturas.pdf"
    
    try:
        textos, metadatas = procesar_pdf_materias(pdf_path)
        
        print(f"✅ Total de materias procesadas: {len(textos)}\n")
        print("Primeras 3 materias con metadata:")
        print("=" * 50)
        for i in range(min(3, len(textos))):
            print(f"Texto:\n{textos[i]}")
            print(f"Metadata: {metadatas[i]}")
            print("-" * 50)
    except FileNotFoundError:
        print(f"⚠️  Archivo no encontrado: {pdf_path}")
        print("Por favor, coloca tu PDF en la ruta especificada.")

