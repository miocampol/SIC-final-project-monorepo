# Estructura de Presentación: prismaUNAL

## Chatbot RAG para Administración de Sistemas Informáticos - UNAL Manizales

---

## 📋 **ESTRUCTURA GENERAL DE LA PRESENTACIÓN** (15-20 minutos)

### 1. **Introducción y Contexto** (2-3 min) - Persona 1

### 2. **Arquitectura y Stack Tecnológico** (4-5 min) - Persona 2

### 3. **Implementación Técnica Detallada** (4-5 min) - Persona 3

### 4. **Demo en Vivo** (3-4 min) - Persona 3

### 5. **Conclusiones y Futuro** (2-3 min) - Persona 1

---

## 👤 **DIVISIÓN DE RESPONSABILIDADES**

### **PERSONA 1: Introducción, Problema y Conclusiones**

#### **Sección 1: Introducción y Contexto** (2-3 min)

- **Hook inicial**: "¿Cuántas veces has tenido que buscar información sobre materias, horarios o profesores en múltiples documentos?"
- **Problema identificado**:
  - Estudiantes de ASI necesitan información dispersa en múltiples fuentes
  - Malla curricular (JSON), contenido de materias (PDF), horarios y profesores (CSV)
  - Búsqueda manual consume tiempo y puede generar errores
- **Solución propuesta**: prismaUNAL
  - Chatbot inteligente que centraliza toda la información académica
  - Respuestas rápidas y precisas usando IA
- **Objetivo del proyecto**: Facilitar el acceso a información académica mediante un asistente virtual especializado

#### **Sección 2 (inicio): Arquitectura General** (1-2 min)

- **Arquitectura del sistema**:

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│   ChromaDB  │
│   (React)   │◀─────│   (FastAPI)  │◀─────│  (Vector DB)│
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   OpenAI API │
                     │ (GPT-5-mini) │
                     └──────────────┘
