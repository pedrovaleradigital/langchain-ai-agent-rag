import os
from langchain_openai import OpenAIEmbeddings
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# ============================================
# CONFIGURACIÓN
# ============================================
TABLE_NAME = "documents_langchain_teknik"
QUERY_NAME = f"match_{TABLE_NAME}"
EMBEDDING_MODEL = "text-embedding-ada-002"
RETRIEVER_K = 12  # Número de chunks a recuperar

class AIBot:

    def __init__(self):
        self.__embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        
        # Obtener credenciales de Supabase
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
        self.__supabase_client = create_client(supabase_url, supabase_key)

    def search_similar_documents(self, query: str, k: int = RETRIEVER_K):
        """
        Busca documentos similares usando la función RPC de Supabase directamente.
        Esta implementación evita el bug de SupabaseVectorStore.
        """
        from langchain_core.documents import Document
        
        try:
            # 1. Convertir la consulta en embedding
            query_embedding = self.__embedding_model.embed_query(query)
            
            # 2. Llamar directamente a la función RPC de Supabase
            result = self.__supabase_client.rpc(
                QUERY_NAME,
                {
                    'query_embedding': query_embedding,
                    'match_count': k,
                    'filter': {}
                }
            ).execute()
            
            # 3. Convertir los resultados en objetos Document
            documents = []
            if result.data:
                for doc in result.data:
                    documents.append(
                        Document(
                            page_content=doc.get('content', ''),
                            metadata=doc.get('metadata', {})
                        )
                    )
            
            print(f"✅ Documentos recuperados desde Supabase: {len(documents)}")
            return documents
            
        except Exception as e:
            print(f"❌ Error al buscar documentos similares: {e}")
            import traceback
            traceback.print_exc()
            return []