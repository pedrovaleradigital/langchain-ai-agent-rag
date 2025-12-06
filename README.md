# Pedro WhatsApp AI Agent

[🇪🇸 Español](#español) | [🇬🇧 English](#english)

---

## Español

Sistema inteligente de chatbot para WhatsApp con RAG (Retrieval-Augmented Generation), integración con Chatwoot y capacidades avanzadas de procesamiento asíncrono.

**Versión:** 2.1 - Background Tasks + Prompts Duales + Humanizador de Respuestas

---

### Descripción

Este proyecto implementa un agente de IA conversacional que opera sobre WhatsApp a través de Chatwoot, utilizando LangChain para orquestación de agentes y OpenAI GPT-4o-mini como modelo de lenguaje. El sistema cuenta con:

- **RAG avanzado** con Supabase como vector store
- **Procesamiento asíncrono** mediante FastAPI Background Tasks
- **Sistema dual de prompts** intercambiables dinámicamente
- **Humanizador de respuestas** - División inteligente de mensajes largos
- **Gestión inteligente de conversaciones** con Redis y Supabase
- **Detección automática** de solicitudes de atención humana
- **Soporte para intervención manual** sin perder contexto
- **Sistema anti-traslape** - Prevención de mensajes mezclados

---

### Características Principales

#### Core Features
- Sistema RAG (Retrieval-Augmented Generation) con embeddings de OpenAI
- Agente LangChain con herramientas personalizadas
- Integración completa con Chatwoot para WhatsApp Business
- Base de datos vectorial con Supabase (pgvector)
- Historial persistente de conversaciones

#### Nuevas Funcionalidades (v2.0)
- **Background Tasks asíncronos** - Procesamiento sin timeouts (< 1s de respuesta)
- **Prompts duales** - "Filósofo" vs "Conversacional" intercambiables vía webhook
- **Filtrado inteligente de historial** - Previene duplicación de mensajes
- **Soporte para mensajes manuales** - Intervención humana con contexto preservado
- **Lock de procesamiento** - Previene procesamiento duplicado con Redis
- **Acumulación de mensajes** - Buffer Redis con TTL configurable

#### Innovaciones (v2.1) 🆕
- **Humanizador de respuestas** - División automática de respuestas largas en múltiples mensajes
- **Delays inteligentes** - Simulación de escritura humana entre mensajes (1-3s)
- **Sistema anti-traslape** - Protección contra mensajes mezclados
- **Auto-relanzamiento** - Procesamiento automático de mensajes pendientes
- **Lock dinámico** - TTL ajustado según longitud de respuesta

#### Gestión Avanzada
- Control automático de etiquetas (atiende-ia / atiende-humano)
- Detección de solicitud de asesor humano con múltiples patrones
- Filtrado automático de mensajes de grupos
- Clasificación de mensajes outgoing (bot vs manual)

---

### Tech Stack

#### Backend & Framework
- **Python 3.x**
- **FastAPI** - Framework web con soporte para Background Tasks
- **Uvicorn** - Servidor ASGI de alto rendimiento

#### IA & Machine Learning
- **LangChain** - Framework de orquestación de agentes
- **OpenAI GPT-4o-mini** - Modelo de lenguaje
- **OpenAI Embeddings** - text-embedding-ada-002 (1536 dimensiones)

#### Bases de Datos
- **Supabase (PostgreSQL + pgvector)** - Vector store y historial de conversaciones
- **Redis Cloud** - Buffer de mensajes y sistema de locks

#### Integraciones
- **Chatwoot** - Plataforma de mensajería (WhatsApp Business API)
- **Google Sheets** - Registro de leads (opcional)
- **Gmail API** - Envío de correos (opcional)
- **Google Calendar** - Agendamiento de reuniones (opcional)

---

### Requisitos Previos

#### Software
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

#### Servicios Cloud (con cuentas creadas)
- Cuenta de OpenAI con API Key
- Instancia de Supabase configurada con pgvector
- Instancia de Redis Cloud
- Cuenta de Chatwoot con WhatsApp conectado
- (Opcional) Credenciales de Google Cloud Platform para servicios de Google

---

### Instalación

#### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd "Project-Clase04-Langchain-RAG-Chatwood - cloud v2"
```

#### 2. Instalar dependencias

```bash
cd src
pip install -r requirements.txt
```

**Dependencias principales:**
- `langchain`, `langchain-core`, `langchain-community`, `langchain-openai`
- `openai`
- `fastapi`, `uvicorn[standard]`
- `supabase>=2.3.0`, `vecs>=0.4.0`
- `redis>=5.0.0`
- `python-dotenv`, `pytz`, `httpx`, `requests`

#### 3. Configurar base de datos Supabase

Ejecutar el script SQL de configuración para crear las tablas necesarias:

```sql
-- Ver archivo: setup_supabase_fresh.sql
-- Crea tablas: chat_history_teknik, documents_langchain_teknik
-- Configura función RPC para búsqueda vectorial
```

#### 4. Cargar documentos al RAG (opcional)

```bash
cd src/RAG
python rag.py
```

Esto cargará los PDFs de la carpeta `Base_de_Conocimientos/` a Supabase como vectores.

---

### Configuración

#### Archivo `.env`

Crear el archivo `src/.env` con las siguientes variables:

```bash
# ============================================
# OpenAI API
# ============================================
OPENAI_API_KEY=sk-proj-...

# ============================================
# Chatwoot
# ============================================
CHATWOOT_BASE_URL=https://tu-instancia.chatwoot.com/
CHATWOOT_ACCOUNT_ID=1
CHATWOOT_API_ACCESS_TOKEN=...

# ============================================
# Supabase
# ============================================
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_KEY=...

# ============================================
# Redis Cloud
# ============================================
REDIS_HOST=redis-xxxxx.cloud.redislabs.com
REDIS_PORT=13530
REDIS_DB=0
REDIS_PASSWORD=...
MESSAGE_ACCUMULATION_TTL=15

# ============================================
# Sistema de Prompts (NUEVO en v2.0)
# ============================================
PROMPT_TYPE=conversacional  # Opciones: "filosofo" | "conversacional"

# ============================================
# Google Services (OPCIONAL)
# ============================================
GOOGLE_SHEET_ID=...
GOOGLE_SHEET_NAME=Interesados
GOOGLE_SERVICE_ACCOUNT_PATH=/ruta/a/credentials.json
APP_PASSWORD_GMAIL=...
EMAIL_REMITENTE=tu-email@gmail.com
```

**IMPORTANTE:**
- El archivo `.env` debe estar en la carpeta `src/`, NO en la raíz
- Nunca commitear `.env` a Git (ya está en `.gitignore`)

---

### Uso

#### Iniciar el servidor

##### Opción 1: Desde `src/` (recomendado)

```bash
cd src
python -m uvicorn app:app --host 0.0.0.0 --port 5005 --reload
```

##### Opción 2: Ejecución directa

```bash
cd src
python app.py
```

El servidor estará disponible en: `http://localhost:5005`

#### Endpoints principales

##### `POST /chatbot/webhook`
Recibe webhooks de Chatwoot con mensajes de WhatsApp.

**Funcionalidades:**
- Validación de mensajes
- Acumulación en Redis
- Lanzamiento de background tasks
- Control de etiquetas
- Detección de mensajes manuales

##### `POST /prompt/webhook` (NUEVO)
Cambia el tipo de prompt dinámicamente.

**Ejemplo:**
```bash
curl -X POST http://localhost:5005/prompt/webhook \
  -H "Content-Type: application/json" \
  -d '{"prompt_type": "filosofo"}'
```

**Respuesta:**
```json
{
  "status": "success",
  "message": "Prompt actualizado a 'filosofo'",
  "current_prompt_type": "filosofo"
}
```

##### `GET /health`
Health check para monitoreo.

#### Configurar webhook en Chatwoot

1. Ir a Settings > Integrations > Webhooks
2. Crear nuevo webhook con URL: `http://tu-servidor:5005/chatbot/webhook`
3. Seleccionar eventos: `message_created`
4. Guardar

#### Sistema de Prompts

El sistema soporta dos tipos de prompts intercambiables:

##### Prompt "Filósofo"
- Responde con frases célebres inspiradoras
- Incluye autor de la frase
- Menciona que Pedro responderá pronto
- Ideal para respuestas automáticas fuera de horario

**Ejemplo:**
```
"La noche es más pura que el día; es mejor para pensar, amar y soñar." - (Eça de Queiroz)

En breve te responderá Pedro, Juan. 👋
```

##### Prompt "Conversacional"
- Asistente profesional con acceso a RAG
- Respuestas conversacionales y contextuales
- Usa base de conocimientos
- Ideal para atención durante horario laboral

**Cambiar prompt:**
- Via `.env`: `PROMPT_TYPE=conversacional`
- Via webhook: `POST /prompt/webhook` (sin reiniciar servicio)

---

### Estructura del Proyecto

```
src/
├── .env                          # Variables de entorno (NO COMMITEAR)
├── app.py                        # Aplicación FastAPI principal
├── agent.py                      # Agente LangChain con prompts duales
├── tools.py                      # Herramientas del agente
├── requirements.txt              # Dependencias del proyecto
│
├── bot/
│   └── ai_bot.py                 # Sistema RAG con Supabase
│
├── services/
│   └── chatwoot.py               # Cliente API de Chatwoot
│
├── utils/
│   ├── db_utils.py               # Gestión de Supabase (historial)
│   ├── redis_utils.py            # Gestión de Redis (buffer + locks)
│   ├── envio_correo.py           # Herramienta de envío de emails
│   ├── registro_google_sheet.py  # Herramienta de Google Sheets
│   └── agenda_reunion_corporativa.py  # Herramienta de agendamiento
│
└── RAG/
    ├── rag.py                    # Script de carga de documentos
    └── Base_de_Conocimientos/    # PDFs para el RAG
        └── *.pdf
```

#### Archivos de configuración

- `Dockerfile.dev` / `Dockerfile.prod` - Containerización
- `cloudbuild.yaml` - CI/CD para Google Cloud
- `service.yaml` - Configuración de Cloud Run
- `setup_supabase_fresh.sql` - Setup de base de datos

---

### Flujo de Datos

```
Usuario envía mensaje → Chatwoot Webhook → FastAPI
    ↓
Validaciones (grupos, etiquetas, tipo de mensaje)
    ↓
¿Solicita asesor humano? → Cambiar etiquetas → FIN
    ↓
Guardar en Supabase + Acumular en Redis
    ↓
Lanzar Background Task (5s) → Retornar 200 OK
    ↓
[Background Task]
    ↓
Esperar 5s → Recuperar buffer Redis + Historial Supabase
    ↓
Procesar con Agente (según PROMPT_TYPE)
    ↓
Generar respuesta → Guardar en Supabase → Enviar a Chatwoot
    ↓
Usuario recibe mensaje
```

---

### Características Técnicas Avanzadas

#### Background Tasks
- Procesamiento asíncrono con FastAPI
- Respuesta inmediata al webhook (< 1s)
- Wait time configurable (default 5s)
- Auto-limpieza de recursos

#### Gestión de Mensajes
- Buffer Redis con TTL de 15s + 5s extra
- Concatenación automática de mensajes rápidos
- Filtrado inteligente de historial (exclude_pending)
- Clasificación de mensajes (user/bot/manual)

#### Sistema de Locks
- Previene procesamiento duplicado
- Lock en Redis por chat_id
- TTL automático (15s)
- Auto-liberación al finalizar

#### RAG (Retrieval-Augmented Generation)
- Embeddings: OpenAI text-embedding-ada-002
- Chunk size: 1024 caracteres
- Chunk overlap: 250 caracteres
- Retriever K: 12 documentos
- Vector store: Supabase pgvector

---

### 🎭 Sistema Humanizador de Respuestas (v2.1)

#### Problema Resuelto

Las respuestas largas del agente IA (por ejemplo, listas con 5-7 items) se enviaban en un solo mensaje, lo que resultaba en:
- Bloques de texto difíciles de leer en WhatsApp
- Experiencia poco natural (los humanos no escriben mensajes tan largos de una vez)
- Pérdida de atención del usuario

#### Solución Implementada

El **Sistema Humanizador** divide automáticamente las respuestas largas en múltiples mensajes más cortos, simulando cómo un humano respondería naturalmente.

#### Características

##### 1. División Inteligente de Mensajes
```python
# Estrategia de división multi-nivel:
# 1. Dividir por párrafos (doble salto de línea)
# 2. Si un párrafo es muy largo, dividir por líneas simples
# 3. Si una línea es muy larga, dividir por puntos
# 4. Longitud máxima configurable (default: 500 caracteres)
```

**Ejemplo de división:**
```
Mensaje original (980 caracteres):
"Pedro tiene habilidades sólidas en análisis de datos, que incluyen:
1. Herramientas de Análisis: Experiencia en...
2. Visualización de Datos: Capacidad para...
3. Interpretación de Datos: Habilidad para...
4. Análisis Estadístico: Conocimientos en...
5. ETL: Experiencia en procesos..."

Se divide en 7 mensajes:
→ Mensaje 1: "Pedro tiene habilidades sólidas..."
→ Mensaje 2: "1. Herramientas de Análisis..."
→ Mensaje 3: "2. Visualización de Datos..."
→ Mensaje 4: "3. Interpretación de Datos..."
→ Mensaje 5: "4. Análisis Estadístico..."
→ Mensaje 6: "5. ETL..."
→ Mensaje 7: "Si necesitas más detalles..."
```

##### 2. Delays Inteligentes Entre Mensajes

Cada mensaje tiene un **delay calculado dinámicamente** para simular el tiempo de escritura humana:

```python
# Fórmula del delay
delay = 1 segundo + (longitud_mensaje / 100)
delay = min(max(delay, 1), 3)  # Entre 1 y 3 segundos
```

**Ejemplo de delays:**
- Mensaje corto (67 chars): 1.7 segundos
- Mensaje medio (183 chars): 2.8 segundos
- Mensaje largo (500 chars): 3.0 segundos

##### 3. Sistema Anti-Traslape

**Problema:** ¿Qué pasa si el usuario escribe mientras el bot está enviando los 7 mensajes?

**Solución:**
1. **Lock Dinámico Extendido**
   - El sistema calcula el tiempo total de envío
   - Extiende automáticamente el lock en Redis
   - Ejemplo: 7 mensajes con 14.5s de delays → Lock de 24s

2. **Detección de Mensajes Huérfanos**
   - Al terminar de enviar, verifica si hay mensajes nuevos en el buffer
   - Si los hay, **auto-relanza** el procesamiento inmediatamente
   - Sin espera (wait_seconds=0)

3. **Procesamiento Recursivo**
   ```
   Usuario: "skill de pedro sobre data analysis?"
   Bot: Envía 7 mensajes...
     → Mensaje 1/7 enviado
     → Mensaje 2/7 enviado
     → Mensaje 3/7 enviado
   Usuario: "y sobre marketing?" ← INTERRUMPE
     → Mensaje se acumula en Redis
     → NO se lanza nuevo task (lock activo)
     → Mensaje 4/7 enviado
     → Mensaje 5/7 enviado
     → Mensaje 6/7 enviado
     → Mensaje 7/7 enviado
     → ⚡ DETECTA mensaje pendiente
     → 🔄 AUTO-RELANZA procesamiento
     → Responde "y sobre marketing?" inmediatamente
   ```

#### Funciones Principales

##### `split_message_humanized(message, max_length=500)`
Divide un mensaje largo en fragmentos inteligentes.

**Parámetros:**
- `message`: Mensaje completo a dividir
- `max_length`: Longitud máxima por fragmento (default: 500)

**Retorna:** Lista de fragmentos

##### Funciones Redis Anti-Traslape
- `has_pending_messages(chat_id)` - Verifica si hay mensajes en buffer
- `mark_needs_reprocessing(chat_id)` - Marca para reprocesamiento
- `needs_reprocessing(chat_id)` - Verifica flag de reprocesamiento
- `clear_reprocessing_flag(chat_id)` - Limpia flag

#### Configuración

```python
# En src/app.py
message_fragments = split_message_humanized(
    response_message,
    max_length=500  # Ajustable según preferencia
)

# Delay configurable por fragmento
delay = 1 + (len(fragment) / 100)  # Fórmula personalizable
delay = max(1, min(3, delay))      # Límites ajustables
```

#### Logs del Sistema Humanizador

```bash
✂️ [Background Task] Dividiendo respuesta en fragmentos humanizados...
📊 Total de fragmentos a enviar: 7
🔒 Extendiendo lock por 24s para enviar 7 mensajes...
📤 [Background Task] Enviando fragmento 1/7...
   Contenido: Pedro tiene habilidades sólidas...
   ⏳ Esperando 1.7s antes del siguiente mensaje...
📤 [Background Task] Enviando fragmento 2/7...
   Contenido: 1. Herramientas de Análisis...
   ⏳ Esperando 2.8s antes del siguiente mensaje...
...
✅ [Background Task] 7 fragmentos enviados a Chatwoot
⚡ [Background Task] ¡MENSAJES PENDIENTES DETECTADOS!
🔄 AUTO-RELANZANDO procesamiento inmediato...
```

#### Ventajas del Sistema

✅ **Experiencia más natural** - Simula conversación humana
✅ **Mejor legibilidad** - Mensajes cortos son más fáciles de leer en móvil
✅ **Previene pérdida de mensajes** - Sistema anti-traslape robusto
✅ **Auto-recuperante** - Procesa mensajes pendientes automáticamente
✅ **Configurable** - Longitud y delays ajustables
✅ **Recursivo** - Maneja múltiples interrupciones

#### Archivo de Prueba

Para probar el sistema humanizador:

```bash
cd src
python test_humanize.py
```

Esto muestra cómo se dividirá un mensaje largo y los delays aplicados.

#### Documentación Adicional

Para detalles técnicos completos del sistema anti-traslape:
- `FLUJO_ANTI_TRASLAPE_SOLUCION_FINAL.md` - Documentación completa con diagramas

---

### Monitoreo y Debugging

#### Logs del sistema

El sistema genera logs detallados en consola:

```
📨 DATOS RECIBIDOS DEL WEBHOOK: {...}
💾 Guardando mensaje individual en Supabase...
📬 Mensaje recibido: hola...
⏳ Mensaje acumulado en Redis...
🚀 Lanzando background task...
⏰ [Background Task] Iniciado para chat...
```

#### Verificar configuración

```bash
# Verificar Redis
cd src
python -c "from utils.redis_utils import check_redis_connection; check_redis_connection()"

# Verificar Supabase
cd src
python -c "from utils.db_utils import get_chat_history; print(get_chat_history('test', limit=1))"
```

---

### Contribuciones

Este es un proyecto educativo AI Developer. Para contribuir:

1. Fork del repositorio
2. Crear branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit de cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

---

### Licencia

Proyecto educativo AI Developer 2025

---

### Contacto

**Proyecto:** Pedro WhatsApp AI Agent
**Autor:** Pedro Valera
**Curso:** AI Developer por el Profesor Kevin Inofuente
**Fecha:** Diciembre 2025

---

### Documentación Adicional

Para documentación técnica detallada, ver:
- `.claude/Documentacion/20251205_ESTRUCTURA_PROYECTO.md` - Documentación completa del proyecto
- `src/agent.py` - Implementación de prompts y agente
- `src/app.py` - Lógica del webhook y background tasks
- `setup_supabase_fresh.sql` - Configuración de base de datos

---

**Última actualización:** 6 de Diciembre, 2025

---
---

## English

Intelligent WhatsApp chatbot system with RAG (Retrieval-Augmented Generation), Chatwoot integration, and advanced asynchronous processing capabilities.

**Version:** 2.1 - Background Tasks + Dual Prompts + Response Humanizer

---

### Description

This project implements a conversational AI agent that operates on WhatsApp through Chatwoot, using LangChain for agent orchestration and OpenAI GPT-4o-mini as the language model. The system features:

- **Advanced RAG** with Supabase as vector store
- **Asynchronous processing** via FastAPI Background Tasks
- **Dual prompt system** dynamically interchangeable
- **Response humanizer** - Intelligent splitting of long messages
- **Intelligent conversation management** with Redis and Supabase
- **Automatic detection** of human assistance requests
- **Support for manual intervention** without losing context
- **Anti-overlap system** - Prevention of mixed messages

---

### Key Features

#### Core Features
- RAG (Retrieval-Augmented Generation) system with OpenAI embeddings
- LangChain agent with custom tools
- Complete integration with Chatwoot for WhatsApp Business
- Vector database with Supabase (pgvector)
- Persistent conversation history

#### New Features (v2.0)
- **Asynchronous Background Tasks** - Processing without timeouts (< 1s response)
- **Dual prompts** - "Philosopher" vs "Conversational" switchable via webhook
- **Intelligent history filtering** - Prevents message duplication
- **Manual message support** - Human intervention with preserved context
- **Processing lock** - Prevents duplicate processing with Redis
- **Message accumulation** - Redis buffer with configurable TTL

#### Innovations (v2.1) 🆕
- **Response humanizer** - Automatic splitting of long responses into multiple messages
- **Intelligent delays** - Human typing simulation between messages (1-3s)
- **Anti-overlap system** - Protection against mixed messages
- **Auto-relaunch** - Automatic processing of pending messages
- **Dynamic lock** - TTL adjusted based on response length

#### Advanced Management
- Automatic label control (atiende-ia / atiende-humano)
- Human advisor request detection with multiple patterns
- Automatic group message filtering
- Outgoing message classification (bot vs manual)

---

### Tech Stack

#### Backend & Framework
- **Python 3.x**
- **FastAPI** - Web framework with Background Tasks support
- **Uvicorn** - High-performance ASGI server

#### AI & Machine Learning
- **LangChain** - Agent orchestration framework
- **OpenAI GPT-4o-mini** - Language model
- **OpenAI Embeddings** - text-embedding-ada-002 (1536 dimensions)

#### Databases
- **Supabase (PostgreSQL + pgvector)** - Vector store and conversation history
- **Redis Cloud** - Message buffer and lock system

#### Integrations
- **Chatwoot** - Messaging platform (WhatsApp Business API)
- **Google Sheets** - Lead registration (optional)
- **Gmail API** - Email sending (optional)
- **Google Calendar** - Meeting scheduling (optional)

---

### Prerequisites

#### Software
- Python 3.8 or higher
- pip (Python package manager)
- Git

#### Cloud Services (with created accounts)
- OpenAI account with API Key
- Supabase instance configured with pgvector
- Redis Cloud instance
- Chatwoot account with WhatsApp connected
- (Optional) Google Cloud Platform credentials for Google services

---

### Installation

#### 1. Clone the repository

```bash
git clone <repository-url>
cd "Project-Clase04-Langchain-RAG-Chatwood - cloud v2"
```

#### 2. Install dependencies

```bash
cd src
pip install -r requirements.txt
```

**Main dependencies:**
- `langchain`, `langchain-core`, `langchain-community`, `langchain-openai`
- `openai`
- `fastapi`, `uvicorn[standard]`
- `supabase>=2.3.0`, `vecs>=0.4.0`
- `redis>=5.0.0`
- `python-dotenv`, `pytz`, `httpx`, `requests`

#### 3. Configure Supabase database

Execute the SQL configuration script to create the necessary tables:

```sql
-- See file: setup_supabase_fresh.sql
-- Creates tables: chat_history_teknik, documents_langchain_teknik
-- Configures RPC function for vector search
```

#### 4. Load documents to RAG (optional)

```bash
cd src/RAG
python rag.py
```

This will load the PDFs from the `Base_de_Conocimientos/` folder to Supabase as vectors.

---

### Configuration

#### `.env` File

Create the `src/.env` file with the following variables:

```bash
# ============================================
# OpenAI API
# ============================================
OPENAI_API_KEY=sk-proj-...

# ============================================
# Chatwoot
# ============================================
CHATWOOT_BASE_URL=https://your-instance.chatwoot.com/
CHATWOOT_ACCOUNT_ID=1
CHATWOOT_API_ACCESS_TOKEN=...

# ============================================
# Supabase
# ============================================
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=...

# ============================================
# Redis Cloud
# ============================================
REDIS_HOST=redis-xxxxx.cloud.redislabs.com
REDIS_PORT=13530
REDIS_DB=0
REDIS_PASSWORD=...
MESSAGE_ACCUMULATION_TTL=15

# ============================================
# Prompt System (NEW in v2.0)
# ============================================
PROMPT_TYPE=conversacional  # Options: "filosofo" | "conversacional"

# ============================================
# Google Services (OPTIONAL)
# ============================================
GOOGLE_SHEET_ID=...
GOOGLE_SHEET_NAME=Interesados
GOOGLE_SERVICE_ACCOUNT_PATH=/path/to/credentials.json
APP_PASSWORD_GMAIL=...
EMAIL_REMITENTE=your-email@gmail.com
```

**IMPORTANT:**
- The `.env` file must be in the `src/` folder, NOT in the root
- Never commit `.env` to Git (already in `.gitignore`)

---

### Usage

#### Start the server

##### Option 1: From `src/` (recommended)

```bash
cd src
python -m uvicorn app:app --host 0.0.0.0 --port 5005 --reload
```

##### Option 2: Direct execution

```bash
cd src
python app.py
```

The server will be available at: `http://localhost:5005`

#### Main endpoints

##### `POST /chatbot/webhook`
Receives Chatwoot webhooks with WhatsApp messages.

**Features:**
- Message validation
- Redis accumulation
- Background tasks launching
- Label control
- Manual message detection

##### `POST /prompt/webhook` (NEW)
Dynamically changes the prompt type.

**Example:**
```bash
curl -X POST http://localhost:5005/prompt/webhook \
  -H "Content-Type: application/json" \
  -d '{"prompt_type": "filosofo"}'
```

**Response:**
```json
{
  "status": "success",
  "message": "Prompt updated to 'filosofo'",
  "current_prompt_type": "filosofo"
}
```

##### `GET /health`
Health check for monitoring.

#### Configure webhook in Chatwoot

1. Go to Settings > Integrations > Webhooks
2. Create new webhook with URL: `http://your-server:5005/chatbot/webhook`
3. Select events: `message_created`
4. Save

#### Prompt System

The system supports two interchangeable prompt types:

##### "Philosopher" Prompt
- Responds with inspiring famous quotes
- Includes quote author
- Mentions that Pedro will respond soon
- Ideal for automatic responses outside business hours

**Example:**
```
"The night is purer than the day; it is better for thinking, loving and dreaming." - (Eça de Queiroz)

Pedro will respond to you shortly, Juan. 👋
```

##### "Conversational" Prompt
- Professional assistant with RAG access
- Conversational and contextual responses
- Uses knowledge base
- Ideal for business hours support

**Change prompt:**
- Via `.env`: `PROMPT_TYPE=conversacional`
- Via webhook: `POST /prompt/webhook` (without restarting service)

---

### Project Structure

```
src/
├── .env                          # Environment variables (DO NOT COMMIT)
├── app.py                        # Main FastAPI application
├── agent.py                      # LangChain agent with dual prompts
├── tools.py                      # Agent tools
├── requirements.txt              # Project dependencies
│
├── bot/
│   └── ai_bot.py                 # RAG system with Supabase
│
├── services/
│   └── chatwoot.py               # Chatwoot API client
│
├── utils/
│   ├── db_utils.py               # Supabase management (history)
│   ├── redis_utils.py            # Redis management (buffer + locks)
│   ├── envio_correo.py           # Email sending tool
│   ├── registro_google_sheet.py  # Google Sheets tool
│   └── agenda_reunion_corporativa.py  # Scheduling tool
│
└── RAG/
    ├── rag.py                    # Document loading script
    └── Base_de_Conocimientos/    # PDFs for RAG
        └── *.pdf
```

#### Configuration files

- `Dockerfile.dev` / `Dockerfile.prod` - Containerization
- `cloudbuild.yaml` - CI/CD for Google Cloud
- `service.yaml` - Cloud Run configuration
- `setup_supabase_fresh.sql` - Database setup

---

### Data Flow

```
User sends message → Chatwoot Webhook → FastAPI
    ↓
Validations (groups, labels, message type)
    ↓
Human advisor request? → Change labels → END
    ↓
Save to Supabase + Accumulate in Redis
    ↓
Launch Background Task (5s) → Return 200 OK
    ↓
[Background Task]
    ↓
Wait 5s → Retrieve Redis buffer + Supabase history
    ↓
Process with Agent (according to PROMPT_TYPE)
    ↓
Generate response → Save to Supabase → Send to Chatwoot
    ↓
User receives message
```

---

### Advanced Technical Features

#### Background Tasks
- Asynchronous processing with FastAPI
- Immediate webhook response (< 1s)
- Configurable wait time (default 5s)
- Automatic resource cleanup

#### Message Management
- Redis buffer with 15s TTL + 5s extra
- Automatic concatenation of rapid messages
- Intelligent history filtering (exclude_pending)
- Message classification (user/bot/manual)

#### Lock System
- Prevents duplicate processing
- Redis lock per chat_id
- Automatic TTL (15s)
- Auto-release on completion

#### RAG (Retrieval-Augmented Generation)
- Embeddings: OpenAI text-embedding-ada-002
- Chunk size: 1024 characters
- Chunk overlap: 250 characters
- Retriever K: 12 documents
- Vector store: Supabase pgvector

---

### 🎭 Response Humanizer System (v2.1)

#### Problem Solved

Long AI agent responses (e.g., lists with 5-7 items) were sent in a single message, resulting in:
- Large text blocks difficult to read on WhatsApp
- Unnatural experience (humans don't write such long messages at once)
- User attention loss

#### Implemented Solution

The **Humanizer System** automatically splits long responses into multiple shorter messages, simulating how a human would naturally respond.

#### Features

##### 1. Intelligent Message Splitting
```python
# Multi-level splitting strategy:
# 1. Split by paragraphs (double line break)
# 2. If a paragraph is too long, split by single lines
# 3. If a line is too long, split by periods
# 4. Configurable maximum length (default: 500 characters)
```

**Splitting example:**
```
Original message (980 characters):
"Pedro has strong data analysis skills, including:
1. Analysis Tools: Experience using...
2. Data Visualization: Ability to create...
3. Data Interpretation: Skill in extracting...
4. Statistical Analysis: Knowledge of...
5. ETL: Experience in ETL processes..."

Split into 7 messages:
→ Message 1: "Pedro has strong data analysis skills..."
→ Message 2: "1. Analysis Tools..."
→ Message 3: "2. Data Visualization..."
→ Message 4: "3. Data Interpretation..."
→ Message 5: "4. Statistical Analysis..."
→ Message 6: "5. ETL..."
→ Message 7: "If you need more details..."
```

##### 2. Intelligent Delays Between Messages

Each message has a **dynamically calculated delay** to simulate human typing time:

```python
# Delay formula
delay = 1 second + (message_length / 100)
delay = min(max(delay, 1), 3)  # Between 1 and 3 seconds
```

**Delay examples:**
- Short message (67 chars): 1.7 seconds
- Medium message (183 chars): 2.8 seconds
- Long message (500 chars): 3.0 seconds

##### 3. Anti-Overlap System

**Problem:** What happens if the user writes while the bot is sending 7 messages?

**Solution:**
1. **Extended Dynamic Lock**
   - System calculates total sending time
   - Automatically extends Redis lock
   - Example: 7 messages with 14.5s delays → 24s lock

2. **Orphaned Message Detection**
   - After sending, checks for new messages in buffer
   - If found, **auto-relaunches** processing immediately
   - No wait (wait_seconds=0)

3. **Recursive Processing**
   ```
   User: "pedro's data analysis skills?"
   Bot: Sends 7 messages...
     → Message 1/7 sent
     → Message 2/7 sent
     → Message 3/7 sent
   User: "and about marketing?" ← INTERRUPTS
     → Message accumulated in Redis
     → Does NOT launch new task (lock active)
     → Message 4/7 sent
     → Message 5/7 sent
     → Message 6/7 sent
     → Message 7/7 sent
     → ⚡ DETECTS pending message
     → 🔄 AUTO-RELAUNCHES processing
     → Responds to "and about marketing?" immediately
   ```

#### Main Functions

##### `split_message_humanized(message, max_length=500)`
Splits a long message into intelligent fragments.

**Parameters:**
- `message`: Complete message to split
- `max_length`: Maximum length per fragment (default: 500)

**Returns:** List of fragments

##### Redis Anti-Overlap Functions
- `has_pending_messages(chat_id)` - Checks for messages in buffer
- `mark_needs_reprocessing(chat_id)` - Marks for reprocessing
- `needs_reprocessing(chat_id)` - Checks reprocessing flag
- `clear_reprocessing_flag(chat_id)` - Clears flag

#### Configuration

```python
# In src/app.py
message_fragments = split_message_humanized(
    response_message,
    max_length=500  # Adjustable by preference
)

# Configurable delay per fragment
delay = 1 + (len(fragment) / 100)  # Customizable formula
delay = max(1, min(3, delay))      # Adjustable limits
```

#### Humanizer System Logs

```bash
✂️ [Background Task] Splitting response into humanized fragments...
📊 Total fragments to send: 7
🔒 Extending lock for 24s to send 7 messages...
📤 [Background Task] Sending fragment 1/7...
   Content: Pedro has strong data analysis skills...
   ⏳ Waiting 1.7s before next message...
📤 [Background Task] Sending fragment 2/7...
   Content: 1. Analysis Tools...
   ⏳ Waiting 2.8s before next message...
...
✅ [Background Task] 7 fragments sent to Chatwoot
⚡ [Background Task] PENDING MESSAGES DETECTED!
🔄 AUTO-RELAUNCHING immediate processing...
```

#### System Advantages

✅ **More natural experience** - Simulates human conversation
✅ **Better readability** - Short messages easier to read on mobile
✅ **Prevents message loss** - Robust anti-overlap system
✅ **Self-recovering** - Automatically processes pending messages
✅ **Configurable** - Adjustable length and delays
✅ **Recursive** - Handles multiple interruptions

#### Test File

To test the humanizer system:

```bash
cd src
python test_humanize.py
```

This shows how a long message will be split and the applied delays.

#### Additional Documentation

For complete technical details of the anti-overlap system:
- `FLUJO_ANTI_TRASLAPE_SOLUCION_FINAL.md` - Complete documentation with diagrams

---

### Monitoring and Debugging

#### System logs

The system generates detailed console logs:

```
📨 WEBHOOK DATA RECEIVED: {...}
💾 Saving individual message to Supabase...
📬 Message received: hello...
⏳ Message accumulated in Redis...
🚀 Launching background task...
⏰ [Background Task] Started for chat...
```

#### Verify configuration

```bash
# Check Redis
cd src
python -c "from utils.redis_utils import check_redis_connection; check_redis_connection()"

# Check Supabase
cd src
python -c "from utils.db_utils import get_chat_history; print(get_chat_history('test', limit=1))"
```

---

### Contributing

This is an AI Developer educational project. To contribute:

1. Fork the repository
2. Create branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

### License

AI Developer Educational Project 2025

---

### Contact

**Project:** Pedro WhatsApp AI Agent
**Author:** Pedro Valera
**Course:** AI Developer by Professor Kevin Inofuente
**Date:** December 2025

---

### Additional Documentation

For detailed technical documentation, see:
- `.claude/Documentacion/20251205_ESTRUCTURA_PROYECTO.md` - Complete project documentation
- `src/agent.py` - Prompts and agent implementation
- `src/app.py` - Webhook logic and background tasks
- `setup_supabase_fresh.sql` - Database configuration

---

**Last updated:** December 6, 2025
