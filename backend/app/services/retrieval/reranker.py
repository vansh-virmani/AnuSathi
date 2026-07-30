from flashrank import Ranker, RerankRequest

# Lazy initialization - Ranker is loaded on first use so again-again it does not load into memory
_ranker = None


def _get_ranker() -> Ranker:
    """
    Initializes the FlashRank engine lazily. 
    FlashRank uses a local ONNX model (ms-marco-MiniLM-L-6-v2) for ultra-fast reranking.
    """
    global _ranker
    if _ranker is None:
        
        try:
            _ranker = Ranker()
        except Exception as e:
            raise e
            
    return _ranker



def rerank_documents(query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
    """
    Refines retrieval results by re-scoring documents against the query semantically.
    
    Why FlashRank? 
    Standard vector search (Cosine Similarity) is fast but mathematically "fuzzy."
    FlashRank uses a Cross-Encoder approach which is much more precise but usually slow.
    FlashRank solves this by using highly optimized, quantized ONNX models locally.
    """
    if not documents:
        return []

    
    

    try:
        ranker = _get_ranker()
        
        # FlashRank expects a list of dictionaries with 'id' and 'text'....etc
        passages = [
            {"id": i, "text": doc["text"]}
            for i, doc in enumerate(documents)
        ]


        """This is why we create:"id": i during passage creation.

Not because FlashRank needs fancy IDs, but because later
 we can use that id as an index back into the original documents list,
 preserving all metadata (page, source, etc.) after reranking.
"""
        
        
        

        request = RerankRequest(query=query, passages=passages)
        results = ranker.rerank(request)
        
        
        # Results are returned sorted by highest semantic score first
        reranked_docs = []
        for res in results[:top_k]:
            original_idx=res["id"]
            reranked_docs.append(documents[original_idx])  #reranked docs contain dict of all page source score

       
        top_score = results[0]['score'] if results else 'N/A'  ##this is the cross encoder score by flashranker
       
        
        return reranked_docs

    except Exception as e:
        
        # Fallback to the original Qdrant order to ensure the user still gets an answer
        return documents[:top_k]





    #Sample output->
    # reranked_results = [
    # {
    #     "text": "Flash Attention speeds up training loops by 3x by making attention algorithms IO-aware, optimizing data movements between GPU SRAM and HBM.",
    #     "source": "flash_attention_v1.pdf",
    #     "page": 1,
    #     "vector_score": 0.89,
    #     "score": 0.9852  # The top-ranked Cross-Encoder semantic match
    # },
    # {
    #     "text": "Standard attention scales quadratically O(N^2) with sequence length, causing severe GPU hardware memory bottlenecks during long-context training.",
    #     "source": "attention_is_all_you_need.pdf",
    #     "page": 4,
    #     "vector_score": 0.92,   Notice: This had a higher Qdrant score, but FlashRank pushed it down to 2nd place!
    #     "score": 0.8419
    # }]
   