```

- **Componentes principales**:

  - Frontend: React + Vite + TailwindCSS (interfaz de usuario)
  - Backend: FastAPI (API REST, lógica de negocio)
  - ChromaDB: Base de datos vectorial (almacenamiento de embeddings)
  - OpenAI API: LLM y embeddings (inteligencia artificial)

- **Flujo general**:

  1. Usuario hace una pregunta en el frontend
  2. Backend procesa la pregunta
  3. Búsqueda en ChromaDB para encontrar contexto relevante
  4. Generación de respuesta con OpenAI
  5. Respuesta enviada al usuario en tiempo real

- **Conceptos clave a introducir**:
  - RAG (Retrieval-Augmented Generation): combina búsqueda + generación
  - Embeddings: representación vectorial del texto
  - Búsqueda semántica: encontrar información por significado, no solo palabras

#### **Sección 5: Conclusiones y Futuro** (2-3 min)

- **Logros alcanzados**:
  - ✅ Sistema RAG funcional con múltiples fuentes de datos
  - ✅ Interfaz web moderna y responsive
  - ✅ Respuestas rápidas con streaming
  - ✅ Extracción programática para consultas específicas
- **Métricas de éxito**:
  - Integración de 3 fuentes de datos (JSON, PDF, CSV)
  - Respuestas precisas sobre materias, horarios, profesores
  - Tiempo de respuesta optimizado
- **Trabajo futuro**:
  - Implementar memoria de sesión persistente
  - Agregar más fuentes de datos (calendario académico, eventos)
  - Mejorar la precisión con fine-tuning
  - Despliegue en producción

---

### **PERSONA 2: Stack Tecnológico y Procesamiento de Datos**

#### **Sección 2 (continuación): Stack Tecnológico** (2-3 min)

##### **2.1 Tecnologías Utilizadas**

- **Frontend**:
  - React: Framework de JavaScript para UI
  - Vite: Build tool rápido
  - TailwindCSS: Framework de estilos utility-first
- **Backend**:
  - FastAPI: Framework moderno de Python para APIs
  - Python 3.12: Lenguaje de programación
- **Base de Datos y Almacenamiento**:
  - ChromaDB: Base de datos vectorial ligera y open-source
  - SQLite: Para metadata de ChromaDB
- **IA y ML**:
  - OpenAI API: Servicio de IA
  - GPT-5-mini: Modelo de lenguaje para generación
  - text-embedding-3-small: Modelo para embeddings

##### **2.2 Procesamiento de Datos** (2-3 min)

- **Fuentes de datos**:

  1. **JSON (Malla curricular)**:

     - Estructura: código, nombre, créditos, semestre, tipo, prerrequisitos
     - Procesamiento: `procesar_json.py`
     - Metadata: `fuente: 'json'`, `semestre`, `tipo`, `categoria`

  2. **PDF (Contenido de materias)**:

     - Extracción de texto con pypdf
     - Parsing de estructura (código, nombre, contenido)
     - Procesamiento: `procesar_pdf.py`
     - Metadata: `fuente: 'pdf'`, `codigo`, `nombre_materia`

  3. **CSV (Horarios y profesores)**:
     - Manejo de encoding (UTF-8, Latin-1) con detección automática
     - Agrupación por código + grupo
     - Procesamiento: `procesar_csv.py`
     - Metadata: `fuente: 'csv'`, `codigo`, `grupo`, `profesor`

- **Pipeline de ingesta**:

  1. Extracción de texto de cada fuente
  2. Fragmentación (chunking) en segmentos manejables
  3. Generación de embeddings con OpenAI
  4. Almacenamiento en ChromaDB con metadata estructurada
  5. Script unificado: `cargar_chroma.py`

- **Desafíos resueltos**:
  - Encoding de archivos CSV (detección automática)
  - Celdas fusionadas en Excel/CSV
  - Estructura inconsistente en PDF
  - Normalización de datos de diferentes fuentes

##### **2.3 Funcionalidades del Sistema** (1-2 min)

- **Tipos de consultas soportadas**:

  - Información de materias (código, créditos, semestre, prerrequisitos)
  - Contenido de materias
  - Listado de materias por semestre/tipo
  - Horarios y profesores
  - Cantidad de materias por categoría

- **Características especiales**:
  - Streaming de respuestas (Server-Sent Events)
  - Detección inteligente de tipo de consulta
  - Respuestas concisas y precisas
  - Identidad personalizada: prismaUNAL

**Conceptos clave a explicar**:

- Embeddings vectoriales y su importancia
- Búsqueda semántica vs. búsqueda por palabras clave
- Metadata filtering para precisión
- Pipeline ETL (Extract, Transform, Load)

---

### **PERSONA 3: Implementación Técnica Detallada y Demo**

#### **Sección 3: Implementación Técnica Detallada** (4-5 min)

##### **3.1 Sistema RAG Híbrido** (2 min)

- **Enfoque híbrido: Programático + LLM**

  **Extracción programática** (sin LLM, más rápido):

  - Consultas sobre cantidad de materias → Respuestas predefinidas
  - Consultas específicas de código → Regex directo
  - Ventajas: más rápido, más confiable, sin costo de API
  - Ejemplo: "¿Cuántas materias fundamentales obligatorias hay?" → Respuesta directa

  **Generación con LLM** (para consultas complejas):

  - Consultas que requieren razonamiento y contexto
  - Respuestas naturales y contextualizadas
  - Uso de contexto recuperado de ChromaDB
  - Ejemplo: "¿Cuál es el contenido de Fundamentos de Programación?" → LLM con contexto del PDF

- **Flujo de decisión**:
  1. Detectar tipo de consulta (saludo, cantidad, específica, compleja)
  2. Si es cantidad → respuesta predefinida
  3. Si es específica → extracción programática
  4. Si es compleja → búsqueda en ChromaDB + LLM

##### **3.2 Optimizaciones Implementadas** (1.5 min)

- **Caché global del vectorstore**:

  - Evita recrear ChromaDB en cada consulta
  - Mejora significativa en tiempo de respuesta
  - Implementación: variable global `_vectorstore_cache`

- **`k` dinámico según tipo de consulta**:

  - Consultas específicas: `k=3` (menos documentos, más precisión)
  - Consultas de listado: `k=10` o más (más documentos, más completitud)
  - Consultas sobre profesores/horarios: `k=20` (todos los grupos)

- **Filtrado por metadata**:

  - Filtra por semestre, tipo, categoría antes de buscar
  - Reduce ruido en los resultados
  - Mejora precisión de respuestas

- **Streaming con Server-Sent Events (SSE)**:
  - Respuestas en tiempo real, palabra por palabra
  - Mejor experiencia de usuario
  - Implementación: generador Python + SSE en FastAPI

##### **3.3 Detalles de Implementación** (1 min)

- **Detección inteligente de consultas**:

  - Regex patterns para identificar tipo de pregunta
  - Clasificación: saludo, cantidad, listado, específica, compleja
  - Extracción de parámetros (nombre de materia, semestre, etc.)

- **Manejo de contexto**:

  - Búsqueda semántica en ChromaDB
  - Construcción de prompt con contexto relevante
  - Instrucciones al LLM para usar SOLO el contexto proporcionado

- **Manejo de errores**:
  - Try-catch en endpoints
  - Logging detallado para debugging
  - Respuestas de error amigables al usuario

##### **3.4 Frontend Técnico** (0.5 min)

- **Implementación de streaming**:

  - EventSource API para recibir SSE
  - Actualización en tiempo real del DOM
  - Manejo de estados (cargando, error, completado)

- **Arquitectura del frontend**:
  - Componentes React modulares
  - Servicio API separado
  - Estado local para mensajes

**Conceptos técnicos a explicar**:

- Enfoque híbrido (programático + LLM) y cuándo usar cada uno
- Filtrado por metadata en ChromaDB
- Streaming con Server-Sent Events
- Optimización de `k` para diferentes tipos de consultas
- Caché para mejorar rendimiento

---

### **SECCIÓN 4: DEMO EN VIVO** (3-4 min) - Persona 3

**Estrategia de demo** (Persona 3):

1. **Abrir la aplicación** y mostrar la interfaz
2. **Explicar qué está pasando** mientras se hacen las preguntas (opcional: mostrar logs del backend)
3. **Hacer las preguntas** y destacar aspectos técnicos

**Preguntas para demostrar** (con explicación técnica):

1. **"Hola, ¿quién eres?"**

   - → Identidad del chatbot
   - **Explicar**: Respuesta directa del LLM usando el prompt del sistema, sin búsqueda en ChromaDB

2. **"¿Cuántas materias fundamentales obligatorias hay?"**

   - → Extracción programática
   - **Explicar**: Detección de consulta de cantidad, respuesta predefinida sin LLM, más rápido

3. **"¿Qué profesores dan Cálculo Diferencial?"**

   - → Búsqueda en CSV con metadata
   - **Explicar**: Búsqueda semántica en ChromaDB con filtro por código, `k=20` para obtener todos los grupos, metadata de CSV

4. **"¿Cuál es el contenido de Fundamentos de Programación?"**

   - → Búsqueda en PDF
   - **Explicar**: Embedding de la pregunta, búsqueda en ChromaDB, recuperación de contexto del PDF, generación con LLM

5. **"¿Cuáles son las materias del primer semestre?"**
   - → Listado con filtro
   - **Explicar**: Filtro por metadata (semestre=1), búsqueda en ChromaDB, respuesta estructurada

**Puntos a destacar durante la demo**:

- ✅ **Velocidad de respuesta**: Streaming en tiempo real
- ✅ **Precisión**: Información basada en documentos reales
- ✅ **Streaming**: Mostrar cómo aparece palabra por palabra
- ✅ **Diferentes tipos de consultas**: Programática vs. LLM
- ✅ **Fuentes de datos**: Explicar de dónde viene cada respuesta (JSON, PDF, CSV)

**Tips para la demo**:

- Tener el código abierto para mostrar si preguntan detalles
- Mostrar logs del backend si es posible (opcional)
- Explicar brevemente qué está pasando detrás de escena
- Destacar las optimizaciones (caché, k dinámico, filtros)

---

## 🎯 **CONCEPTOS CLAVE A EXPLICAR**

### **Para la audiencia técnica**:

1. **RAG (Retrieval-Augmented Generation)**

   - Qué es y por qué es mejor que solo LLM
   - Cómo reduce alucinaciones
   - Flujo: Query → Embedding → Búsqueda → Contexto → LLM

2. **Embeddings y Búsqueda Semántica**

   - Representación vectorial del texto
   - Similitud coseno
   - Ventajas sobre búsqueda por palabras clave

3. **Vector Databases (ChromaDB)**

   - Almacenamiento eficiente de embeddings
   - Búsqueda por similitud
   - Filtrado por metadata

4. **Enfoque Híbrido**
   - Extracción programática vs. LLM
   - Cuándo usar cada uno
   - Optimización de costos y velocidad

### **Para la audiencia general**:

1. **Problema resuelto**: Centralización de información académica
2. **Solución**: Chatbot inteligente con IA
3. **Beneficios**: Rapidez, precisión, accesibilidad
4. **Tecnología**: IA conversacional + búsqueda inteligente

---

## 📊 **DIAGRAMA DE FLUJO PARA LA PRESENTACIÓN**

```
Usuario pregunta
    ↓
