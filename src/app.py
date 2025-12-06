from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse

# Cargar variables de entorno PRIMERO
from dotenv import load_dotenv
from pathlib import Path
import asyncio
import time

# Cargar .env desde el directorio src/ (mismo nivel que app.py)
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path, override=True)

from bot.ai_bot import AIBot
from services.chatwoot import Chatwoot

from agent import DataPath

#Histórico del Chat
from utils.db_utils import store_chat_history, get_chat_history

#Redis para concatenación de mensajes
from utils.redis_utils import (
    accumulate_message,
    check_redis_connection,
    clear_accumulated_messages,
    mark_chat_as_processing,
    unmark_chat_as_processing,
    is_chat_being_processed,
    get_accumulated_messages
)

app = FastAPI(
    title="Pedro WhatsApp AI Agent",
    description="API para chatbot de WhatsApp con RAG y agentes LangChain",
    version="1.0.0"
)


# ============================================
# BACKGROUND TASK - PROCESAR MENSAJES ACUMULADOS
# ============================================
async def process_accumulated_messages_task(
    chat_id: str,
    conversation_id: int,
    sender_name: str,
    sender_phone: str,
    wait_seconds: int = 10
):
    """
    Background task que espera N segundos y luego procesa los mensajes acumulados.
    Similar al nodo "Wait" de n8n.

    Args:
        chat_id: ID del chat
        conversation_id: ID de la conversación en Chatwoot
        sender_name: Nombre del usuario
        sender_phone: Número de teléfono del usuario
        wait_seconds: Segundos a esperar antes de procesar
    """
    try:
        print(f"⏰ [Background Task] Iniciado para chat {chat_id}. Esperando {wait_seconds}s...")

        # Esperar el tiempo configurado (similar al nodo Wait de n8n)
        await asyncio.sleep(wait_seconds)

        print(f"⏱️ [Background Task] Tiempo de espera completado para chat {chat_id}")

        # Obtener mensajes acumulados de Redis
        accumulated_message = get_accumulated_messages(chat_id)

        if not accumulated_message:
            print(f"⚠️ [Background Task] No hay mensajes acumulados para {chat_id}")
            unmark_chat_as_processing(chat_id)
            return

        print("=" * 80)
        print("📦 [Background Task] MENSAJES RECUPERADOS DEL BUFFER REDIS:")
        print(f"{accumulated_message}")
        print("=" * 80)

        # Obtener historial de Supabase (excluyendo mensajes pendientes sin respuesta)
        print("📚 [Background Task] Obteniendo historial de Supabase...")
        historial = get_chat_history(chat_id=chat_id, limit=15, exclude_pending=True)
        print(f"✅ Historial recuperado: {len(historial)} mensajes (solo hasta la última respuesta del bot)")

        # Inicializar el agente (pasando nombre y teléfono del usuario)
        bot = DataPath()
        agente, tools = bot.crear_agente(sender_name=sender_name, sender_phone=sender_phone)

        # Procesar con el agente IA
        print("🤖 [Background Task] Enviando a agente IA...")
        try:
            resultado = bot.procesar_mensaje(accumulated_message, agente, tools, history_messages=historial)
            response_message = resultado.get("output", "No se pudo procesar el mensaje correctamente.")
            print("=" * 80)
            print("✅ [Background Task] RESPUESTA DEL AGENTE IA:")
            print(f"{response_message}")
            print("=" * 80)
        except Exception as e:
            print(f"❌ [Background Task] Error al procesar el mensaje: {e}")
            import traceback
            traceback.print_exc()
            response_message = f"Ocurrió un error al procesar tu mensaje: {str(e)}"

        # Guardar respuesta del bot en Supabase
        store_chat_history(chat_id, "bot", response_message)

        # Enviar respuesta a Chatwoot
        chatwoot = Chatwoot()
        chatwoot.send_message(
            conversation_id=conversation_id,
            message=response_message,
            message_type='outgoing'
        )
        print(f"✅ [Background Task] Respuesta enviada a Chatwoot (conversación {conversation_id})")

        # Limpiar buffer de Redis
        clear_accumulated_messages(chat_id)
        print(f"🗑️ [Background Task] Buffer Redis limpiado para {chat_id}")

    except Exception as e:
        print(f"❌ [Background Task] Error crítico: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Siempre desmarcar el chat como procesando
        unmark_chat_as_processing(chat_id)
        print(f"✅ [Background Task] Completado para chat {chat_id}")


@app.post('/chatbot/webhook') #Endpoint (sin slash final para evitar redirects)
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    
    # DEBUG: Imprimir estructura completa de datos recibidos
    print("=" * 80)
    print("📨 DATOS RECIBIDOS DEL WEBHOOK:")
    print(f"{data}")
    print("=" * 80)

    # Detectar formato del webhook (Evolution API vs WAHA)
    # Evolution API envía: data directamente con 'key', 'pushName', 'message', etc.
    # WAHA envía: data['payload'] con 'from', 'body', etc.
    
    # Variables para almacenar información del webhook
    webhook_format = None
    conversation_id = None
    sender_name = None
    chatwoot_service = None  # Para control de etiquetas
    
    try:
        # Detectar y procesar diferentes formatos de webhook
        
        # 1. Formato Chatwoot (el que estás usando)
        if 'event' in data and data.get('event') == 'message_created':
            webhook_format = 'chatwoot'
            message_type = data.get('message_type')

            # Extraer chat_id preferiblemente del teléfono en meta
            phone_number = data.get('conversation', {}).get('meta', {}).get('sender', {}).get('phone_number')

            if phone_number:
                chat_id = phone_number.replace('+', '')
            else:
                # Fallback: usar el identificador del sender si no hay teléfono en meta
                chat_id = data.get('sender', {}).get('identifier')
            received_message = data.get('content', '')
            sender_name = data.get('sender', {}).get('name', 'Usuario')
            conversation_id = data.get('conversation', {}).get('id')

            print(f"✅ Formato Chatwoot detectado")
            print(f"   Tipo de mensaje: {message_type}")
            print(f"   Chat ID: {chat_id}")
            print(f"   Nombre: {sender_name}")
            print(f"   Conversación ID: {conversation_id}")
            print(f"   Mensaje: {received_message}")

            # ============================================
            # MANEJO DE MENSAJES OUTGOING (MANUALES)
            # ============================================
            if message_type == 'outgoing':
                # Filtrar mensaje de conexión establecida
                if "Connection successfully established!" in received_message:
                    print("⏭️  Mensaje de conexión ignorado")
                    return JSONResponse(
                        content={'status': 'success', 'message': 'Mensaje de conexión ignorado'},
                        status_code=200
                    )

                # Determinar si es mensaje manual (enviado por humano)
                sender_identifier = data.get('conversation', {}).get('meta', {}).get('sender', {}).get('identifier', '')
                sender_type = 'manual' if 'lid' in sender_identifier else 'bot'

                print(f"📤 Mensaje outgoing detectado")
                print(f"   Sender identifier: {sender_identifier}")
                print(f"   Clasificado como: {sender_type}")

                # Guardar mensaje outgoing manual en Supabase
                if sender_type == 'manual':
                    print(f"💾 Guardando mensaje manual en Supabase...")
                    store_chat_history(chat_id, "manual", received_message)
                    print(f"✅ Mensaje manual guardado en Supabase")
                    return JSONResponse(
                        content={'status': 'success', 'message': 'Mensaje manual guardado'},
                        status_code=200
                    )
                else:
                    # Es un mensaje del bot, ignorar
                    print("⏭️  Mensaje del bot ignorado")
                    return JSONResponse(
                        content={'status': 'success', 'message': 'Mensaje del bot ignorado'},
                        status_code=200
                    )
            
            # ============================================
            # CONTROL DE ETIQUETAS - VERIFICAR "atiende-ia"
            # ============================================
            chatwoot_service = Chatwoot()
            conversation_labels = chatwoot_service.get_conversation_labels(conversation_id)
            
            print(f"🏷️  Etiquetas actuales: {conversation_labels}")
            print("✅ Conversación tiene etiqueta 'atiende-ia' - IA puede responder")
            
            # ============================================
            # DETECTAR SOLICITUD DE ASESOR HUMANO
            # ============================================
            mensaje_lower = received_message.lower()
            patrones_humano = [
                'hablar con un asesor',
                'hablar con una asesora',
                'hablar con asesor',
                'hablar con asesora',
                'quiero un asesor',
                'quiero una asesora',
                'necesito un asesor',
                'necesito una asesora',
                'comunicarme con un asesor',
                'comunicarme con una asesora',
                'contactar con un asesor',
                'contactar con una asesora',
                'hablar con humano',
                'hablar con una persona',
                'hablar con alguien',
                'atención humana',
                'asesor humano',
                'asesora humana',
                'persona real',
                'agente humano'
            ]
            
            solicita_humano = any(patron in mensaje_lower for patron in patrones_humano)
            
            if solicita_humano:
                print("🤝 Usuario solicita asesor humano - Cambiando etiquetas...")
                
                # Eliminar etiqueta "atiende-ia"
                chatwoot_service.remove_labels(conversation_id, ['atiende-ia'])
                print("   ❌ Etiqueta 'atiende-ia' eliminada")
                
                # Agregar etiqueta "atiende-humano"
                chatwoot_service.add_labels(conversation_id, ['atiende-humano'])
                print("   ✅ Etiqueta 'atiende-humano' agregada")
                
                # Enviar mensaje de confirmación
                mensaje_transferencia = (
                    f"Perfecto {sender_name}! 👋\n\n"
                    "He notificado a un asesor humano de DataPath para que te atienda personalmente. "
                    "Un miembro de nuestro equipo se comunicará contigo muy pronto.\n\n"
                    "Mientras tanto, estaremos aquí para ayudarte. ¡Gracias por tu paciencia! 😊"
                )
                
                chatwoot_service.send_message(
                    conversation_id=conversation_id,
                    message=mensaje_transferencia,
                    message_type='outgoing'
                )
                
                # Guardar en historial
                store_chat_history(chat_id, "user", received_message)
                store_chat_history(chat_id, "bot", mensaje_transferencia)
                
                print("✅ Usuario transferido a atención humana")
                
                return JSONResponse(
                    content={'status': 'success', 'message': 'Usuario transferido a humano'},
                    status_code=200
                )
        
        # 2. Formato Evolution API directo
        elif 'key' in data and 'message' in data:
            webhook_format = 'evolution'
            chat_id = data['key']['remoteJid']
            message_obj = data.get('message', {})
            received_message = (
                message_obj.get('conversation') or 
                message_obj.get('extendedTextMessage', {}).get('text') or
                ''
            )
            print(f"✅ Formato Evolution API detectado")
            print(f"   Chat ID: {chat_id}")
            print(f"   Mensaje: {received_message}")
            
        # 3. Formato WAHA (legacy)
        elif 'payload' in data:
            webhook_format = 'waha'
            chat_id = data['payload']['from']
            received_message = data['payload']['body']
            print(f"✅ Formato WAHA detectado")
            
        else:
            print("❌ Formato de datos desconocido")
            return JSONResponse(
                content={'status': 'error', 'message': 'Formato de datos no reconocido'},
                status_code=400
            )
        
        # Filtrar mensajes de grupos
        is_group = '@g.us' in chat_id
        if is_group:
            print("⏭️  Mensaje de grupo ignorado")
            return JSONResponse(
                content={'status': 'success', 'message': 'Mensaje de grupo ignorado'},
                status_code=200
            )
        
        if not received_message:
            print("⏭️  Mensaje vacío ignorado")
            return JSONResponse(
                content={'status': 'success', 'message': 'Mensaje vacío ignorado'},
                status_code=200
            )
            
    except Exception as e:
        print(f"❌ Error al procesar datos del webhook: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={'status': 'error', 'message': f'Error: {str(e)}'},
            status_code=500
        )

    # Inicializar servicios según el formato detectado
    chatwoot = chatwoot_service if webhook_format == 'chatwoot' else None

    bot = DataPath()
    agente, tools = bot.crear_agente()

    # ============================================
    # 1) GUARDAR MENSAJE INDIVIDUAL EN SUPABASE (SIEMPRE)
    # ============================================
    # Guardamos CADA mensaje individual antes de acumular en Redis
    print(f"💾 Guardando mensaje individual en Supabase...")
    store_chat_history(chat_id, "user", received_message)

    # ============================================
    # 2) REDIS: Concatenación de mensajes con Background Task
    # ============================================
    print(f"📬 Mensaje recibido: {received_message[:50]}...")

    # Acumular mensaje en Redis
    accumulated_result = accumulate_message(chat_id, received_message)

    if accumulated_result is None:
        # El mensaje está siendo acumulado
        print(f"⏳ Mensaje acumulado en Redis. Esperando más mensajes (10s)...")

        # Verificar si ya hay un background task procesando este chat
        if is_chat_being_processed(chat_id):
            print(f"⏭️ Ya existe un background task para este chat, no crear otro")
            return JSONResponse(
                content={'status': 'success', 'message': 'Mensaje acumulado'},
                status_code=200
            )

        # Marcar como en procesamiento y lanzar background task
        if mark_chat_as_processing(chat_id, ttl=15):  # TTL más largo que el wait_seconds
            print(f"🚀 Lanzando background task para procesar en 5s...")

            # Extraer teléfono del usuario
            phone_number = data.get('conversation', {}).get('meta', {}).get('sender', {}).get('phone_number', '')
            sender_phone_clean = phone_number.replace('+', '') if phone_number else chat_id

            background_tasks.add_task(
                process_accumulated_messages_task,
                chat_id=chat_id,
                conversation_id=conversation_id,
                sender_name=sender_name,
                sender_phone=sender_phone_clean,
                wait_seconds=5
            )

        return JSONResponse(
            content={'status': 'success', 'message': 'Mensaje acumulado, procesamiento iniciado'},
            status_code=200
        )
    else:
        # Esto ya no debería ejecutarse con el nuevo sistema
        # porque el background task se encarga de procesar
        print(f"⚠️ ADVERTENCIA: accumulated_result no es None, esto no debería pasar")
        num_mensajes = accumulated_result.count('\n') + 1
        print(f"✅ Procesando {num_mensajes} mensajes acumulados inmediatamente...")

    return JSONResponse(content={'status': 'success'}, status_code=200)

    return JSONResponse(content={'status': 'success'}, status_code=200)


# ============================================
# ENDPOINT PARA CAMBIAR PROMPT DINÁMICAMENTE
# ============================================
import os
from pydantic import BaseModel

class PromptUpdate(BaseModel):
    prompt_type: str

@app.post("/prompt/webhook")
async def update_prompt_type(update: PromptUpdate):
    """
    Webhook para cambiar el tipo de prompt (PROMPT_TYPE) dinámicamente.
    Acepta JSON: {"prompt_type": "filosofo" | "conversacional"}
    """
    new_type = update.prompt_type.lower()
    
    if new_type not in ["filosofo", "conversacional"]:
        return JSONResponse(
            content={"status": "error", "message": "Tipo de prompt inválido. Use 'filosofo' o 'conversacional'."},
            status_code=400
        )
    
    # Actualizar variable de entorno globalmente para el proceso
    os.environ["PROMPT_TYPE"] = new_type
    
    print(f"🔄 PROMPT_TYPE actualizado a: {new_type}")
    
    return {
        "status": "success",
        "message": f"Prompt actualizado a '{new_type}'",
        "current_prompt_type": new_type
    }
@app.get("/")
async def root():
    """Endpoint de health check"""
    return {"status": "ok", "message": "Pedro WhatsApp AI Agent is running"}


@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoreo"""
    return {"status": "healthy", "service": "chatbot-api"}


if __name__ == '__main__':
    import uvicorn
    # Para usar reload, necesitamos pasar la app como string de importación
    uvicorn.run("app:app", host='0.0.0.0', port=5005, reload=True)