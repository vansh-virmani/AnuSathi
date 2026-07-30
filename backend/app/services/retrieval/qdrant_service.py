from qdrant_client import QdrantClient,models
from app.config import settings

qdrant_client = QdrantClient(
    url=settings.QDRANT_ENDPOINT,
    api_key=settings.QDRANT_KEY,
    timeout=60.0
)
def  qdrant_search(query_vector,limit: int=10,document_id: str|None = None):
   
    try:

        query_filter = None

        if document_id:  #if pdf is uploaded or doc_id is there present then search only in that pdf
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="source",  
                        match=models.MatchValue(value=document_id),
                    )
                ]
            )

        response = qdrant_client.query_points(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_filter=query_filter,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )

        results = []

        for point in response.points:

            results.append(
                {
                    "text": point.payload.get("text", ""),
                    "source": point.payload.get("source", ""),
                    "page": point.payload.get("page", 1),
                    "vector_score": point.score,
                }
            )

        return results

    except Exception as e:
        print(f"Qdrant Search Error: {e}")
        return []
