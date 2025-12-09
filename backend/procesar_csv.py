"""
Procesador para archivos CSV con información de asignaturas (horarios, profesores, salones)
Extrae información de horarios, profesores y salones por grupo
"""
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple
import chardet


def detectar_encoding(archivo_path: str) -> str:
    """Detecta el encoding del archivo CSV"""
    with open(archivo_path, 'rb') as f:
        raw_data = f.read()
        resultado = chardet.detect(raw_data)
        encoding = resultado['encoding']
        print(f"🔍 Encoding detectado: {encoding} (confianza: {resultado['confidence']:.2%})")
        return encoding or 'utf-8'


def corregir_encoding_texto(texto: str) -> str:
    """Intenta corregir problemas de encoding en el texto"""
    if not texto:
        return texto
    
    # Intentar corregir encoding doble: texto que fue UTF-8 pero se leyó como latin-1
    try:
        # Si el texto tiene caracteres como 'Ã³', intentar corregirlo
        texto_corregido = texto.encode('latin-1').decode('utf-8')
        return texto_corregido
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Si falla, devolver el texto original
        return texto


def normalizar_nombre_columna(nombre: str) -> str:
    """Normaliza nombres de columnas para manejar problemas de encoding"""
    nombre_limpio = nombre.strip()
    
    # Detectar patrones comunes con problemas de encoding usando coincidencias parciales
    nombre_lower = nombre_limpio.lower()
    
    # 'CÃ³dig', 'C√≥dig', 'Códig' -> 'Código'
    if 'codig' in nombre_lower or ('c' in nombre_lower and ('√' in nombre_limpio or 'Ã' in nombre_limpio)):
        return 'Código'
    
    # 'SalÃ³', 'Sal√≥', 'Saló' -> 'Salón'
    if 'sal' in nombre_lower and ('√' in nombre_limpio or 'ó' in nombre_limpio or 'Ã' in nombre_limpio or len(nombre_limpio) <= 5):
        return 'Salón'
    
    # Mapeo exacto de nombres comunes con problemas de encoding
    mapeo = {
        'Códig': 'Código',
        'CÃ³dig': 'Código',  # Agregado para el caso actual
        'CÃ³digo': 'Código',
        'Codigo': 'Código',
        'Nombre Asignatura': 'Nombre Asignatura',
        'Profesor': 'Profesor',
        'Grupo': 'Grupo',
        'Horario Completo': 'Horario Completo',
        'Saló': 'Salón',
        'SalÃ³': 'Salón',  # Agregado para el caso actual
        'SalÃ³n': 'Salón',
        'Salon': 'Salón',
    }
    
    return mapeo.get(nombre_limpio, nombre_limpio)


