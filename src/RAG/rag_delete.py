import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# ============================================
# CONFIGURACIÓN
# ============================================
TABLE_NAME = "documents_langchain_teknik"

def delete_all_documents():
    print("🔄 Conectando con Supabase...")
    
    # Validar variables de entorno
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("\n❌ ERROR: Variables de entorno no configuradas")
        print(f"   SUPABASE_URL: {'✅ Configurada' if supabase_url else '❌ NO ENCONTRADA'}")
        print(f"   SUPABASE_SERVICE_KEY: {'✅ Configurada' if supabase_key else '❌ NO ENCONTRADA'}")
        exit(1)
        
    try:
        client = create_client(supabase_url, supabase_key)
        print("   ✅ Cliente de Supabase creado correctamente")
        
        print(f"\n⚠️  ATENCIÓN: Estás a punto de BORRAR TODO el contenido de la tabla '{TABLE_NAME}'")
        confirm = input("   ¿Estás seguro? Escribe 'BORRAR' para confirmar: ")
        
        if confirm != "BORRAR":
            print("\n❌ Operación cancelada por el usuario.")
            return

        print(f"\n🗑️  Eliminando registros de '{TABLE_NAME}'...")
        
        # En Supabase/Postgrest, para borrar todo se suele necesitar una condición que cubra todo.
        # Usaremos neq (not equal) a un ID imposible o is not null si el campo lo permite.
        # Asumiendo que 'id' es la PK.
        
        # Opción 1: Borrar donde id no es nulo (si id existe)
        # client.table(TABLE_NAME).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        # Una forma más generica si no sabemos el tipo de ID es usar un filtro que siempre sea verdaero para los datos existentes
        # O iterar. Pero para vector stores suele ser mejor borrar por metadata o simplemente todo.
        # Probaremos neq de un UUID dummy si es uuid, o gt 0 si es int.
        # Al ser vector store creado por langchain, suele tener ids tipo uuid.
        
        response = client.table(TABLE_NAME).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        # Verificamos la respuesta (data suele contener los registros borrados)
        data = response.data
        count = len(data) if data else 0
        
        print(f"✅ Se han eliminado {count} registros de la tabla '{TABLE_NAME}'.")
        
    except Exception as e:
        print(f"\n❌ Error durante el proceso: {e}")
        # Si el error es por política de DELETE (ej: necesitas una clausula WHERE), esto fallará y lo veremos.

if __name__ == "__main__":
    delete_all_documents()
