# redis_utils.py
"""
Utilidades para gestión de concatenación de mensajes con Redis
Permite acumular múltiples mensajes del usuario antes de procesarlos
"""
import os
import redis
import json
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# Cargar .env desde src/ (1 nivel arriba de utils/)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path, override=True)


# ============================================
# CONFIGURACIÓN
# ============================================
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Tiempo de espera para concatenar mensajes (en segundos)
MESSAGE_ACCUMULATION_TTL = int(os.getenv("MESSAGE_ACCUMULATION_TTL", "15"))

# Prefijo para las keys de Redis
REDIS_KEY_PREFIX = "whatsapp_msg:"
REDIS_PROCESSING_PREFIX = "whatsapp_processing:"


def get_redis_client() -> redis.Redis:
    """Crea y retorna un cliente de Redis"""
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5
        )
        # Verificar conexión
        client.ping()
        return client
    except Exception as e:
        print(f"[ERROR] Error al conectar con Redis: {e}")
        print("Continuando sin concatenacion de mensajes...")
        return None


def accumulate_message(chat_id: str, message: str) -> Optional[str]:
    """
    Acumula mensajes del usuario en Redis.
    Con el nuevo sistema de background tasks, esta función SIEMPRE retorna None
    porque el procesamiento lo hace el background task después del wait.

    Args:
        chat_id: Identificador único del chat
        message: Mensaje a acumular

    Returns:
        None si el mensaje fue acumulado (siempre en el nuevo sistema)
        str solo si Redis no está disponible (fallback)
    """
    try:
        client = get_redis_client()
        if not client:
            # Si Redis no está disponible, retornar el mensaje directamente
            print("⚠️ Redis no disponible, procesando mensaje inmediatamente")
            return message

        key = f"{REDIS_KEY_PREFIX}{chat_id}"

        # Obtener mensajes acumulados actuales
        accumulated_data = client.get(key)

        if accumulated_data:
            # Ya hay mensajes acumulados, agregar el nuevo
            data = json.loads(accumulated_data)
            data["messages"].append(message)
            data["count"] += 1

            # IMPORTANTE: NO decrementar el TTL, usar un TTL fijo largo
            # El background task se encarga de limpiar
            ttl_actual = client.ttl(key)
            print(f"🔍 DEBUG Redis - Key existe. TTL actual: {ttl_actual}s")

            # Usar un TTL generoso para asegurar que el background task tenga tiempo
            ttl_a_usar = MESSAGE_ACCUMULATION_TTL + 5
            client.setex(key, ttl_a_usar, json.dumps(data))
            print(f"📝 Mensaje acumulado ({data['count']} mensajes). TTL actualizado a: {ttl_a_usar}s")
            return None  # El background task procesará
        else:
            # Primer mensaje, iniciar acumulación
            data = {
                "messages": [message],
                "count": 1
            }
            # Usamos un TTL generoso para que no expire antes del background task
            ttl_inicial = MESSAGE_ACCUMULATION_TTL + 5
            client.setex(key, ttl_inicial, json.dumps(data))
            print(f"🕐 Iniciando acumulación de mensajes (TTL: {ttl_inicial}s)")
            print(f"   Chat ID: {chat_id}")
            print(f"   Redis Key: {key}")
            return None  # El background task procesará

    except Exception as e:
        print(f"[ERROR] Error en accumulate_message: {e}")
        import traceback
        traceback.print_exc()
        # En caso de error, retornar el mensaje sin concatenar
        return message


def get_accumulated_messages(chat_id: str) -> Optional[str]:
    """
    Obtiene y elimina los mensajes acumulados de un chat.
    Útil cuando se quiere forzar el procesamiento antes del TTL.

    Args:
        chat_id: Identificador único del chat

    Returns:
        str con los mensajes concatenados, o None si no hay mensajes acumulados
    """
    try:
        client = get_redis_client()
        if not client:
            return None

        key = f"{REDIS_KEY_PREFIX}{chat_id}"
        accumulated_data = client.get(key)

        if accumulated_data:
            data = json.loads(accumulated_data)
            concatenated = "\n".join(data["messages"])
            client.delete(key)
            print(f"✅ Obtenidos {data['count']} mensajes acumulados (forzado)")
            return concatenated

        return None

    except Exception as e:
        print(f"[ERROR] Error en get_accumulated_messages: {e}")
        return None


def clear_accumulated_messages(chat_id: str) -> bool:
    """
    Limpia los mensajes acumulados de un chat sin procesarlos.

    Args:
        chat_id: Identificador único del chat

    Returns:
        True si se eliminaron mensajes, False si no había nada o hubo error
    """
    try:
        client = get_redis_client()
        if not client:
            return False

        key = f"{REDIS_KEY_PREFIX}{chat_id}"
        result = client.delete(key)

        if result > 0:
            print(f"🗑️ Mensajes acumulados eliminados para chat {chat_id}")
            return True
        return False

    except Exception as e:
        print(f"[ERROR] Error en clear_accumulated_messages: {e}")
        return False


def check_redis_connection() -> bool:
    """
    Verifica si Redis está disponible y funcionando.

    Returns:
        True si la conexión es exitosa, False en caso contrario
    """
    try:
        client = get_redis_client()
        if client:
            client.ping()
            print("[OK] Redis conectado correctamente")
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Redis no disponible: {e}")
        return False


def is_chat_being_processed(chat_id: str) -> bool:
    """
    Verifica si un chat ya está siendo procesado por un background task.

    Args:
        chat_id: Identificador único del chat

    Returns:
        True si ya está siendo procesado, False en caso contrario
    """
    try:
        client = get_redis_client()
        if not client:
            return False

        key = f"{REDIS_PROCESSING_PREFIX}{chat_id}"
        return client.exists(key) > 0
    except Exception as e:
        print(f"[ERROR] Error en is_chat_being_processed: {e}")
        return False


def mark_chat_as_processing(chat_id: str, ttl: int = 30) -> bool:
    """
    Marca un chat como en procesamiento para evitar procesamiento duplicado.

    Args:
        chat_id: Identificador único del chat
        ttl: Tiempo en segundos que durará el lock (default 30s)

    Returns:
        True si se marcó exitosamente, False si ya estaba marcado
    """
    try:
        client = get_redis_client()
        if not client:
            return True  # Si no hay Redis, permitir procesar

        key = f"{REDIS_PROCESSING_PREFIX}{chat_id}"
        # setnx solo setea si no existe (set if not exists)
        result = client.setnx(key, "1")
        if result:
            client.expire(key, ttl)
            print(f"🔒 Chat {chat_id} marcado como en procesamiento (TTL: {ttl}s)")
            return True
        else:
            print(f"⏭️ Chat {chat_id} ya está siendo procesado")
            return False
    except Exception as e:
        print(f"[ERROR] Error en mark_chat_as_processing: {e}")
        return True  # En caso de error, permitir procesar


def unmark_chat_as_processing(chat_id: str) -> bool:
    """
    Desmarca un chat de procesamiento.

    Args:
        chat_id: Identificador único del chat

    Returns:
        True si se desmarcó, False en caso contrario
    """
    try:
        client = get_redis_client()
        if not client:
            return False

        key = f"{REDIS_PROCESSING_PREFIX}{chat_id}"
        result = client.delete(key)
        if result > 0:
            print(f"🔓 Chat {chat_id} desmarcado de procesamiento")
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Error en unmark_chat_as_processing: {e}")
        return False
