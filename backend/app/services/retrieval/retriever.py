from app.services.retrieval.qdrant_service import qdrant_search
from app.config import settings
from app.services.retrieval.embeddings import embed_query
from app.services.retrieval.reranker import rerank_documents

def retriever(question:str,top_k: int=5,document_id: str | None = None) ->list[dict]:
    
    query_vector=embed_query(question)

    

    #converted to list of floats which will be understood by qdrant db for matching vectors

    results=qdrant_search(query_vector,limit=10,document_id=document_id) # consists of semantically matched text score page score
    
    if results:
        print("First result:", results[0])#testing purpose 

    if not results:
        print("No results returned from Qdrant")
        return []

    reranked_results=rerank_documents(question,results, top_k=top_k) #reranked
    
    return reranked_results
#it returns mapped documents with top results that contain text source vector_score



