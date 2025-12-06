# Pedro WhatsApp AI Agent

Sistema inteligente de chatbot para WhatsApp con RAG (Retrieval-Augmented Generation), integración con Chatwoot y capacidades avanzadas de procesamiento asíncrono.

**Versión:** 2.0 - Background Tasks + Prompts Duales

---

## Descripción

Este proyecto implementa un agente de IA conversacional que opera sobre WhatsApp a través de Chatwoot, utilizando LangChain para orquestación de agentes y OpenAI GPT-4o-mini como modelo de lenguaje. El sistema cuenta con:

- **RAG avanzado** con Supabase como vector store
- **Procesamiento asíncrono** mediante FastAPI Background Tasks
- **Sistema dual de prompts** intercambiables dinámicamente
- **Gestión inteligente de conversaciones** con Redis y Supabase
- **Detección automática** de solicitudes de atención humana
- **Soporte para intervención manual** sin perder contexto

---

## Características Principales

### Core Features
- Sistema RAG (Retrieval-Augmented Generation) con embeddings de OpenAI
- Agente LangChain con herramientas personalizadas
- Integración completa con Chatwoot para WhatsApp Business
- Base de datos vectorial con Supabase (pgvector)
- Historial persistente de conversaciones

### Nuevas Funcionalidades (v2.0)
- **Background Tasks asíncronos** - Procesamiento sin timeouts (< 1s de respuesta)
- **Prompts duales** - "Filósofo" vs "Conversacional" intercambiables vía webhook
- **Filtrado inteligente de historial** - Previene duplicación de mensajes
- **Soporte para mensajes manuales** - Intervención humana con contexto preservado
- **Lock de procesamiento** - Previene procesamiento duplicado con Redis
- **Acumulación de mensajes** - Buffer Redis con TTL configurable

### Gestión Avanzada
- Control automático de etiquetas (atiende-ia / atiende-humano)
- Detección de solicitud de asesor humano con múltiples patrones
- Filtrado automático de mensajes de grupos
- Clasificación de mensajes outgoing (bot vs manual)

---

## Tech Stack

### Backend & Framework
- **Python 3.x**
- **FastAPI** - Framework web con soporte para Background Tasks
- **Uvicorn** - Servidor ASGI de alto rendimiento

### IA & Machine Learning
- **LangChain** - Framework de orquestación de agentes
- **OpenAI GPT-4o-mini** - Modelo de lenguaje
- **OpenAI Embeddings** - text-embedding-ada-002 (1536 dimensiones)

### Bases de Datos
- **Supabase (PostgreSQL + pgvector)** - Vector store y historial de conversaciones
- **Redis Cloud** - Buffer de mensajes y sistema de locks

### Integraciones
- **Chatwoot** - Plataforma de mensajería (WhatsApp Business API)
- **Google Sheets** - Registro de leads (opcional)
- **Gmail API** - Envío de correos (opcional)
- **Google Calendar** - Agendamiento de reuniones (opcional)

---

## Requisitos Previos

### Software
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

### Servicios Cloud (con cuentas creadas)
- Cuenta de OpenAI con API Key
- Instancia de Supabase configurada con pgvector
- Instancia de Redis Cloud
- Cuenta de Chatwoot con WhatsApp conectado
- (Opcional) Credenciales de Google Cloud Platform para servicios de Google

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd "Project-Clase04-Langchain-RAG-Chatwood - cloud v2"
```

### 2. Instalar dependencias

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

### 3. Configurar base de datos Supabase

Ejecutar el script SQL de configuración para crear las tablas necesarias:

```sql
-- Ver archivo: setup_supabase_fresh.sql
-- Crea tablas: chat_history_teknik, documents_langchain_teknik
-- Configura función RPC para búsqueda vectorial
```

### 4. Cargar documentos al RAG (opcional)

```bash
cd src/RAG
python rag.py
```

Esto cargará los PDFs de la carpeta `Base_de_Conocimientos/` a Supabase como vectores.

---

## Configuración

### Archivo `.env`

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

## Uso

### Iniciar el servidor

#### Opción 1: Desde `src/` (recomendado)

```bash
cd src
python -m uvicorn app:app --host 0.0.0.0 --port 5005 --reload
```

#### Opción 2: Ejecución directa

```bash
cd src
python app.py
```

El servidor estará disponible en: `http://localhost:5005`

