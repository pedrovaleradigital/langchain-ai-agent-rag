from time import sleep
from datetime import datetime
import pytz
import os

# LangChain v1.0 imports
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

from tools import PedroTools





class DataPath:
    def __init__(self):
        self.llm = ChatOpenAI(model= 'gpt-4o-mini') # no olvides adicionar tu api_key en el .env
        self.tool = PedroTools()
        self.history_messages = None  # Almacenamos el historial aquí

    def obtener_fecha_hora_actual(self):
        """Obtiene la fecha y hora actual en Lima, Perú"""
        try:
            tz = pytz.timezone("America/Lima")
            ahora = datetime.now(tz)
            
            # Traducir días al español
            dias_es = {
                'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            
            meses_es = {
                'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
                'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
                'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
                'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
            }
            
            dia_semana = dias_es.get(ahora.strftime("%A"), ahora.strftime("%A"))
            mes = meses_es.get(ahora.strftime("%B"), ahora.strftime("%B"))
            
            fecha_completa = f"{dia_semana} {ahora.day} de {mes} de {ahora.year}"
            hora_actual = ahora.strftime("%I:%M %p")
            
            return f"HOY ES: {fecha_completa}, {hora_actual}"
        except:
            return "HOY ES: Miércoles 17 de Septiembre de 2025, 2:45 PM"

    def crear_agente(self, sender_name: str = "Usuario", sender_phone: str = ""):

        # Creamos un closure para pasar el historial de mensajes a la herramienta
        def consultar_baseconocimiento_pedro_with_history(query: str) -> str:
            """Usa el sistema RAG para consultar la base de conocimiento de Pedro."""
            return PedroTools.consultar_RAG_func(query, self.history_messages)

        # Herramientas disponibles para el agente
        tools = [
            # PedroTools.enviar_correo,  # 🔴 DESACTIVADA - No usar por ahora
            # PedroTools.registrar_google_sheet,  # 🔴 DESACTIVADA - No usar por ahora
            # PedroTools.agendar_reunion_corporativa,  # 🔴 DESACTIVADA - Tool para leads B2B
            Tool(name="consultar_RAG", func=consultar_baseconocimiento_pedro_with_history, description="Usa el sistema RAG para consultar la base de conocimiento de Pedro.")
        ]

        llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

        # Obtener fecha y hora actual
        fecha_hora_actual = self.obtener_fecha_hora_actual()

        # ============================================
        # SELECCIÓN DE PROMPT SEGÚN CONFIGURACIÓN
        # ============================================
        # ============================================
        # SELECCIÓN DE PROMPT SEGÚN CONFIGURACIÓN (DINÁMICO)
        # ============================================
        # Leer variable de entorno en tiempo de ejecución para permitir cambios via webhook
        current_prompt_type = os.environ.get("PROMPT_TYPE", "conversacional")

        if current_prompt_type == "filosofo":
            system_prompt_text = self._get_filosofo_prompt(fecha_hora_actual, sender_name, sender_phone)
        else:  # conversacional (default)
            system_prompt_text = self._get_conversacional_prompt(fecha_hora_actual, sender_name, sender_phone)

        print(f"🎭 Prompt activo: {current_prompt_type.upper()}")

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt_text),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )


        # LangChain v1.0: Usar create_agent() directamente
        # Este agente ya incluye el executor internamente usando LangGraph
        agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=system_prompt_text
        )

        return agent, tools

    def _get_filosofo_prompt(self, fecha_hora_actual: str, sender_name: str = "Usuario", sender_phone: str = "") -> str:
        """Prompt del filósofo sabio que responde con frases célebres"""
        return f"""
Eres un sabio filósofo que responde a TODOS los mensajes con frases célebres inspiradoras.

⏰ **INFORMACIÓN TEMPORAL ACTUAL:**
{fecha_hora_actual}

👤 **INFORMACIÓN DEL USUARIO:**
- Nombre: {sender_name}
- Teléfono: {sender_phone}

**TU ÚNICA TAREA:**
Responde SIEMPRE con una frase célebre famosa relacionada con el tema del mensaje del usuario.

**REGLAS:**
1. SOLO responde con UNA frase célebre
2. Incluye el autor de la frase entre paréntesis
3. Al final, SIEMPRE agrega una línea que mencione que Pedro responderá pronto
4. Usa VARIACIONES en el mensaje de Pedro (no repitas la misma frase)
5. **IMPORTANTE:** Incluye el nombre del usuario ({sender_name}) al menos una vez en tu respuesta
6. NO menciones DataPath ni nada relacionado con educación
7. Sé breve y directo

**FORMATO DE RESPUESTA:**
"[Frase célebre aquí]" - (Autor)

[Línea en blanco]

[Variación de "Pedro te responderá pronto" mencionando el nombre del usuario]

**VARIACIONES PARA MENCIONAR A PEDRO (elige una diferente cada vez):**
- "En breve te responderá Pedro, {sender_name}. 👋"
- "Pedro estará contigo muy pronto, {sender_name}. 😊"
- "Pedro se unirá a la conversación enseguida, {sender_name}. ⏰"
- "Pronto tendrás respuesta de Pedro, {sender_name}. 🙌"
- "Pedro te atenderá en un momento, {sender_name}. ✨"

**Ejemplo completo:**
Usuario: "hola es de noche no?"
Tú:
"La noche es más pura que el día; es mejor para pensar, amar y soñar." - (Eça de Queiroz)

En breve te responderá Pedro, {sender_name}. 👋

**IMPORTANTE:** NO uses herramientas (consultar_RAG, enviar_correo, etc.). Solo responde con frases célebres.
"""

    def _get_conversacional_prompt(self, fecha_hora_actual: str, sender_name: str, sender_phone: str) -> str:
        """Prompt conversacional para asistente de Pedro"""
        return f"""
Eres el asistente de WhatsApp de Pedro Valera, un experto en inteligencia artificial y automatización.

⏰ **INFORMACIÓN TEMPORAL ACTUAL:**
{fecha_hora_actual}

👤 **INFORMACIÓN DEL USUARIO:**
- Nombre: {sender_name}
- Teléfono: {sender_phone}

**TU MISIÓN:**
Asistir a Pedro respondiendo sus mensajes de WhatsApp de manera profesional, amigable y eficiente. Tienes acceso a una base de conocimientos sobre los proyectos y servicios de Pedro.

**REGLAS DE COMPORTAMIENTO:**
1. Sé conversacional, natural y amigable
2. Usa el nombre del usuario cuando sea apropiado
3. Mantén las respuestas concisas pero informativas
4. Si tienes dudas sobre algo específico, menciona que Pedro lo confirmará personalmente
5. Usa emojis moderadamente para dar calidez (máximo 1-2 por mensaje)
6. Responde en el mismo idioma que el usuario

**HERRAMIENTAS DISPONIBLES:**
- consultar_RAG: Usa esta herramienta cuando necesites información específica sobre proyectos, servicios o conocimientos técnicos de Pedro

**CONTEXTO:**
Tienes acceso al historial completo de la conversación para mantener contexto y coherencia en tus respuestas.

**EJEMPLO DE CONVERSACIÓN:**
Usuario: "Hola, me interesa saber sobre automatizaciones con IA"
Tú: "¡Hola {sender_name}! 👋 Qué bueno que te interese el tema de automatizaciones con IA. Pedro es especialista en esto. Déjame consultar información específica sobre los servicios que ofrece..."

[Luego usarías la herramienta consultar_RAG para dar detalles precisos]
"""

    def procesar_mensaje(self, msg, agente, tools, history_messages=None):

        # Guardamos el historial de mensajes en la instancia
        self.history_messages = history_messages

        # Verificamos si history_messages llega correctamente
        if history_messages is None:
            print("❌ No se recibió historial (history_messages es None)")
            messages = []
        else:
            print(f"✅ Historial recibido: {len(history_messages)} mensajes")
            for idx, message in enumerate(history_messages):
                sender_type = "👤 Usuario" if message.get('isUser') else "🤖 Bot"
                print(f"  {idx+1}. {sender_type}: {message.get('body', 'Sin contenido')[:50]}...")
            print("---")

        # Se reconstruye la lista de mensajes para el prompt. 
        # Nota: Si antes usabas 'fromMe' y ahora usas 'isUser', asegúrate de que todos tus mensajes tengan la clave correcta.
        messages = []
        if history_messages:  # Verificar que no sea None o lista vacía
            for message in history_messages:
                # Usamos 'isUser' para determinar el tipo de mensaje
                message_class = HumanMessage if message.get('isUser') else AIMessage
                messages.append(message_class(content=message.get('body')))
        
        # El mensaje actual NO lo agregamos aquí, ya se maneja en el input
        # messages.append(HumanMessage(content=msg))

        """Procesa el mensaje recibido vía WhatsApp y llama a la herramienta correcta."""
        
        # Debug: Verificar que el historial se esté enviando correctamente
        print(f"📨 Enviando al agente: {len(messages)} mensajes de historial")
        if messages:
            print("📜 Últimos 3 mensajes del historial:")
            for i, m in enumerate(messages[-3:]):
                msg_type = "👤" if isinstance(m, HumanMessage) else "🤖"
                print(f"   {msg_type} {m.content[:60]}...")
        
        # LangChain v1.0: El agente espera mensajes en formato de lista
        # Convertir el historial + mensaje actual al formato esperado
        all_messages = []
        
        # Agregar el historial de mensajes
        for hist_msg in messages:
            if isinstance(hist_msg, HumanMessage):
                all_messages.append({"role": "user", "content": hist_msg.content})
            elif isinstance(hist_msg, AIMessage):
                all_messages.append({"role": "assistant", "content": hist_msg.content})
        
        # Agregar el mensaje actual del usuario (sin instrucciones adicionales)
        # El comportamiento está definido en el system prompt (línea 73)
        print("=" * 80)
        print("📥 MENSAJE ACTUAL DEL USUARIO (del buffer Redis):")
        print(f"{msg}")
        print("=" * 80)
        all_messages.append({"role": "user", "content": msg})
        
        # Invocar el agente con el nuevo formato de LangChain v1.0
        resultado = agente.invoke({"messages": all_messages})
        
        # El resultado en v1.0 viene en formato {"messages": [...]}
        # Extraer el último mensaje (respuesta del agente)
        if "messages" in resultado:
            last_message = resultado["messages"][-1]
            # Crear un diccionario compatible con el formato anterior
            return {
                "output": last_message.content if hasattr(last_message, 'content') else str(last_message)
            }
        else:
            return {"output": str(resultado)}