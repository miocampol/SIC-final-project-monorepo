"""
Procesador genérico para documentos JSON de malla curricular
Convierte JSON a texto estructurado para RAG
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple


def procesar_malla_curricular(json_path: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Procesa un archivo JSON de malla curricular y lo convierte en textos estructurados y metadata.
    
    Args:
        json_path: Ruta al archivo JSON
        
    Returns:
        Tupla con (textos, metadatas) donde:
        - textos: Lista de textos estructurados, uno por materia
        - metadatas: Lista de diccionarios con metadata de cada materia
    """
    json_file = Path(json_path)
    
    if not json_file.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {json_path}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        materias = json.load(f)
    
    textos = []
    metadatas = []
    
    for materia in materias:
        # Manejar prerrequisitos: puede ser string o array
        prerequisitos = materia.get('prerequisitos', 'Ninguna')
        if isinstance(prerequisitos, str):
            # Si es string, usarlo directamente (puede ser "Ninguna" o un nombre)
            prerequisitos_str = prerequisitos if prerequisitos and prerequisitos.lower() not in ['ninguna', 'ninguno', ''] else 'Ninguno'
            tiene_prerequisitos = prerequisitos_str != 'Ninguno'
            num_prerequisitos = 1 if tiene_prerequisitos else 0
        elif isinstance(prerequisitos, list):
            # Si es array, unir con comas
            prerequisitos_str = ', '.join(prerequisitos) if prerequisitos else 'Ninguno'
            tiene_prerequisitos = len(prerequisitos) > 0
            num_prerequisitos = len(prerequisitos)
        else:
            prerequisitos_str = 'Ninguno'
            tiene_prerequisitos = False
            num_prerequisitos = 0
        
        # Crear texto estructurado
        texto = f"""Materia: {materia['nombre']}
Código: {materia['codigo']}
Semestre: {materia['semestre']}
Créditos: {materia['creditos']}
Tipología: {materia['tipologia']}
Prerrequisitos: {prerequisitos_str}
"""
        textos.append(texto)
        
        # Crear metadata estructurada
        metadata = {
            'codigo': materia['codigo'],
            'nombre': materia['nombre'],
            'semestre': str(materia['semestre']) if materia['semestre'] is not None else 'null',
            'creditos': str(materia['creditos']),
            'tipologia': materia['tipologia'],
            'tipologia_tipo': _extraer_tipo_tipologia(materia['tipologia']),
            'tipologia_categoria': _extraer_categoria_tipologia(materia['tipologia']),
            'tiene_prerequisitos': tiene_prerequisitos,
            'num_prerequisitos': num_prerequisitos
        }
        metadatas.append(metadata)
    
    return textos, metadatas


def _extraer_tipo_tipologia(tipologia: str) -> str:
    """Extrae el tipo de tipología: OBLIGATORIA, OPTATIVA, etc."""
    tipologia_upper = tipologia.upper()
    if "OBLIGATORIA" in tipologia_upper:
        return "OBLIGATORIA"
    elif "OPTATIVA" in tipologia_upper or "ELECTIVA" in tipologia_upper:
        return "OPTATIVA"
    return "OTRO"


def _extraer_categoria_tipologia(tipologia: str) -> str:
    """Extrae la categoría de tipología: FUNDAMENTAL, DISCIPLINAR, etc."""
    tipologia_upper = tipologia.upper()
    if "FUND." in tipologia_upper or "FUNDAMENTAL" in tipologia_upper:
        return "FUNDAMENTAL"
    elif "DISCIPLINAR" in tipologia_upper:
        return "DISCIPLINAR"
    elif "LENGUA EXTRANJERA" in tipologia_upper:
        return "LENGUA EXTRANJERA"
    elif "TRABAJO DE GRADO" in tipologia_upper:
        return "TRABAJO DE GRADO"
    return "OTRO"


if __name__ == "__main__":
    # Ejemplo de uso
    json_path = "data/documents/malla_curricular_administracion_sistemas_informaticos.json"
    
    textos, metadatas = procesar_malla_curricular(json_path)
    
    print(f"✅ Total de materias procesadas: {len(textos)}\n")
    print("Primeras 3 materias con metadata:")
    print("=" * 50)
    for i in range(min(3, len(textos))):
        print(f"Texto:\n{textos[i]}")
        print(f"Metadata: {metadatas[i]}")
        print("-" * 50)

