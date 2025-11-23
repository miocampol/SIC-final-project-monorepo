"""
Script simple para procesar el JSON de malla curricular
y convertirlo en texto estructurado para RAG
"""
import json
from pathlib import Path

# Cargar el JSON
json_path = Path("data/documents/malla_curricular_administracion_sistemas_informaticos (1).json")

with open(json_path, 'r', encoding='utf-8') as f:
    materias = json.load(f)

print(f"Total de materias: {len(materias)}\n")

# Convertir cada materia en texto estructurado
textos = []
for materia in materias[:5]:  # Mostrar solo las primeras 5
    # Crear texto estructurado
    texto = f"""Materia: {materia['nombre']}
Código: {materia['codigo']}
Semestre: {materia['semestre']}
Créditos: {materia['creditos']}
Tipología: {materia['tipologia']}
Prerrequisitos: {', '.join(materia['prerequisitos']) if materia['prerequisitos'] else 'Ninguno'}
"""
    textos.append(texto)
    print(texto)
    print("-" * 50)

print(f"\n✅ Procesadas {len(textos)} materias (mostrando solo primeras 5)")
print(f"📝 Total de materias en el archivo: {len(materias)}")

