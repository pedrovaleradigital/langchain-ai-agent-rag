import os

#Paso 1: Elección de la Técnica de DocumentLoader
from langchain_community.document_loaders import PyPDFLoader

#Paso 2: Elección de Técnica de Splitting (LangChain v1.0)
from langchain_text_splitters import RecursiveCharacterTextSplitter

#Paso 3: Elección del Modelo de Word Embedding
from langchain_openai import OpenAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

#Importanciones para trabajar con SUPABASE
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client


# ============================================
# CONFIGURACIÓN
# ============================================
TABLE_NAME = "documents_langchain_teknik"#"documents_langchain_asistente_de_ventas"
QUERY_NAME = f"match_{TABLE_NAME}"
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 250
EMBEDDING_MODEL = "text-embedding-ada-002" #1536 dimensiones -> 3072 Large
PDF_PATH = "Base_de_Conocimientos/resumen_experiencia_pedro_valera.pdf"


if __name__ == '__main__':
    #=================================== Paso 1: Documment Loader =======================================
    print(f"📄 Cargando PDF: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documentos = loader.load()
    print(f"✅ Documentos cargados: {len(documentos)} páginas")


    #============================ Paso 2: Document Splitting  - Chunking ===========================================
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = text_splitter.split_documents(documents=documentos)
    print(f"✅ Chunks creados: {len(chunks)} fragmentos (tamaño: {CHUNK_SIZE}, overlap: {CHUNK_OVERLAP})")


    #========== Paso 3: Embeddings - Cargamos el Modelo de Embeddings para convertir los Chunks ==========
    print(f"🔢 Usando modelo de embeddings: {EMBEDDING_MODEL}")
    embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL)


    #======================= Paso 4: VectorStore - Llevamos los Embeddings a Supabase ====================
    print("🔄 Conectando con Supabase...")
    
    # Validar que las variables de entorno existan
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("\n❌ ERROR: Variables de entorno no configuradas")
        print(f"   SUPABASE_URL: {'✅ Configurada' if supabase_url else '❌ NO ENCONTRADA'}")
        print(f"   SUPABASE_SERVICE_KEY: {'✅ Configurada' if supabase_key else '❌ NO ENCONTRADA'}")
        print("\n💡 Solución:")
        print("   1. Crea un archivo .env en la raíz del proyecto")
        print("   2. Agrega las siguientes líneas:")
        print('      SUPABASE_URL="https://tu-proyecto.supabase.co"')
        print('      SUPABASE_SERVICE_KEY="tu_service_key_aqui"')
        exit(1)
    
    print(f"   URL completa: {supabase_url}")
    print(f"   Key: {supabase_key[:20]}...")
    
    try:
        client = create_client(supabase_url, supabase_key)
        print("   ✅ Cliente de Supabase creado correctamente")
        
        # Probar la conexión con una consulta simple
        print(f"   🔍 Probando conexión con tabla: {TABLE_NAME}")
        test_response = client.table(TABLE_NAME).select("id").limit(1).execute()
        print(f"   ✅ Conexión exitosa! Tabla '{TABLE_NAME}' accesible")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica que la URL de Supabase sea correcta")
        print("   2. Verifica tu conexión a internet")
        print(f"   3. Verifica que la tabla '{TABLE_NAME}' exista en Supabase")
        print("   4. Verifica que el SERVICE_KEY tenga permisos suficientes")
        exit(1)

    print(f"🔄 Cargando vectores a Supabase en tabla '{TABLE_NAME}' (esto puede tardar un poco)...")
    vectorstore = SupabaseVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        client=client,
        table_name=TABLE_NAME,
        query_name=QUERY_NAME,
    )
    
    print(f"\n{'='*80}")
    print(f"✅ ¡Proceso completado exitosamente!")
    print(f"📊 {len(chunks)} chunks cargados a la tabla '{TABLE_NAME}'")
    print(f"🔍 Función de búsqueda: {QUERY_NAME}")
    print(f"📚 Tu base de conocimiento está lista para ser consultada por el chatbot")
    print(f"{'='*80}")