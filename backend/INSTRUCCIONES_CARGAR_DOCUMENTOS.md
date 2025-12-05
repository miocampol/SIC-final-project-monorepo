# Instrucciones para Cargar Documentos al RAG

El sistema RAG ahora soporta **dos formatos de documentos**:

1. **JSON** - Malla curricular con información básica (código, nombre, semestre, créditos, tipología, prerrequisitos)
2. **PDF** - Documentos detallados con información completa (código, nombre, descripción, contenido)

## 📋 Requisitos Previos

1. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

2. Asegúrate de tener tu archivo `.env` con `OPENAI_API_KEY` configurada.

## 📁 Estructura de Archivos

Coloca tus documentos en la carpeta `data/documents/`:

```
data/documents/
  ├── malla_curricular_administracion_sistemas_informaticos.json  (opcional)
  └── materias.pdf  (opcional - ajusta el nombre en cargar_chroma.py)
```

## 🔄 Cargar Documentos

### Opción 1: Solo JSON

Si solo tienes el JSON, colócalo en `data/documents/` y ejecuta:

```bash
python cargar_chroma.py
```

### Opción 2: Solo PDF

Si solo tienes el PDF:

1. Coloca tu PDF en `data/documents/materias.pdf` (o ajusta la ruta en `cargar_chroma.py`)
2. Ejecuta:

```bash
python cargar_chroma.py
```

### Opción 3: Ambos Formatos (Recomendado)

Si tienes ambos formatos:

1. Coloca el JSON en `data/documents/malla_curricular_administracion_sistemas_informaticos.json`
2. Coloca el PDF en `data/documents/materias.pdf` (o ajusta la ruta)
3. Ejecuta:

```bash
python cargar_chroma.py
```

El sistema cargará **ambos formatos** y los combinará en el mismo vector store.

## 📄 Formato del PDF

El procesador de PDF intenta detectar automáticamente la estructura de tus materias. Busca patrones como:

```
Código: [CÓDIGO]
Nombre: [NOMBRE]
Descripción: [DESCRIPCIÓN]
Contenido: [CONTENIDO]
```

Si tu PDF tiene un formato diferente, puedes ajustar los patrones en `procesar_pdf.py` en la función `_extraer_materias_del_texto()`.

## ⚙️ Personalizar la Ruta del PDF

Si tu PDF tiene otro nombre o está en otra ubicación, edita `cargar_chroma.py` y cambia la variable `pdf_path`:

```python
pdf_path = "data/documents/tu_archivo.pdf"  # Cambia aquí
```

## 🔍 Verificar la Carga

Después de ejecutar `cargar_chroma.py`, verás un resumen:

- Cantidad de materias del JSON procesadas
- Cantidad de materias del PDF procesadas
- Total de documentos cargados

## ⚠️ Notas Importantes

1. **El vector store se recrea cada vez**: Cada vez que ejecutas `cargar_chroma.py`, se elimina el vector store anterior y se crea uno nuevo. Esto asegura que los cambios en los documentos se reflejen.

2. **Metadata diferenciada**: Los documentos del PDF tienen `'fuente': 'pdf'` en su metadata, mientras que los del JSON no tienen este campo. Esto permite distinguirlos si es necesario.

3. **Semestre automático**: El procesador intenta extraer el semestre del código o nombre de la materia, pero si no lo encuentra, no se incluirá en la metadata.

4. **Ajustar patrones**: Si tu PDF tiene un formato muy específico, es posible que necesites ajustar los patrones de extracción en `procesar_pdf.py`.

## 🚀 Después de Cargar

Una vez cargados los documentos, puedes usar el chatbot normalmente. El sistema RAG buscará información tanto en los documentos del JSON como en los del PDF.