Frontend (React) → POST /chat/stream
    ↓
Backend (FastAPI) → responder_con_rag_stream()
    ↓
¿Es pregunta académica?
    ├─ NO → LLM directo (saludos)
    └─ SÍ → Buscar contexto en ChromaDB
            ↓
        ¿Tipo de consulta?
            ├─ Cantidad → Respuesta predefinida
            ├─ Específica → Extracción programática
            └─ Compleja → LLM con contexto
                ↓
        Generar respuesta (streaming)
            ↓
Frontend muestra respuesta en tiempo real
```

---

## 💡 **TIPS PARA LA PRESENTACIÓN**

### **Preparación**:

- ✅ Probar la demo varias veces antes
- ✅ Tener preguntas de respaldo preparadas
- ✅ Preparar respuestas a preguntas frecuentes
- ✅ Revisar que el servidor esté corriendo

### **Durante la presentación**:

- ✅ Mantener contacto visual con la audiencia
- ✅ Explicar conceptos técnicos de forma simple
- ✅ Usar analogías cuando sea posible
- ✅ Mostrar entusiasmo por el proyecto

### **Preguntas frecuentes (preparar respuestas)**:

1. **¿Por qué RAG y no solo un LLM?**

   - RAG asegura que las respuestas estén basadas en documentos reales
   - Reduce alucinaciones
   - Permite actualizar información sin reentrenar

2. **¿Cómo se actualiza la información?**

   - Re-ejecutar `cargar_chroma.py` con nuevos datos
   - ChromaDB se actualiza automáticamente

3. **¿Cuál es el costo de usar OpenAI?**

   - GPT-5-mini es económico
   - Embeddings son muy baratos
   - Se puede optimizar con caché

4. **¿Funciona offline?**
   - No, requiere conexión a OpenAI API
   - ChromaDB está local, pero embeddings y LLM son en la nube

---

## 📝 **CHECKLIST PRE-PRESENTACIÓN**

- [ ] Backend corriendo (`python main.py`)
- [ ] Frontend corriendo (`npm run dev`)
- [ ] ChromaDB cargado con datos
- [ ] API key de OpenAI configurada
- [ ] Demo probada con todas las preguntas
- [ ] Slides/diapositivas preparadas (opcional)
- [ ] Código abierto en IDE para mostrar si preguntan
- [ ] Logs visibles para mostrar el proceso

---

## 🎬 **ESTRUCTURA DE SLIDES (Opcional)**

1. **Slide 1**: Título - prismaUNAL
2. **Slide 2**: Problema y motivación
3. **Slide 3**: Solución propuesta
4. **Slide 4**: Arquitectura del sistema
5. **Slide 5**: Stack tecnológico
6. **Slide 6**: Flujo de datos
7. **Slide 7**: Funcionalidades
8. **Slide 8**: Demo (pantalla compartida)
9. **Slide 9**: Conclusiones
10. **Slide 10**: Trabajo futuro

---

## 🔗 **ENLACES ÚTILES**

- Repositorio del proyecto
- Documentación de FastAPI
- Documentación de ChromaDB
- OpenAI API documentation

---

**¡Éxito en la presentación! 🚀**
