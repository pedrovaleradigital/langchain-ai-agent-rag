# db_utils.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


# ============================================
# CONFIGURACIÓN
# ============================================
CHAT_HISTORY_TABLE = "chat_history_teknik"
CHAT_HISTORY_LIMIT = 15  # Número de mensajes a recuperar por defecto


def get_supabase_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    return create_client(supabase_url, supabase_key)

#Guarda cada mensaje en la tabla de historial
#Almacena: ID del chat, quién envió (user/bot) y el mensaje
def store_chat_history(chat_id: str, sender: str, message: str) -> None:
    try:
        client = get_supabase_client()
        data = {
            "chat_id": chat_id,
            "sender": sender,
            "message": message
        }
        response = client.table(CHAT_HISTORY_TABLE).insert(data).execute()
        
        # Comprobar si el objeto response tiene el atributo 'error'
        if hasattr(response, 'error') and response.error is not None:
            print("Error al almacenar el mensaje:", response.error)
        else:
            print("Mensaje almacenado correctamente:", response.data)
    except Exception as e:
        print(f"Error al conectar con Supabase o tabla no existe: {e}")
        print("Continuando sin guardar historial...")


#Recupera el historial de mensajes de un chat específico
#Devuelve los últimos N mensajes en orden cronológico
#Formatea los datos para que el LLM pueda entenderlos
def get_chat_history(chat_id: str, limit: int = CHAT_HISTORY_LIMIT, exclude_pending: bool = False) -> list:
    try:
        client = get_supabase_client()
        response = (
            client.table(CHAT_HISTORY_TABLE)
            .select("*")
            .eq("chat_id", chat_id)
            .order("created_at", desc=True)  # Orden cronológico descendente (los más nuevos primero)
            .limit(limit)
            .execute()
        )

        
        # Si el objeto response tiene un atributo 'error' y no es None,
        # consideramos que hubo un error.
        if hasattr(response, "error") and response.error is not None:
            print("Error al obtener el histórico:", response.error)
            return []
        
        # Si no hay error, extraemos los datos
        data = response.data or []
        messages = []

        for row in data:
            # Si 'sender' es "user" o "manual", consideramos que es un mensaje del usuario.
            # "manual" son mensajes enviados manualmente por un humano (outgoing con lid)
            is_user = (row["sender"] in ["user", "manual"])
            messages.append({
                "body": row["message"],
                "isUser": is_user,
                "timestamp": row.get("created_at"),  # Agregar timestamp para debugging
                "sender": row["sender"]  # Mantener info del sender
            })

        # IMPORTANTE: Revertir el orden para que sea cronológico (más antiguo primero)
        # Esto es lo que esperan los LLMs para entender la conversación
        messages.reverse()

        # Si exclude_pending=True, filtrar mensajes de usuario sin respuesta del bot
        if exclude_pending and len(messages) > 0:
            # Buscar desde el final hacia atrás el último mensaje del bot
            # y excluir todos los mensajes del usuario después de ese
            last_bot_index = -1
            for i in range(len(messages) - 1, -1, -1):
                if not messages[i]["isUser"]:  # Es mensaje del bot
                    last_bot_index = i
                    break

            if last_bot_index >= 0:
                # Quedarnos solo hasta el último mensaje del bot (inclusive)
                messages = messages[:last_bot_index + 1]
                print(f"📌 Historial filtrado: excluidos {len(data) - len(messages)} mensajes pendientes sin respuesta")
            else:
                # No hay ningún mensaje del bot, significa que todos son del usuario
                # Excluir todos para evitar duplicación con el buffer
                print(f"📌 No hay mensajes del bot en historial, excluyendo todos los mensajes del usuario")
                messages = []

        print(f"Historial procesado: {len(messages)} mensajes en orden cronológico")
        return messages
    except Exception as e:
        print(f"Error al conectar con Supabase o tabla no existe: {e}")
        print("Continuando sin historial previo...")
        return []