### Endpoints principales

#### `POST /chatbot/webhook`
Recibe webhooks de Chatwoot con mensajes de WhatsApp.

**Funcionalidades:**
- Validación de mensajes
- Acumulación en Redis
- Lanzamiento de background tasks
- Control de etiquetas
- Detección de mensajes manuales

#### `POST /prompt/webhook` (NUEVO)
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

#### `GET /health`
Health check para monitoreo.

### Configurar webhook en Chatwoot

1. Ir a Settings > Integrations > Webhooks
2. Crear nuevo webhook con URL: `http://tu-servidor:5005/chatbot/webhook`
3. Seleccionar eventos: `message_created`
4. Guardar

### Sistema de Prompts

El sistema soporta dos tipos de prompts intercambiables:

#### Prompt "Filósofo"
- Responde con frases célebres inspiradoras
- Incluye autor de la frase
- Menciona que Pedro responderá pronto
- Ideal para respuestas automáticas fuera de horario

**Ejemplo:**
```
"La noche es más pura que el día; es mejor para pensar, amar y soñar." - (Eça de Queiroz)

En breve te responderá Pedro, Juan. 👋
```

#### Prompt "Conversacional"
- Asistente profesional con acceso a RAG
- Respuestas conversacionales y contextuales
- Usa base de conocimientos
- Ideal para atención durante horario laboral

**Cambiar prompt:**
- Via `.env`: `PROMPT_TYPE=conversacional`
- Via webhook: `POST /prompt/webhook` (sin reiniciar servicio)

---

## Estructura del Proyecto

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

### Archivos de configuración

- `Dockerfile.dev` / `Dockerfile.prod` - Containerización
- `cloudbuild.yaml` - CI/CD para Google Cloud
- `service.yaml` - Configuración de Cloud Run
- `setup_supabase_fresh.sql` - Setup de base de datos

---

## Flujo de Datos

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

## Características Técnicas Avanzadas

### Background Tasks
- Procesamiento asíncrono con FastAPI
- Respuesta inmediata al webhook (< 1s)
- Wait time configurable (default 5s)
- Auto-limpieza de recursos

### Gestión de Mensajes
- Buffer Redis con TTL de 15s + 5s extra
- Concatenación automática de mensajes rápidos
- Filtrado inteligente de historial (exclude_pending)
- Clasificación de mensajes (user/bot/manual)

### Sistema de Locks
- Previene procesamiento duplicado
- Lock en Redis por chat_id
- TTL automático (15s)
- Auto-liberación al finalizar

### RAG (Retrieval-Augmented Generation)
- Embeddings: OpenAI text-embedding-ada-002
- Chunk size: 1024 caracteres
- Chunk overlap: 250 caracteres
- Retriever K: 12 documentos
- Vector store: Supabase pgvector

---

## Monitoreo y Debugging

### Logs del sistema

El sistema genera logs detallados en consola:

```
📨 DATOS RECIBIDOS DEL WEBHOOK: {...}
💾 Guardando mensaje individual en Supabase...
📬 Mensaje recibido: hola...
⏳ Mensaje acumulado en Redis...
🚀 Lanzando background task...
⏰ [Background Task] Iniciado para chat...
```

### Verificar configuración

```bash
# Verificar Redis
cd src
python -c "from utils.redis_utils import check_redis_connection; check_redis_connection()"

# Verificar Supabase
cd src
python -c "from utils.db_utils import get_chat_history; print(get_chat_history('test', limit=1))"
```

---

## Contribuciones

Este es un proyecto educativo del curso AI Developer. Para contribuir:

1. Fork del repositorio
2. Crear branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit de cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

---

## Licencia

Proyecto educativo - Curso AI Developer 2025

---

## Contacto

**Proyecto:** Pedro WhatsApp AI Agent
**Autor:** Pedro Valera
**Curso:** AI Developer - DataPath por el Profesor Kevin Inofuente
**Fecha:** Diciembre 2025

---

## Documentación Adicional

Para documentación técnica detallada, ver:
- `.claude/Documentacion/20251205_ESTRUCTURA_PROYECTO.md` - Documentación completa del proyecto
- `src/agent.py` - Implementación de prompts y agente
- `src/app.py` - Lógica del webhook y background tasks
- `setup_supabase_fresh.sql` - Configuración de base de datos

---

**Última actualización:** 5 de Diciembre, 2025
