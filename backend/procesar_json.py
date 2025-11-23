"""
Procesador genérico para documentos JSON de malla curricular
Convierte JSON a texto estructurado para RAG
"""
import json
from pathlib import Path
from typing import List, Dict, Any


def procesar_malla_curricular(json_path: str) -> List[str]:
    """
    Procesa un archivo JSON de malla curricular y lo convierte en textos estructurados
    
    Args:
        json_path: Ruta al archivo JSON
        
    Returns:
        Lista de textos estructurados, uno por materia
    """
    json_file = Path(json_path)
    
    if not json_file.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {json_path}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        materias = json.load(f)
    
    textos = []
    for materia in materias:
        # Crear texto estructurado
        texto = f"""Materia: {materia['nombre']}
Código: {materia['codigo']}
Semestre: {materia['semestre']}
Créditos: {materia['creditos']}
Tipología: {materia['tipologia']}
Prerrequisitos: {', '.join(materia['prerequisitos']) if materia['prerequisitos'] else 'Ninguno'}
"""
        textos.append(texto)
    
    return textos


if __name__ == "__main__":
    # Ejemplo de uso
    json_path = "data/documents/malla_curricular_administracion_sistemas_informaticos (1).json"
    
    textos = procesar_malla_curricular(json_path)
    
    print(f"✅ Total de materias procesadas: {len(textos)}\n")
    print("Primeras 3 materias:")
    print("=" * 50)
    for texto in textos[:3]:
        print(texto)
        print("-" * 50)