def procesar_csv_horarios(csv_path: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Procesa un archivo CSV con información de horarios, profesores y salones.
    
    Columnas esperadas:
    - Código
    - Nombre Asignatura
    - Profesor
    - Grupo
    - Horario Completo
    - Salón
    
    Args:
        csv_path: Ruta al archivo CSV
        
    Returns:
        Tupla con (textos, metadatas) donde:
        - textos: Lista de textos estructurados, uno por grupo de materia
        - metadatas: Lista de diccionarios con metadata de cada grupo
    """
    csv_file = Path(csv_path)
    
    if not csv_file.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {csv_path}")
    
    # Detectar encoding
    encoding = detectar_encoding(csv_path)
    
    # Leer CSV con diferentes encodings si es necesario
    filas = []
    columnas_originales = []
    encoding_usado = None
    delimiter_usado = None
    
    # Intentar diferentes encodings, priorizando los más comunes para CSV en español
    encodings_intentados = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1', encoding]
    
    for enc in encodings_intentados:
        try:
            with open(csv_file, 'r', encoding=enc, newline='') as f:
                # Detectar delimitador
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(f, delimiter=delimiter)
                filas = list(reader)
                if filas:
                    columnas_originales = list(filas[0].keys())
                    encoding_usado = enc
                    delimiter_usado = delimiter
                    print(f"✅ CSV leído exitosamente con encoding: {enc}, delimitador: '{delimiter}'")
                    break
        except (UnicodeDecodeError, csv.Error) as e:
            print(f"⚠️  Error con encoding {enc}: {e}")
            continue
    
    if not filas:
        raise ValueError(f"No se pudo leer el CSV con ningún encoding: {encodings_intentados}")
    
    # Normalizar nombres de columnas
    columnas_normalizadas = {col: normalizar_nombre_columna(col) for col in columnas_originales}
    print(f"📋 Columnas originales: {columnas_originales}")
    print(f"📋 Columnas normalizadas: {list(columnas_normalizadas.values())}")
    
    # Agrupar por código y grupo (puede haber múltiples horarios/salones por grupo)
    grupos_agrupados: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    
    for idx, fila in enumerate(filas):
        # Normalizar nombres de columnas en la fila
        fila_normalizada = {columnas_normalizadas.get(k, k): v for k, v in fila.items()}
        
        codigo = fila_normalizada.get('Código', '').strip()
        nombre = fila_normalizada.get('Nombre Asignatura', '').strip()
        profesor = fila_normalizada.get('Profesor', '').strip()
        grupo = fila_normalizada.get('Grupo', '').strip()
        horario = fila_normalizada.get('Horario Completo', '').strip()
        salon = fila_normalizada.get('Salón', '').strip()
        
        # Intentar corregir problemas de encoding en los valores
        codigo = corregir_encoding_texto(codigo)
        nombre = corregir_encoding_texto(nombre)
        profesor = corregir_encoding_texto(profesor)
        salon = corregir_encoding_texto(salon)
        
        # Debug: mostrar primera fila procesada
        if idx == 0:
            print(f"🔍 Primera fila procesada:")
            print(f"   Columnas normalizadas disponibles: {list(fila_normalizada.keys())}")
            print(f"   Código: '{codigo}' | Nombre: '{nombre}' | Grupo: '{grupo}'")
        
        # Limpiar valores vacíos o inválidos
        if not codigo or not nombre:
            continue
        
        # Limpiar caracteres extraños del profesor (si hay caracteres de control)
        if profesor:
            profesor = ''.join(char for char in profesor if ord(char) >= 32 or char in '\n\r\t').strip()
        
        # Clave única: código + nombre + grupo
        clave = (codigo, nombre, grupo)
        
        if clave not in grupos_agrupados:
            grupos_agrupados[clave] = {
                'codigo': codigo,
                'nombre': nombre,
                'grupo': grupo,
                'profesores': [],
                'horarios': [],
                'salones': []
            }
        
        # Agregar información si no está vacía
        if profesor and profesor not in grupos_agrupados[clave]['profesores']:
            grupos_agrupados[clave]['profesores'].append(profesor)
        
        if horario and horario not in grupos_agrupados[clave]['horarios']:
            grupos_agrupados[clave]['horarios'].append(horario)
        
        if salon and salon not in grupos_agrupados[clave]['salones']:
            grupos_agrupados[clave]['salones'].append(salon)
    
    textos = []
    metadatas = []
    
    for (codigo, nombre, grupo), info in grupos_agrupados.items():
        # Crear texto estructurado
        texto = f"""Materia: {nombre}
Código: {codigo}
Grupo: {info['grupo']}"""
        
        if info['profesores']:
            profesores_str = ', '.join(info['profesores'])
            texto += f"\nProfesor(es): {profesores_str}"
        
        if info['horarios']:
            horarios_str = '; '.join(info['horarios'])
            texto += f"\nHorario: {horarios_str}"
        
        if info['salones']:
            salones_str = '; '.join(info['salones'])
            texto += f"\nSalón(es): {salones_str}"
        
        textos.append(texto)
        
        # Crear metadata
        metadata = {
            'codigo': codigo,
            'nombre': nombre,
            'grupo': info['grupo'],
            'fuente': 'csv',  # Para distinguir del JSON y PDF
            'tiene_profesor': len(info['profesores']) > 0,
            'tiene_horario': len(info['horarios']) > 0,
            'tiene_salon': len(info['salones']) > 0,
            'num_profesores': len(info['profesores']),
            'num_horarios': len(info['horarios']),
            'num_salones': len(info['salones'])
        }
        
        # Agregar información adicional a metadata para búsquedas
        if info['profesores']:
            metadata['profesores'] = '; '.join(info['profesores'])
        if info['horarios']:
            metadata['horarios'] = '; '.join(info['horarios'])
        if info['salones']:
            metadata['salones'] = '; '.join(info['salones'])
        
        metadatas.append(metadata)
    
    return textos, metadatas


if __name__ == "__main__":
    # Ejemplo de uso
    csv_path = "data/documents/asignaturas_formato.csv"
    
    textos, metadatas = procesar_csv_horarios(csv_path)
    
    print(f"\n✅ Total de grupos procesados: {len(textos)}\n")
    print("Primeros 3 grupos con metadata:")
    print("=" * 50)
    for i in range(min(3, len(textos))):
        print(f"Texto:\n{textos[i]}")
        print(f"Metadata: {metadatas[i]}")
        print("-" * 50)

