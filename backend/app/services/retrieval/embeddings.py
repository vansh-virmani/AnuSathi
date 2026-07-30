from app.config import settings
from sentence_transformers import SentenceTransformer

BATCH_SIZE = 50

embedding_model=SentenceTransformer(settings.EMBEDDING_MODEL)


# ── Batch embedding -- _ underscore before a fn name to tell that it is used internally

def _embed_batch(batch: list[str]) -> list[list[float]]:
   
   
        return embedding_model.encode(batch, show_progress_bar=True,normalize_embeddings=True,convert_to_numpy=True).tolist()
#progressbar on terminal like white one


#embed user query
def embed_query(query: str) -> list[float]:

   
      return embedding_model.encode(
        query, normalize_embeddings=True, convert_to_numpy=True,).tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
   
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        
        all_embeddings.extend(_embed_batch(batch)) #use .extend as embeddings are many otherwise would use append
    return all_embeddings